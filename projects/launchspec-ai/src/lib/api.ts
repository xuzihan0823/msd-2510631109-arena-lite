import { AIProviderError } from "./ai-provider";
import { ValidationError } from "./validation";

export async function readJsonBody(request: Request): Promise<unknown> {
  try {
    return await request.json();
  } catch {
    throw new ValidationError("请求体必须是有效 JSON");
  }
}

export function readField(payload: unknown, field: string): unknown {
  if (typeof payload !== "object" || payload === null || Array.isArray(payload)) {
    throw new ValidationError("请求体必须是 JSON 对象");
  }

  return (payload as Record<string, unknown>)[field];
}

export function errorResponse(error: unknown): Response {
  if (error instanceof ValidationError) {
    return Response.json({ error: error.message }, { status: 400 });
  }

  if (error instanceof AIProviderError) {
    return Response.json({ error: error.message }, { status: error.status });
  }

  return Response.json({ error: "服务器暂时无法处理请求，请稍后重试。" }, { status: 500 });
}
