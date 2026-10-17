"""Base validator — interface que todo validador deve implementar."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseValidator(ABC):
    """Interface que todo validador deve implementar.

    Cada validador deve:
    1. Implementar validate() — retorna (is_valid, error_message)
    2. Implementar validate_batch() — retorna lista de resultados
    3. Implementar test_suite() — retorna >= 10 casos (5 válidos, 5 inválidos)
    4. Implementar run_tests() — executa test_suite(), fail-closed se falhar
    5. Ter @property name → nome do validador
    6. Ter @property version → versão do validador (hash do código ou semver)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do validador (usado no report e na política)."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Versão do validador."""
        ...

    @abstractmethod
    def validate(self, item: dict[str, Any]) -> tuple[bool, str | None]:
        """Valida um item. Returns: (is_valid, error_message)."""
        ...

    @abstractmethod
    def validate_batch(
        self, items: list[dict[str, Any]]
    ) -> list[tuple[dict[str, Any], bool, str | None]]:
        """Valida lote. Returns: [(item, is_valid, error_message), ...]"""
        ...

    @abstractmethod
    def test_suite(self) -> list[tuple[dict[str, Any], bool, str]]:
        """Casos de teste: [(input, expected_valid, description), ...].

        Mínimo 10 casos: 5 válidos, 5 inválidos.
        """
        ...

    def run_tests(self) -> bool:
        """Executa test_suite(). Fail-closed — retorna False se qualquer teste falhar."""
        import sys
        suite = self.test_suite()
        if len(suite) < 10:
            print(f"FAIL: {self.name} tem apenas {len(suite)} casos de teste (mínimo: 10)")
            return False

        valid_count = sum(1 for _, expected, _ in suite if expected)
        invalid_count = len(suite) - valid_count

        if valid_count < 5 or invalid_count < 5:
            print(f"FAIL: {self.name} precisa de 5 válidos e 5 inválidos (tem {valid_count}/{invalid_count})")
            return False

        failures = []
        for i, (item, expected_valid, description) in enumerate(suite):
            try:
                actual_valid, error = self.validate(item)
            except Exception as exc:
                failures.append(f"  Caso {i+1} '{description}': exceção {exc}")
                continue

            if actual_valid != expected_valid:
                failures.append(
                    f"  Caso {i+1} '{description}': "
                    f"expected={expected_valid}, got={actual_valid} "
                    f"(error={error})"
                )

        if failures:
            print(f"FAIL: {self.name} — {len(failures)}/{len(suite)} testes falharam:")
            for f in failures:
                print(f)
            return False

        print(f"OK: {self.name}@{self.version} — {len(suite)}/{len(suite)} testes aprovados")
        return True
