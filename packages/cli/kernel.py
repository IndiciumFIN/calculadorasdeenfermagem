"""Porta única das tarefas de acervo. Sem Work Order, a tarefa não corre."""
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
import typer
from bs4 import BeautifulSoup

from packages.cli import finds
from packages.cli.pep import RAIZ, carregar_wo, decidir_atomizacao, politica

app = typer.Typer(help="Kernel de tarefas: obter, atomizar, validar, retirar")
SAIDA = RAIZ / "data" / "legado" / "extracao_bruta"


def _fail(msg: str):
    typer.secho(f"FAIL: {msg}", fg=typer.colors.RED)
    raise typer.Exit(2)


def _wo(caminho: Path, esperado: str):
    try:
        wo = carregar_wo(caminho)
    except Exception as exc:
        _fail(str(exc))
    if wo.task_type != esperado:
        _fail(f"Work Order {wo.id} é {wo.task_type}, a tarefa pedida é {esperado}")
    return wo


def _destino(caminho: str) -> Path:
    dest = (SAIDA / caminho).resolve()
    if not str(dest).startswith(str(SAIDA.resolve())):
        _fail(f"caminho fora da pasta governada: {caminho}")
    return dest


def _sha(arquivo: Path) -> str:
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


def _eh_html(corpo: bytes) -> bool:
    inicio = corpo[:200].lstrip().lower()
    return inicio.startswith(b"<!doctype html") or inicio.startswith(b"<html")


def _confirmacao_drive(corpo: bytes, file_id: str) -> str | None:
    """Confirma o aviso do Drive só quando o formulário é deste id."""
    form = BeautifulSoup(corpo, "html.parser").find("form", id="download-form")
    if form is None or form.get("action") != "https://drive.usercontent.google.com/download":
        return None
    campos = {
        inp.get("name"): inp.get("value") or ""
        for inp in form.find_all("input")
        if inp.get("name")
    }
    if (
        campos.get("id") != file_id
        or campos.get("export") != "download"
        or campos.get("confirm") != "t"
        or not campos.get("uuid")
    ):
        return None
    return "https://drive.usercontent.google.com/download?" + urlencode(
        {chave: campos[chave] for chave in ("id", "export", "confirm", "uuid")}
    )


TENTATIVAS_DOWNLOAD = 3
ESPERA_DOWNLOAD = 2


def _get(url: str, file_id: str):
    """Repete só resposta 5xx. Quatrocentos e o terceiro erro fecham."""
    ultimo = None
    for tentativa in range(TENTATIVAS_DOWNLOAD):
        try:
            resposta = requests.get(url, allow_redirects=True, timeout=600)
        except requests.RequestException as exc:
            ultimo = exc
            if tentativa + 1 == TENTATIVAS_DOWNLOAD:
                _fail(f"download {file_id} falhou: {exc}")
            time.sleep(ESPERA_DOWNLOAD)
            continue
        if resposta.status_code < 500:
            return resposta
        ultimo = resposta.status_code
        if tentativa + 1 == TENTATIVAS_DOWNLOAD:
            break
        time.sleep(ESPERA_DOWNLOAD)
    _fail(f"download {file_id} respondeu {ultimo}")


def _corpo(resposta, file_id: str) -> bytes:
    if resposta.status_code != 200:
        _fail(f"download {file_id} respondeu {resposta.status_code}")
    return resposta.content


def _nome_anexo(resposta) -> str | None:
    headers = getattr(resposta, "headers", None) or {}
    disp = headers.get("content-disposition") or ""
    if "filename=" not in disp:
        return None
    bruto = disp.split("filename=", 1)[1].strip()
    if bruto.startswith('"'):
        return bruto.split('"', 2)[1]
    return bruto.split(";", 1)[0].strip()


