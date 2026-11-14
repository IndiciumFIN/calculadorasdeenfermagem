"""Kernel — executor determinístico de políticas normativo.
Sem política registrada → rejeitado (exit 2).
"""
__version__ = "1.0.0"

from .core import Kernel
from .policy_registry import PolicyRegistry, get_policy, list_policies

__all__ = ["Kernel", "PolicyRegistry", "get_policy", "list_policies"]
