"""Kernel — executor determinístico de políticas normativas.

Sem política registrada → rejeitado (exit 2).
Os imports pesados ficam preguiçosos para permitir `python -m` de atividades
que só leem o registry JSON, sem o namespace top-level `kernel`.
"""
__version__ = "1.0.0"

__all__ = ["Kernel", "PolicyRegistry", "get_policy", "list_policies"]


def __getattr__(name):
    if name == "Kernel":
        from kernel.core import Kernel
        return Kernel
    if name in {"PolicyRegistry", "get_policy", "list_policies"}:
        from kernel.policy_registry import PolicyRegistry, get_policy, list_policies
        return {
            "PolicyRegistry": PolicyRegistry,
            "get_policy": get_policy,
            "list_policies": list_policies,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