def _baixar(file_id: str, dest: Path) -> None:
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resposta = _get(url, file_id)
    corpo = _corpo(resposta, file_id)
    if _eh_html(corpo):
        confirmacao = _confirmacao_drive(corpo, file_id)
        if confirmacao:
            resposta = _get(confirmacao, file_id)
            corpo = _corpo(resposta, file_id)
            if _eh_html(corpo):
                _fail(f"download {file_id} continuou em HTML depois da confirmação")
        elif _nome_anexo(resposta) != dest.name or b"Virus scan warning" in corpo:
            _fail(f"download {file_id} devolveu HTML, não o arquivo")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(corpo)


def _gravar(nome: str, doc: dict) -> Path:
    SAIDA.mkdir(parents=True, exist_ok=True)
    caminho = SAIDA / nome
    caminho.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


@app.callback()
def _callback():
    """Força o modo subcomando."""


@app.command()
def obter(work_order: Path = typer.Option(..., "--work-order")):
    """Baixa cada id da Work Order e grava o SHA-256. Não atomiza."""
    wo = _wo(work_order, "obter")
    itens = []
    for entrada in wo.entradas:
        dest = _destino(entrada.caminho)
        _baixar(entrada.id_origem, dest)
        itens.append(
            {
                "id_origem": entrada.id_origem,
                "caminho": entrada.caminho,
                "classe": entrada.classe,
                "sha256": _sha(dest),
                "bytes": dest.stat().st_size,
            }
        )
    _gravar(
        f"manifesto_obter_{wo.id}.json",
        {"work_order": wo.id, "policy_version": wo.policy_version, "itens": itens},
    )
    typer.secho(f"✓ obter {wo.id}: {len(itens)} arquivos", fg=typer.colors.GREEN)


@app.command()
def atomizar(work_order: Path = typer.Option(..., "--work-order")):
    """Aplica a classe da política. Referência não vira átomo."""
    wo = _wo(work_order, "atomizar")
    doc = politica()
    itens = []
    for entrada in wo.entradas:
        dest = _destino(entrada.caminho)
        if not dest.is_file():
            _fail(f"arquivo ausente: {entrada.caminho}")
        if _sha(dest) != entrada.sha256:
            _fail(f"SHA-256 divergente: {entrada.id_origem}")
        modo = decidir_atomizacao(entrada.classe)
        if modo == "NAO_APLICAVEL":
            itens.append(
                {
                    "id_origem": entrada.id_origem,
                    "caminho": entrada.caminho,
                    "classe": entrada.classe,
                    "sha256": entrada.sha256,
                    "atomos": [],
                    "resultado": "NAO_APLICAVEL",
                    "motivo": doc["classes"][entrada.classe]["motivo"],
                }
            )
            continue
        if modo != "CANDIDATO":
            _fail(f"modo de atomização desconhecido: {modo}")
        _fail(
            f"{entrada.id_origem} é ATO e este lote não tem extrator de dispositivo. "
            "Falha fechada: nenhum átomo foi inventado."
        )
    _gravar(
        f"manifesto_atomizar_{wo.id}.json",
        {"work_order": wo.id, "policy_version": wo.policy_version, "itens": itens},
    )
    typer.secho(f"✓ atomizar {wo.id}: {len(itens)} arquivos, 0 átomos", fg=typer.colors.GREEN)


