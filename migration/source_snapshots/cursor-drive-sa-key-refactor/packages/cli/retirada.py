"""Invariante FONTE_RETIRADA.

O que está implantado no repositório governado, ou formalmente descartado,
não permanece como origem no Drive nem no Supabase. A exclusão só é
autorizada com SHA-256 idêntico (IMPLANTADO) ou com motivo de descarte
(DESCARTADO). Hash divergente bloqueia: conflito não é duplicata.
"""
import hashlib
import json
from pathlib import Path

import typer
from pydantic import BaseModel, ConfigDict, Field, model_validator

app = typer.Typer(help="Invariante de retirada da origem após implantação ou descarte")

RAIZ = Path(__file__).resolve().parents[2]
SHA = r"^[0-9a-f]{64}$"


class ItemRetirada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origem: str = Field(pattern=r"^(drive|supabase)$")
    id_origem: str = Field(min_length=3)
    disposicao: str = Field(pattern=r"^(IMPLANTADO|DESCARTADO)$")
    sha256: str | None = Field(default=None, pattern=SHA)
    copia: str | None = None
    motivo_descarte: str | None = None
    estado_origem: str = Field(pattern=r"^(AUSENTE|PRESENTE|TOMBSTONE_410)$")

    @model_validator(mode="after")
    def vinculo(self):
        if self.disposicao == "IMPLANTADO":
            if not self.sha256 or not self.copia:
                raise ValueError("IMPLANTADO exige sha256 e copia governada")
        if self.disposicao == "DESCARTADO":
            if not self.motivo_descarte or len(self.motivo_descarte.strip()) < 10:
                raise ValueError("DESCARTADO exige motivo registrado")
        return self


def _fail(msg: str):
    typer.secho(f"FAIL: {msg}", fg=typer.colors.RED)
    raise typer.Exit(2)


def decidir(item: ItemRetirada) -> str:
    """RETIRAR ou BLOQUEAR. Não apaga nada; só aplica a invariante."""
    if item.disposicao == "IMPLANTADO":
        if item.estado_origem != "AUSENTE":
            return "BLOQUEAR"
        return "RETIRAR"
    if item.estado_origem == "PRESENTE":
        return "BLOQUEAR"
    return "RETIRAR"


def hashes_conferem(item: ItemRetirada, raiz: Path) -> bool:
    if item.disposicao != "IMPLANTADO":
        return True
    arquivo = raiz / item.copia
    if not arquivo.is_file():
        return False
    digest = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    if digest == item.sha256:
        return True
    if arquivo.name != "manifesto.json":
        return False
    from packages.cli.fracionar import recomposto_confere

    return recomposto_confere(arquivo, item.sha256)


def verificar_ledger(ledger: dict, raiz: Path) -> list[str]:
    erros: list[str] = []
    politica = json.loads((RAIZ / "policies" / "retirada_fonte.json").read_text(encoding="utf-8"))
    if ledger.get("invariante") != politica["invariante"]:
        erros.append("ledger não declara FONTE_RETIRADA")
    vistos: set[str] = set()
    for bruto in ledger.get("itens") or []:
        try:
            item = ItemRetirada.model_validate(bruto)
        except Exception as exc:
            erros.append(f"item inválido: {exc}")
            continue
        chave = f"{item.origem}:{item.id_origem}"
        if chave in vistos:
            erros.append(f"origem repetida: {chave}")
        vistos.add(chave)
        if decidir(item) != "RETIRAR":
            erros.append(f"{chave} ainda presente; retirada não concluída")
        if not hashes_conferem(item, raiz):
            erros.append(f"{chave} SHA-256 da cópia não confere")
    for bruto in ledger.get("pendentes") or []:
        try:
            item = ItemRetirada.model_validate(bruto)
        except Exception as exc:
            erros.append(f"pendência inválida: {exc}")
            continue
        if decidir(item) == "RETIRAR" and item.estado_origem == "AUSENTE":
            erros.append(f"{item.id_origem} está ausente e não pode continuar pendente")
    return erros


@app.callback()
def _callback():
    """Força o modo subcomando."""


@app.command()
def verificar(
    ledger: Path = typer.Option(Path("data/legado/retirada_fontes.json"), "--ledger"),
    raiz: Path = typer.Option(RAIZ, "--raiz"),
):
    """Confere a invariante contra as cópias locais. Exit 2 se a retirada foi alegada sem hash."""
    if not ledger.is_file():
        _fail(f"ledger ausente: {ledger}")
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    erros = verificar_ledger(doc, raiz)
    if erros:
        for erro in erros:
            typer.secho(f"FAIL: {erro}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho(
        f"✓ FONTE_RETIRADA: {len(doc.get('itens') or [])} origens retiradas, "
        f"{len(doc.get('pendentes') or [])} pendentes",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    app()
