import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// Gateway governado do DeepSeek (porta única de saída para api.deepseek.com).
// Versão 3, implantada em 15/10/2026. Fonte espelhada aqui para rastreabilidade;
// o deploy é feito no projeto Supabase aevqrmkdhffmursdtcmo.
//
// Aceita os dois nomes de secret: DEEPSEEK_API_KEY (canônico) e DeepseekAPI
// (nome usado no cadastro manual do dashboard em 14/10/2026).
const DEEPSEEK_API_KEY = Deno.env.get("DEEPSEEK_API_KEY") ?? Deno.env.get("DeepseekAPI");
const DEFAULT_MODEL = Deno.env.get("DEEPSEEK_MODEL") || "deepseek-chat";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });

Deno.serve(async (req: Request) => {
  if (req.method === "GET") {
    return json({
      ok: true,
      service: "cko-deepseek-gateway",
      persistence: "none",
      deepseek_configured: Boolean(DEEPSEEK_API_KEY),
      model: DEFAULT_MODEL,
    });
  }

  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);
  if (!DEEPSEEK_API_KEY) return json({ error: "deepseek_secret_missing" }, 503);

  try {
    const body = await req.json();
    const messages = Array.isArray(body?.messages) ? body.messages : null;
    if (!messages?.length) return json({ error: "messages_required" }, 400);

    const model = typeof body?.model === "string" && body.model.trim()
      ? body.model.trim()
      : DEFAULT_MODEL;

    const payload: Record<string, unknown> = {
      model,
      messages,
      temperature: typeof body?.temperature === "number" ? body.temperature : 0.1,
    };

    if (body?.response_format) payload.response_format = body.response_format;
    if (typeof body?.max_tokens === "number") payload.max_tokens = body.max_tokens;

    const upstream = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "authorization": `Bearer ${DEEPSEEK_API_KEY}`,
      },
      body: JSON.stringify(payload),
    });

    const result = await upstream.json().catch(() => ({ error: "invalid_upstream_json" }));
    if (!upstream.ok) {
      return json({
        error: "deepseek_upstream_error",
        status: upstream.status,
        details: result,
      }, 502);
    }

    return json({
      ok: true,
      provider: "deepseek",
      model,
      persistence: "none",
      result,
    });
  } catch (error) {
    return json({
      error: "gateway_error",
      message: error instanceof Error ? error.message : String(error),
    }, 500);
  }
});