@app.command()
def validar(work_order: Path = typer.Option(..., "--work-order")):
    """Confere hash, classe e a ausência de átomo Vigente."""
    wo = _wo(work_order, "validar")
    origem = wo.parametros.get("atomizar_work_order")
    if not origem:
        _fail("validar exige parametros.atomizar_work_order")
    atomos = SAIDA / f"manifesto_atomizar_{origem}.json"
    if not atomos.is_file():
        _fail("manifesto_atomizar.json ausente")
    feito = json.loads(atomos.read_text(encoding="utf-8"))
    por_caminho = {item["caminho"]: item for item in feito["itens"]}
    parecer = []
    for entrada in wo.entradas:
        item = por_caminho.get(entrada.caminho)
        dest = _destino(entrada.caminho)
        if item is None or item.get("id_origem") != entrada.id_origem or not dest.is_file():
            _fail(f"sem resultado de atomização: {entrada.id_origem}")
        if _sha(dest) != entrada.sha256 or item["sha256"] != entrada.sha256:
            _fail(f"SHA-256 divergente na validação: {entrada.id_origem}")
        if item["resultado"] != "NAO_APLICAVEL" or item["atomos"]:
            _fail(f"resultado inesperado: {entrada.id_origem}")
        parecer.append(
            {
                "id_origem": entrada.id_origem,
                "caminho": entrada.caminho,
                "sha256": entrada.sha256,
                "resultado": "PASS",
                "atomos": 0,
            }
        )
    _gravar(
        f"parecer_validar_{wo.id}.json",
        {
            "work_order": wo.id,
            "checker_id": wo.checker_id,
            "authorized_by": wo.authorized_by,
            "itens": parecer,
        },
    )
    typer.secho(f"✓ validar {wo.id}: {len(parecer)} PASS", fg=typer.colors.GREEN)


@app.command()
def retirar(work_order: Path = typer.Option(..., "--work-order")):
    """Autoriza a lixeira. Não apaga. Exige parecer PASS e checker diferente."""
    wo = _wo(work_order, "retirar")
    parecer_arq = SAIDA / f"parecer_validar_{wo.parametros.get('parecer_work_order')}.json"
    if not parecer_arq.is_file():
        _fail("parecer_validar.json ausente")
    parecer = json.loads(parecer_arq.read_text(encoding="utf-8"))
    if wo.parametros.get("parecer_work_order") != parecer.get("work_order"):
        _fail("parecer_work_order não confere com o parecer gravado")
    por_caminho = {item["caminho"]: item for item in parecer["itens"] if item.get("caminho")}
    autorizados = []
    for entrada in wo.entradas:
        item = por_caminho.get(entrada.caminho)
        if item is None or item.get("id_origem") != entrada.id_origem or item.get("resultado") != "PASS":
            _fail(f"retirada sem PASS: {entrada.id_origem}")
        if item.get("sha256") != entrada.sha256:
            _fail(f"SHA-256 do parecer divergente: {entrada.id_origem}")
        if _sha(_destino(entrada.caminho)) != entrada.sha256:
            _fail(f"cópia local divergente: {entrada.id_origem}")
        autorizados.append(entrada.id_origem)
    _gravar(
        f"autorizacao_retirada_{wo.id}.json",
        {"work_order": wo.id, "checker_id": wo.checker_id, "ids": autorizados},
    )
    typer.secho(f"✓ retirar {wo.id}: {len(autorizados)} ids autorizados", fg=typer.colors.GREEN)


def _find(work_order: Path, procedimento: str):
    wo = _wo(work_order, procedimento)
    try:
        if procedimento == "registrar-find":
            return wo, finds.registrar(wo.parametros, wo.id, wo.agent_id)
        if procedimento == "vincular-find":
            return wo, finds.vincular(wo.parametros, wo.id)
        if procedimento == "analisar-find":
            return wo, finds.analisar(wo.parametros, wo.id, wo.agent_id)
        if procedimento == "corrigir-find":
            return wo, finds.corrigir(wo.parametros, wo.id, wo.agent_id)
        if procedimento == "encerrar-find":
            return wo, finds.encerrar(wo.parametros, wo.id)
    except Exception as exc:
        _fail(str(exc))
    _fail(f"procedimento de FIND desconhecido: {procedimento}")


def registro_nao_autoriza_correcao(doc: dict, find_id: str) -> bool:
    """O FIND recém-registrado não sai com correção autorizada."""
    alvo = next(item for item in doc["finds"] if item["id"] == find_id)
    return not alvo.get("correcao_autorizada")


