from packages.schemas.invariantes import AtomoBlindado

def gerar_dicionario() -> str:
    schema = AtomoBlindado.model_json_schema()
    lines = [
        "# Dicionário de Dados Vivo (gerado do código)",
        "",
        "Gerado automaticamente a partir de `packages/schemas/invariantes.py`.",
        "",
        "| Campo | Tipo | Obrigatório | Descrição |",
        "|---|---|---|---|"
    ]
    required = set(schema.get("required", []))
    props = schema.get("properties", {})
    for name, prop in props.items():
        tipo = prop.get("type", "string")
        desc = prop.get("description", "")
        obrig = "Sim" if name in required else "Não"
        lines.append(f"| `{name}` | {tipo} | {obrig} | {desc} |")
    return "\n".join(lines)

if __name__ == "__main__":
    print(gerar_dicionario())
