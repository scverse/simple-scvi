from __future__ import annotations

import numpy as np
import numpy.typing as npt
import torch
import torch.nn.functional as F
from scvi import REGISTRY_KEYS
from scvi.distributions import ZeroInflatedNegativeBinomial
from scvi.module._constants import MODULE_KEYS
from scvi.module.base import BaseModuleClass, LossOutput, auto_move_data
from scvi.nn import DecoderSCVI, Encoder, one_hot
from torch import Tensor
from torch.distributions import Normal
from torch.distributions import kl_divergence as kl


class MyModule(BaseModuleClass):
    """Skeleton variational auto-encoder (VAE) model.

    Here we implement a basic version of scVI's underlying VAE :cite:p:`Lopez18`. This
    implementation is for instructional purposes only.

    Parameters
    ----------
    n_input
        Number of input genes.
    library_log_means
        1 x n_batch array of means of the log library sizes. Parameterizes prior on library size if
        not using observed library size.
    library_log_vars
        1 x n_batch array of variances of the log library sizes. Parameterizes prior on library
        size if not using observed library size.
    n_batch
        Number of batches, if 0, no batch correction is performed.
    n_hidden
        Number of nodes per hidden layer.
    n_latent
        Dimensionality of the latent space.
    n_layers
        Number of hidden layers used for encoder and decoder NNs.
    dropout_rate
        Dropout rate for neural networks.
    """

    def __init__(
        self,
        n_input: int,
        library_log_means: npt.NDArray,
        library_log_vars: npt.NDArray,
        n_batch: int = 0,
        n_hidden: int = 128,
        n_latent: int = 10,
        n_layers: int = 1,
        dropout_rate: float = 0.1,
    ):
        super().__init__()
        self.n_latent = n_latent
        self.n_batch = n_batch
        # this is needed to comply with some requirement of the VAEMixin class
        self.latent_distribution = "normal"

        self.register_buffer("library_log_means", torch.from_numpy(library_log_means).float())
        self.register_buffer("library_log_vars", torch.from_numpy(library_log_vars).float())

        # setup the parameters of your generative model, as well as your inference model
        self.px_r = torch.nn.Parameter(torch.randn(n_input))
        # z encoder goes from the n_input-dimensional data to an n_latent-d
        # latent space representation
        self.z_encoder = Encoder(
            n_input,
            n_latent,
            n_layers=n_layers,
            n_hidden=n_hidden,
            dropout_rate=dropout_rate,
        )
        # l encoder goes from n_input-dimensional data to 1-d library size
        self.l_encoder = Encoder(
            n_input,
            1,
            n_layers=1,
            n_hidden=n_hidden,
            dropout_rate=dropout_rate,
        )
        # decoder goes from n_latent-dimensional space to n_input-d data
        self.decoder = DecoderSCVI(
            n_latent,
            n_input,
            n_layers=n_layers,
            n_hidden=n_hidden,
        )

    def _get_inference_input(self, tensors: dict[str, Tensor]) -> dict[str, Tensor]:
        """Parse the dictionary to get appropriate args."""
        return {MODULE_KEYS.X_KEY: tensors[REGISTRY_KEYS.X_KEY]}

    def _get_generative_input(
        self,
        tensors: dict[str, Tensor],
        inference_outputs: dict[str, Tensor],
    ) -> dict[str, Tensor]:
        return {
            MODULE_KEYS.Z_KEY: inference_outputs["z"],
            MODULE_KEYS.LIBRARY_KEY: inference_outputs["library"],
        }

    @auto_move_data
    def inference(self, x: Tensor) -> dict[str, Tensor]:
        """
        High level inference method.

        Runs the inference (encoder) model.
        """
        # log the input to the variational distribution for numerical stability
        x_ = torch.log1p(x)
        # get variational parameters via the encoder networks
        qz_m, qz_v, z = self.z_encoder(x_)
        ql_m, ql_v, library = self.l_encoder(x_)

        return {
            MODULE_KEYS.Z_KEY: z,
            MODULE_KEYS.QZM_KEY: qz_m,
            MODULE_KEYS.QZV_KEY: qz_v,
            "ql_m": ql_m,
            "ql_v": ql_v,
            MODULE_KEYS.LIBRARY_KEY: library,
        }

    @auto_move_data
    def generative(self, z: Tensor, library: Tensor) -> dict[str, Tensor]:
        """Runs the generative model."""
        # form the parameters of the ZINB likelihood
        px_scale, _, px_rate, px_dropout = self.decoder("gene", z, library)
        px_r = torch.exp(self.px_r)

        return {
            "px_scale": px_scale,
            "px_r": px_r,
            "px_rate": px_rate,
            "px_dropout": px_dropout,
        }

    def loss(
        self,
        tensors: dict[str, Tensor],
        inference_outputs: dict[str, Tensor],
        generative_outputs: dict[str, Tensor],
        kl_weight: float = 1.0,
    ) -> LossOutput:
        """Loss function."""
        x = tensors[REGISTRY_KEYS.X_KEY]
        batch_index = tensors[REGISTRY_KEYS.BATCH_KEY]
        qz_m = inference_outputs[MODULE_KEYS.QZM_KEY]
        qz_v = inference_outputs[MODULE_KEYS.QZV_KEY]
        ql_m = inference_outputs["ql_m"]
        ql_v = inference_outputs["ql_v"]
        px_rate = generative_outputs["px_rate"]
        px_r = generative_outputs["px_r"]
        px_dropout = generative_outputs["px_dropout"]

        mean = torch.zeros_like(qz_m)
        scale = torch.ones_like(qz_v)

        kl_divergence_z = kl(Normal(qz_m, torch.sqrt(qz_v)), Normal(mean, scale)).sum(dim=1)

        n_batch = self.library_log_means.shape[1]
        local_library_log_means = F.linear(one_hot(batch_index, n_batch), self.library_log_means)
        local_library_log_vars = F.linear(one_hot(batch_index, n_batch), self.library_log_vars)

        kl_divergence_l = kl(
            Normal(ql_m, torch.sqrt(ql_v)),
            Normal(local_library_log_means, torch.sqrt(local_library_log_vars)),
        ).sum(dim=1)

        reconst_loss = (
            -ZeroInflatedNegativeBinomial(mu=px_rate, theta=px_r, zi_logits=px_dropout)
            .log_prob(x)
            .sum(dim=-1)
        )

        kl_local_for_warmup = kl_divergence_z
        kl_local_no_warmup = kl_divergence_l

        weighted_kl_local = kl_weight * kl_local_for_warmup + kl_local_no_warmup

        loss = torch.mean(reconst_loss + weighted_kl_local)

        kl_local = {
            MODULE_KEYS.KL_L_KEY: kl_divergence_l,
            MODULE_KEYS.KL_Z_KEY: kl_divergence_z,
        }
        return LossOutput(loss=loss, reconstruction_loss=reconst_loss, kl_local=kl_local)

    @torch.no_grad()
    def sample(
        self,
        tensors: dict[str, Tensor],
        n_samples: int = 1,
        library_size: int = 1,
    ) -> Tensor:
        r"""Generate observation samples from the posterior predictive distribution.

        The posterior predictive distribution is written as :math:`p(\hat{x} \mid x)`.

        Parameters
        ----------
        tensors
            Tensors dict
        n_samples
            Number of required samples for each cell
        library_size
            Library size to scale scamples to

        Returns
        -------
        x_new
            tensor with shape (n_cells, n_genes, n_samples)
        """
        inference_kwargs = {"n_samples": n_samples}
        (
            _,
            generative_outputs,
        ) = self.forward(
            tensors,
            inference_kwargs=inference_kwargs,
            compute_loss=False,
        )

        px_r = generative_outputs["px_r"]
        px_rate = generative_outputs["px_rate"]
        px_dropout = generative_outputs["px_dropout"]

        dist = ZeroInflatedNegativeBinomial(mu=px_rate, theta=px_r, zi_logits=px_dropout)

        if n_samples > 1:
            exprs = dist.sample().permute([1, 2, 0])  # Shape : (n_cells_batch, n_genes, n_samples)
        else:
            exprs = dist.sample()

        return exprs.cpu()

    @torch.no_grad()
    @auto_move_data
    def marginal_ll(self, tensors: dict[str, Tensor], n_mc_samples: int) -> float:
        """Marginal ll."""
        sample_batch = tensors[REGISTRY_KEYS.X_KEY]
        batch_index = tensors[REGISTRY_KEYS.BATCH_KEY]

        to_sum = torch.zeros(sample_batch.size()[0], n_mc_samples)

        for i in range(n_mc_samples):
            # Distribution parameters and sampled variables
            inference_outputs, _, losses = self.forward(tensors)
            qz_m = inference_outputs[MODULE_KEYS.QZM_KEY]
            qz_v = inference_outputs[MODULE_KEYS.QZV_KEY]
            z = inference_outputs[MODULE_KEYS.Z_KEY]
            ql_m = inference_outputs["ql_m"]
            ql_v = inference_outputs["ql_v"]
            library = inference_outputs[MODULE_KEYS.LIBRARY_KEY]

            # Reconstruction Loss
            reconst_loss = losses.dict_sum(losses.reconstruction_loss)

            # Log-probabilities
            n_batch = self.library_log_means.shape[1]
            local_library_log_means = F.linear(
                one_hot(batch_index, n_batch), self.library_log_means
            )
            local_library_log_vars = F.linear(one_hot(batch_index, n_batch), self.library_log_vars)
            p_l = (
                Normal(local_library_log_means, local_library_log_vars.sqrt())
                .log_prob(library)
                .sum(dim=-1)
            )

            p_z = Normal(torch.zeros_like(qz_m), torch.ones_like(qz_v)).log_prob(z).sum(dim=-1)
            p_x_zl = -reconst_loss
            q_z_x = Normal(qz_m, qz_v.sqrt()).log_prob(z).sum(dim=-1)
            q_l_x = Normal(ql_m, ql_v.sqrt()).log_prob(library).sum(dim=-1)

            to_sum[:, i] = p_z + p_l + p_x_zl - q_z_x - q_l_x

        batch_log_lkl = torch.logsumexp(to_sum, dim=-1) - np.log(n_mc_samples)
        log_lkl = torch.sum(batch_log_lkl).item()
        return log_lkl
