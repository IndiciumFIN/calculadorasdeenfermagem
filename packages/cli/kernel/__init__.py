"""Kernel — executor determinístico de políticas normativo.
Sem política registrada → rejeitado (exit 2).
"""
__version__ = "1.0.0"

from packages.cli.kernel.core import Kernel
from packages.cli.kernel.policy_registry import PolicyRegistry, get_policy, list_policies

__all__ = ["Kernel", "PolicyRegistry", "get_policy", "list_policies"]
