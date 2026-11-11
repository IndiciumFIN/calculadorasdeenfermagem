"""Kernel — executor determinístico de políticas normativo.
Sem política registrada → rejeitado (exit 2).

Os imports pesados são preguiçosos para que `policy_registry` carregue
sem exigir o pacote top-level `kernel` (uso: python -m packages.cli.main).
"""
__version__ = "1.0.0"

__all__ = ["Kernel", "PolicyRegistry", "get_policy", "list_policies"]


def __getattr__(name: str):
    if name == "Kernel":
        try:
            from packages.cli.kernel.core import Kernel
        except ImportError:
            from kernel.core import Kernel
        return Kernel
    if name in {"PolicyRegistry", "get_policy", "list_policies"}:
        try:
            from packages.cli.kernel import policy_registry as registry
        except ImportError:
            from kernel import policy_registry as registry
        return getattr(registry, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