@app.command("registrar-find")
def registrar_find(work_order: Path = typer.Option(..., "--work-order")):
    """Registra o achado. Não autoriza correção."""
    wo, doc = _find(work_order, "registrar-find")
    ultimo = doc["eventos"][-1]
    if not registro_nao_autoriza_correcao(doc, ultimo["find_id"]):
        _fail("registro de FIND autorizou correção")
    typer.secho(f"✓ registrar-find {wo.id}: {ultimo['tipo']} {ultimo['find_id']}", fg=typer.colors.GREEN)


@app.command("vincular-find")
def vincular_find(work_order: Path = typer.Option(..., "--work-order")):
    """Liga o FIND a uma execução. Não fecha e não autoriza correção."""
    wo, doc = _find(work_order, "vincular-find")
    typer.secho(f"✓ vincular-find {wo.id}: {doc['eventos'][-1]['find_id']}", fg=typer.colors.GREEN)


@app.command("analisar-find")
def analisar_find(work_order: Path = typer.Option(..., "--work-order")):
    """Outro agente analisa o FIND. Não corrige e não fecha."""
    wo, doc = _find(work_order, "analisar-find")
    typer.secho(f"✓ analisar-find {wo.id}: {doc['eventos'][-1]['find_id']}", fg=typer.colors.GREEN)


@app.command("corrigir-find")
def corrigir_find(work_order: Path = typer.Option(..., "--work-order")):
    """O agente que analisou registra a correção. O FIND continua aberto."""
    wo, doc = _find(work_order, "corrigir-find")
    typer.secho(f"✓ corrigir-find {wo.id}: {doc['eventos'][-1]['find_id']}", fg=typer.colors.GREEN)


@app.command("encerrar-find")
def encerrar_find(work_order: Path = typer.Option(..., "--work-order")):
    """Fecha o FIND com evidência conferida. O histórico permanece."""
    wo, doc = _find(work_order, "encerrar-find")
    typer.secho(f"✓ encerrar-find {wo.id}: {doc['eventos'][-1]['find_id']}", fg=typer.colors.GREEN)


@app.command("auditar-inventario")
def auditar_inventario(work_order: Path = typer.Option(..., "--work-order")):
    """Audita snapshot de metadados pelo Kernel. Jamais elimina nem publica."""
    from packages.cli.inventory import auditar
    wo = _wo(work_order, "auditar-inventario")
    try:
        resultado, destino = auditar(wo, RAIZ)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        _fail(f"WO {wo.id}: {exc}")
    typer.echo(f"✓ {wo.id}: {resultado['arquivos_observados']} itens; "
               f"{resultado['zips_observados']} ZIPs; status {resultado['status']}; "
               f"evidência {destino}")

@app.command("auditar-zip")
def auditar_zip(work_order: Path = typer.Option(..., "--work-order")):
    """Audita ZIP original sob WO. Sem remoção ou extração para disco."""
    from packages.cli.archive_audit import auditar_zip_wo
    wo = _wo(work_order, "auditar-zip")
    try:
        result, evidence = auditar_zip_wo(wo, RAIZ)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        _fail(f"WO {wo.id}: {exc}")
    typer.echo(f"✓ {wo.id}: {result['membros']} membros; status {result['status']}; evidência {evidence}")
    if result["status"] != "ANALISADO":
        raise typer.Exit(2)

@app.command("importar-drive")
def importar_drive(work_order: Path = typer.Option(..., "--work-order")):
    """Importa arquivo autenticado previamente montado, sob WO. Sem remoção."""
    from packages.cli.staging import importar
    wo = _wo(work_order, "importar-drive")
    try:
        report, evidence = importar(wo, RAIZ)
    except (ValueError, OSError) as exc:
        _fail(f"WO {wo.id}: {exc}")
    typer.echo(f"✓ {wo.id}: {report['bytes']} bytes; status {report['status']}; evidência {evidence}")

if __name__ == "__main__":
    app()
