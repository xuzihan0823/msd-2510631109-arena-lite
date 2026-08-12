import { readFile } from "node:fs/promises";

import { createDemoBlueprint } from "./blueprint";
import { reviewBlueprint } from "./review";
import type {
  Blueprint,
  NewProjectInput,
  ReviewFinding,
  ReviewReport,
} from "./types";
import { validateBlueprint } from "./validation";

export type ProviderSource = "demo" | "openai-compatible" | "anthropic-compatible";

export interface GeneratedBlueprint {
  blueprint: Blueprint;
  source: ProviderSource;
}

export class AIProviderError extends Error {
  constructor(message: string, public readonly status = 503) {
    super(message);
    this.name = "AIProviderError";
  }
}

type JsonRecord = Record<string, unknown>;

function asRecord(value: unknown): JsonRecord | undefined {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    return value as JsonRecord;
  }
  return undefined;
}

function providerName(): ProviderSource {
  const configured = process.env.AI_PROVIDER ?? "demo";
  if (
    configured === "demo" ||
    configured === "openai-compatible" ||
    configured === "anthropic-compatible"
  ) {
    return configured;
  }
  throw new AIProviderError(
    "AI_PROVIDER 仅支持 demo、openai-compatible 或 anthropic-compatible",
    500,
  );
}

interface ClaudeProviderSettings {
  baseUrl: string;
  token: string;
  model: string;
}

async function readClaudeProviderSettings(): Promise<ClaudeProviderSettings> {
  const configPath = process.env.CLAUDE_CONFIG_PATH;
  if (!configPath) {
    throw new AIProviderError("anthropic-compatible 模式需要 CLAUDE_CONFIG_PATH。", 503);
  }

  let raw: unknown;

  try {
    raw = JSON.parse(await readFile(configPath, "utf8"));
  } catch {
    throw new AIProviderError("无法读取 Claude Code provider 配置。", 503);
  }

  const config = asRecord(raw);
  const env = asRecord(config?.env);
  const baseUrl = env?.ANTHROPIC_BASE_URL;
  const token = env?.ANTHROPIC_AUTH_TOKEN;
  const model = env?.ANTHROPIC_MODEL ?? config?.model;

  if (
    typeof baseUrl !== "string" ||
    typeof token !== "string" ||
    typeof model !== "string" ||
    !baseUrl.trim() ||
    !token.trim() ||
    !model.trim()
  ) {
    throw new AIProviderError(
      "Claude Code provider 配置缺少 ANTHROPIC_BASE_URL、ANTHROPIC_AUTH_TOKEN 或模型名。",
      503,
    );
  }

  return { baseUrl: baseUrl.replace(/\/$/, ""), token, model };
}

export async function getProviderStatus(): Promise<{ mode: ProviderSource; ready: boolean }> {
  const mode = providerName();
  if (mode === "demo") {
    return { mode, ready: true };
  }

  if (mode === "anthropic-compatible") {
    try {
      await readClaudeProviderSettings();
      return { mode, ready: true };
    } catch {
      return { mode, ready: false };
    }
  }

  return {
    mode,
    ready: Boolean(process.env.AI_BASE_URL && process.env.AI_API_KEY && process.env.AI_MODEL),
  };
}

function removeCodeFence(text: string): string {
  const trimmed = text.trim();
  if (trimmed.startsWith("```")) {
    return trimmed.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  }

  const start = trimmed.indexOf("{");
  const end = trimmed.lastIndexOf("}");
  return start >= 0 && end > start ? trimmed.slice(start, end + 1) : trimmed;
}

function parseModelJson(text: string): unknown {
  try {
    return JSON.parse(removeCodeFence(text));
  } catch {
    throw new AIProviderError("模型没有返回可解析的 JSON；请缩短想法后重试。", 502);
  }
}

