"""Registry de políticas do Kernel — versionado em Git.

Cada política é um arquivo JSON em contracts/policies/.
Sem arquivo de política → Kernel recusa.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

POLICIES_DIR = Path(__file__).parent.parent.parent.parent / "contracts" / "policies"


@dataclass
class KernelPolicy:
    """Política registrada no Kernel."""
    id: str
    name: str
    description: str
    source_contract: str
    validators: list[str] = field(default_factory=list)
    atoms_output: str = ""
    cuarentena_output: str = ""
    sha256_required: bool = True
    fail_closed: bool = True
    requires_human_review: bool = True
    wo_required: bool = True
    wo_template: str = ""
    version: str = "1.0.0"
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KernelPolicy":
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known_fields})


class PolicyRegistry:
    """Registry de políticas — carrega de contracts/policies/."""

    def __init__(self) -> None:
        self._policies: dict[str, KernelPolicy] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not POLICIES_DIR.exists():
            return
        for pfile in sorted(POLICIES_DIR.glob("*.json")):
            try:
                with pfile.open() as f:
                    data = json.load(f)
                policy = KernelPolicy.from_dict(data)
                self._policies[policy.id] = policy
            except (json.JSONDecodeError, TypeError, FileNotFoundError):
                pass

    def register(self, policy: KernelPolicy) -> None:
        """Registra ou atualiza uma política."""
        self._policies[policy.id] = policy

    def get(self, policy_id: str) -> KernelPolicy:
        """Retorna política por ID."""
        if policy_id not in self._policies:
            raise KeyError(f"Política '{policy_id}' não encontrada no registry.")
        return self._policies[policy_id]

    def list_policies(self) -> list[KernelPolicy]:
        """Lista todas as políticas."""
        return sorted(self._policies.values(), key=lambda p: p.id)

    def save(self, policy: KernelPolicy) -> Path:
        """Salva política no disco (contracts/policies/{id}.json)."""
        POLICIES_DIR.mkdir(parents=True, exist_ok=True)
        path = POLICIES_DIR / f"{policy.id}.json"
        with path.open("w") as f:
            json.dump(policy.to_dict(), f, ensure_ascii=False, indent=2)
        self.register(policy)
        return path


# Instância global
_registry: PolicyRegistry | None = None

def _get_registry() -> PolicyRegistry:
    global _registry
    if _registry is None:
        _registry = PolicyRegistry()
    return _registry

def get_policy(policy_id: str) -> KernelPolicy:
    """Retorna política por ID."""
    return _get_registry().get(policy_id)

def list_policies() -> list[KernelPolicy]:
    """Lista todas as políticas."""
    return _get_registry().list_policies()

def register_policy(policy: KernelPolicy) -> Path:
    """Registra e salva política."""
    return _get_registry().save(policy)
