from ..templates import Layer
from ..core import DeeplayModule
from ..config import Config, Ref

import torch.nn as nn


class MultiLayerPerceptron(DeeplayModule):
    """Multi-layer perceptron module.

    Also commonly known as a fully-connected neural network, or a dense neural network.

    Configurables
    -------------
    - blocks (template-like): Specification for the blocks of the MLP. (Default: "layer" >> "activation")
        - layer (template-like): Specification for the layer of the block. (Default: nn.LazyLinear)
        - activation (template-like): Specification for the activation of the block. (Default: nn.ReLU)

    Constraints
    -----------
    - input shape: (batch_size, ch_in)
    - output shape: (batch_size, ch_out)
    - depth >= 1

    Evaluation
    ----------
    >>> for block in mlp.blocks:
    >>>    x = block(x)
    >>> return x

    Examples
    --------
    >>> # Using default values
    >>> mlp = MultiLayerPerceptron()
    >>> # Customizing depth and activation
    >>> mlp = MultiLayerPerceptron(depth=4, blocks=Config().activation(nn.Sigmoid))
    >>> # Using from_config with custom normalization
    >>> mlp = MultiLayerPerceptron.from_config(
    >>>     Config()
    >>>     .blocks(Layer("layer") >> Layer("activation") >> Layer("normalization"))
    >>>     .blocks.normalization(nn.LazyBatchNorm1d)
    >>> )

    Return Values
    -------------
    The forward method returns the processed tensor.

    Additional Notes
    ----------------
    The `Config` and `Layer` classes are used for configuring the blocks of the MLP. For more details refer to [Config Documentation](#) and [Layer Documentation](#).

    """

    @staticmethod
    def defaults():
        return (
            Config()
            .in_features(None)
            .depth(Ref("hidden_dims", lambda s: len(s) + 1))
            .blocks(
                Layer("layer")
                >> Layer("normalization")
                >> Layer("activation")
                >> Layer("dropout")
            )
            .blocks.layer(nn.Linear)
            .blocks.activation(nn.ReLU)
            .blocks.normalization(nn.Identity)
            .blocks.dropout(nn.Identity)
            .out_layer(nn.Linear)
            .out_layer.in_features(Ref("hidden_dims", lambda s: s[-1]))
            .out_layer.out_features(Ref("out_features"))
            .out_activation(nn.Identity)
            # If in_features is not specified, we do lazy initialization
        )

    def __init__(
        self,
        in_features: int or None,
        hidden_dims: list[int],
        out_features: int,
        out_activation=None,
        blocks=None,
    ):
        super().__init__(
            in_features=in_features,
            hidden_dims=hidden_dims,
            out_features=out_features,
            out_activation=out_activation,
            blocks=blocks,
        )

        self.in_features = self.attr("in_features")
        self.hidden_dims = self.attr("hidden_dims")
        self.out_features = self.attr("out_features")

        blocks = nn.ModuleList()
        for i, out_features in enumerate(self.hidden_dims):
            in_features = self.in_features if i == 0 else self.hidden_dims[i - 1]

            if in_features is None:
                kwargs = {
                    "layer": nn.LazyLinear,
                    "layer.out_features": out_features,
                }
            else:
                kwargs = {
                    "layer.in_features": in_features,
                    "layer.out_features": out_features,
                }

            block = self.new(
                "blocks",
                i,
                extra_kwargs=kwargs,
                now=True,
            )
            blocks.append(block)

        self.blocks = blocks

        # Underscored to represent that it is not a configurable attribute
        self.out_layer = self.new("out_layer")

        self.out_activation = self.new("out_activation")

    def forward(self, x):
        x = nn.Flatten()(x)
        for block in self.blocks:
            x = block(x)
        x = self.out_layer(x)
        x = self.out_activation(x)
        return x


class MLPTiny(MultiLayerPerceptron):
    @staticmethod
    def defaults():
        # 97% accuracy on MNIST
        return (
            MultiLayerPerceptron.defaults()
            .hidden_dims([16, 256])
            .blocks[0]
            .normalization(nn.LazyBatchNorm1d, num_features=16)
            .blocks[1]
            .normalization(nn.LazyBatchNorm1d, num_features=256)
            .blocks.activation(nn.LeakyReLU, negative_slope=0.1)
        )


class MLPSmall(MultiLayerPerceptron):
    # 98.1% accuracy on MNIST
    @staticmethod
    def defaults():
        return (
            MultiLayerPerceptron.defaults()
            .hidden_dims([100, 200])
            .blocks.activation(nn.GELU)
            .blocks[0]
            .normalization(nn.LazyBatchNorm1d, num_features=100)
        )


class MLPMedium(MultiLayerPerceptron):
    @staticmethod
    def defaults():
        return (
            MultiLayerPerceptron.defaults()
            .hidden_dims([500, 700, 200])
            .blocks.normalization(nn.LazyBatchNorm1d)
            .blocks.activation(nn.GELU)
        )


class MLPLarge(MultiLayerPerceptron):
    @staticmethod
    def defaults():
        return (
            MultiLayerPerceptron.defaults()
            .hidden_dims([2500, 2000, 1500, 1000, 500])
            .blocks.normalization(nn.LazyBatchNorm1d)
        )


class MLPMassive(MultiLayerPerceptron):
    @staticmethod
    def defaults():
        return (
            MultiLayerPerceptron.defaults()
            .hidden_dims([512, 1024, 1024, 1024, 1024, 1024])
            .blocks.normalization(nn.LazyBatchNorm1d)
        )
