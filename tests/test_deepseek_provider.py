"""
Testes do provider deepseek:deepseek-chat via gateway Supabase (cko-deepseek-gateway).

O gateway real guarda a chave do DeepSeek como secret no Supabase. Aqui o
gateway é simulado por um servidor HTTP local para provar, sem rede externa:
- fail-closed quando falta credencial (exit 2);
- fail-closed quando o gateway responde erro (503 deepseek_secret_missing);
- caminho feliz com temperatura 0 enviada e manifesto correto;
- proibição de gateway sem TLS fora do modo de teste.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WO_DEEPSEEK = "contracts/work_orders/WO-DEEPSEEK-EXEMPLO-001.json"


def run_cli(args, cwd, extra_env=None, drop_env=()):
    env = {k: v for k, v in os.environ.items() if k not in drop_env}
    env["PYTHONPATH"] = str(REPO)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-m"] + args,
        cwd=cwd, env=env, capture_output=True, text=True,
    )


def _preparar_workdir(tmp_path):
    for pasta in ["agents", "prompts", "contracts", "config"]:
        shutil.copytree(REPO / pasta, tmp_path / pasta)
    return tmp_path


def _apontar_gateway(cwd: Path, url: str):
    cfg_path = cwd / "config" / "providers.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["providers"]["deepseek_via_supabase"]["gateway_url"] = url
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


class _GatewayFake(BaseHTTPRequestHandler):
    """Simula o contrato da Edge Function cko-deepseek-gateway."""

    modo = "sucesso"
    ultimo_payload = None

    def do_POST(self):
        corpo = self.rfile.read(int(self.headers.get("content-length", 0)))
        type(self).ultimo_payload = json.loads(corpo)
        if type(self).modo == "secret_missing":
            self._responder(503, {"error": "deepseek_secret_missing"})
            return
        resposta = {
            "ok": True,
            "provider": "deepseek",
            "model": type(self).ultimo_payload.get("model"),
            "persistence": "none",
            "result": {
                "id": "req-fake-001",
                "choices": [{"message": {"role": "assistant", "content": "{\"atomos\": []}"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
        }
        self._responder(200, resposta)

    def _responder(self, status, corpo):
        dados = json.dumps(corpo).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, *args):
        pass


def _subir_gateway(modo):
    _GatewayFake.modo = modo
    _GatewayFake.ultimo_payload = None
    servidor = HTTPServer(("127.0.0.1", 0), _GatewayFake)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    return servidor, f"http://127.0.0.1:{servidor.server_address[1]}/functions/v1/cko-deepseek-gateway"


def test_deepseek_sem_credencial_reprova(tmp_path):
    cwd = _preparar_workdir(tmp_path)
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", WO_DEEPSEEK],
        cwd=cwd, drop_env=("CE_SUPABASE_ANON_KEY",),
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "CE_SUPABASE_ANON_KEY" in r.stdout


def test_deepseek_gateway_http_fora_do_teste_reprova(tmp_path):
    cwd = _preparar_workdir(tmp_path)
    _apontar_gateway(cwd, "http://127.0.0.1:9/functions/v1/cko-deepseek-gateway")
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", WO_DEEPSEEK],
        cwd=cwd, extra_env={"CE_SUPABASE_ANON_KEY": "token-de-teste"},
        drop_env=("CE_ALLOW_TEST_GATEWAY",),
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "TLS" in r.stdout


def test_deepseek_secret_ausente_no_supabase_reprova(tmp_path):
    cwd = _preparar_workdir(tmp_path)
    servidor, url = _subir_gateway("secret_missing")
    try:
        _apontar_gateway(cwd, url)
        r = run_cli(
            ["packages.cli.llm_runner", "run", "--work-order", WO_DEEPSEEK],
            cwd=cwd,
            extra_env={"CE_SUPABASE_ANON_KEY": "token-de-teste", "CE_ALLOW_TEST_GATEWAY": "1"},
        )
    finally:
        servidor.shutdown()
    assert r.returncode == 2, r.stdout + r.stderr
    assert "deepseek_secret_missing" in r.stdout


def test_deepseek_sucesso_envia_temperatura_zero_e_gera_manifesto(tmp_path):
    cwd = _preparar_workdir(tmp_path)
    servidor, url = _subir_gateway("sucesso")
    try:
        _apontar_gateway(cwd, url)
        r = run_cli(
            ["packages.cli.llm_runner", "run", "--work-order", WO_DEEPSEEK],
            cwd=cwd,
            extra_env={"CE_SUPABASE_ANON_KEY": "token-de-teste", "CE_ALLOW_TEST_GATEWAY": "1"},
        )
    finally:
        servidor.shutdown()
    assert r.returncode == 0, r.stdout + r.stderr

    payload = _GatewayFake.ultimo_payload
    assert payload["temperature"] == 0, "temperatura enviada ao gateway deve ser 0"
    assert payload["model"] == "deepseek-chat"
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"

    out_dir = cwd / "data" / "raw_llm" / "WO-DEEPSEEK-EXEMPLO-001"
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["provider"] == "deepseek_via_supabase"
    assert manifest["estagio"] == "raw"
    assert manifest["promotable"] is True
    assert manifest["provider_meta"]["modelo_retornado"] == "deepseek-chat"
    assert (out_dir / "output.json").read_text(encoding="utf-8") == "{\"atomos\": []}"


def test_deepseek_modelo_nao_pinado_reprova(tmp_path):
    cwd = _preparar_workdir(tmp_path)
    wo_path = cwd / WO_DEEPSEEK
    wo = json.loads(wo_path.read_text(encoding="utf-8"))
    wo["model_id"] = "deepseek:deepseek-reasoner"
    wo_path.write_text(json.dumps(wo, ensure_ascii=False, indent=2), encoding="utf-8")
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", str(wo_path)],
        cwd=cwd, extra_env={"CE_SUPABASE_ANON_KEY": "token-de-teste"},
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "allowlist" in r.stdout