async function chatForOpenAiJson(system: string, user: string): Promise<unknown> {
  const baseUrl = process.env.AI_BASE_URL?.replace(/\/$/, "");
  const apiKey = process.env.AI_API_KEY;
  const model = process.env.AI_MODEL;

  if (!baseUrl || !apiKey || !model) {
    throw new AIProviderError(
      "openai-compatible 模式需要 AI_BASE_URL、AI_API_KEY 和 AI_MODEL；请使用 .env.local 配置。",
    );
  }

  let response: Response;
  try {
    response = await fetch(`${baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        temperature: 0.2,
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
      }),
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    throw new AIProviderError("无法连接模型服务，请检查 AI_BASE_URL 或网络后重试。", 502);
  }

  if (!response.ok) {
    throw new AIProviderError(`模型服务返回 HTTP ${response.status}。`, 502);
  }

  const body = asRecord(await response.json());
  const choices = body?.choices;
  const firstChoice = Array.isArray(choices) ? asRecord(choices[0]) : undefined;
  const message = asRecord(firstChoice?.message);
  const content = message?.content;

  if (typeof content !== "string" || content.trim().length === 0) {
    throw new AIProviderError("模型返回为空，未生成可用方案。", 502);
  }

  return parseModelJson(content);
}

function messagesEndpoint(baseUrl: string): string {
  return baseUrl.endsWith("/v1") ? `${baseUrl}/messages` : `${baseUrl}/v1/messages`;
}

async function chatForAnthropicJson(system: string, user: string): Promise<unknown> {
  const settings = await readClaudeProviderSettings();
  let response: Response;

  try {
    response = await fetch(messagesEndpoint(settings.baseUrl), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${settings.token}`,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: settings.model,
        max_tokens: 1_800,
        temperature: 0.2,
        system,
        messages: [{ role: "user", content: user }],
      }),
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    throw new AIProviderError("无法连接 Claude provider，请检查本机配置或网络后重试。", 502);
  }

  if (!response.ok) {
    throw new AIProviderError(`Claude provider 返回 HTTP ${response.status}。`, 502);
  }

  const body = asRecord(await response.json());
  const blocks = body?.content;
  const text = Array.isArray(blocks)
    ? blocks
        .map((block) => asRecord(block)?.text)
        .find((content): content is string => typeof content === "string" && content.trim().length > 0)
    : undefined;

  if (!text) {
    throw new AIProviderError("Claude provider 返回为空，未生成可用方案。", 502);
  }

  return parseModelJson(text);
}

async function chatForJson(
  source: Exclude<ProviderSource, "demo">,
  system: string,
  user: string,
): Promise<unknown> {
  return source === "anthropic-compatible"
    ? chatForAnthropicJson(system, user)
    : chatForOpenAiJson(system, user);
}

const BLUEPRINT_CONTRACT = `返回一个 JSON 对象，必须只有以下字段：
{
  "projectTitle": "string",
  "oneSentencePitch": "string",
  "targetUsers": ["string"],
  "problem": "string",
  "coreScenario": "string",
  "mvpScope": ["string"],
  "nonGoals": ["string"],
  "acceptanceCriteria": [{"operation":"string","expected":"string"}],
  "risks": [{"risk":"string","mitigation":"string"}],
  "architecture": ["string"],
  "aiBoundary": ["string"]
}
所有内容使用简体中文。MVP 范围控制在 3 到 5 项；验收标准至少 2 项且必须是“操作 → 可观察预期输出”。不得声称已经执行了真实市场调研或法律审查。`;

export async function generateBlueprintWithProvider(
  input: NewProjectInput,
): Promise<GeneratedBlueprint> {
  const source = providerName();
  if (source === "demo") {
    return { blueprint: createDemoBlueprint(input), source };
  }

  const payload = await chatForJson(
    source,
    "你是审慎的 AI 产品经理。只输出合法 JSON，不使用 Markdown 代码块。",
    `${BLUEPRINT_CONTRACT}\n\n项目名称：${input.name}\n产品想法：${input.idea}`,
  );

  return { blueprint: validateBlueprint(payload), source };
}

function parseReviewFinding(value: unknown, index: number): ReviewFinding {
  const record = asRecord(value);
  const id = record?.id;
  const severity = record?.severity;
  const area = record?.area;
  const message = record?.message;
  const recommendation = record?.recommendation;

  if (
    (severity !== "blocking" && severity !== "warning" && severity !== "info") ||
    typeof area !== "string" ||
    typeof message !== "string" ||
    typeof recommendation !== "string"
  ) {
    throw new AIProviderError("模型审查结果不符合约定格式。", 502);
  }

  return {
    id: typeof id === "string" && id.trim() ? id.trim() : `model-${index + 1}`,
    severity,
    area: area.trim(),
    message: message.trim(),
    recommendation: recommendation.trim(),
  };
}

function parseModelReview(payload: unknown): ReviewReport {
  const record = asRecord(payload);
  const readiness = record?.readiness;
  const summary = record?.summary;
  const findings = record?.findings;

  if (
    (readiness !== "ready" && readiness !== "needs-revision") ||
    typeof summary !== "string" ||
    !Array.isArray(findings)
  ) {
    throw new AIProviderError("模型审查结果缺少 readiness、summary 或 findings。", 502);
  }

  return {
    readiness,
    summary: summary.trim(),
    findings: findings.map(parseReviewFinding),
    reviewedAt: new Date().toISOString(),
    source: "model",
  };
}

export async function reviewBlueprintWithProvider(blueprint: Blueprint): Promise<ReviewReport> {
  const source = providerName();
  if (source === "demo") {
    return reviewBlueprint(blueprint);
  }

  const payload = await chatForJson(
    source,
    "你是独立项目方案审查员。只输出合法 JSON，不使用 Markdown 代码块。",
    `请审查下面的项目蓝图，重点检查范围、验收标准、非目标、风险和 AI 人工确认边界。\n返回：{"readiness":"ready 或 needs-revision","summary":"string","findings":[{"id":"string","severity":"blocking|warning|info","area":"string","message":"string","recommendation":"string"}]}。\n\n${JSON.stringify(blueprint)}`,
  );

  return parseModelReview(payload);
}
