import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it, vi } from "vitest";

import { generateBlueprintWithProvider, reviewBlueprintWithProvider } from "./ai-provider";
import { createDemoBlueprint } from "./blueprint";

const originalProvider = process.env.AI_PROVIDER;
const originalClaudeConfigPath = process.env.CLAUDE_CONFIG_PATH;
const originalFetch = globalThis.fetch;
let temporaryProfileDirectory: string | undefined;

afterEach(async () => {
  if (originalProvider === undefined) {
    delete process.env.AI_PROVIDER;
  } else {
    process.env.AI_PROVIDER = originalProvider;
  }

  if (originalClaudeConfigPath === undefined) {
    delete process.env.CLAUDE_CONFIG_PATH;
  } else {
    process.env.CLAUDE_CONFIG_PATH = originalClaudeConfigPath;
  }

  globalThis.fetch = originalFetch;
  if (temporaryProfileDirectory) {
    await rm(temporaryProfileDirectory, { recursive: true, force: true });
    temporaryProfileDirectory = undefined;
  }
});

describe("AI provider boundary", () => {
  it("uses the deterministic demo provider when explicitly configured", async () => {
    process.env.AI_PROVIDER = "demo";

    const result = await generateBlueprintWithProvider({
      name: "LaunchSpec AI",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });

    expect(result.source).toBe("demo");
    expect(result.blueprint.projectTitle).toBe("LaunchSpec AI");
  });

  it("returns a clearly labelled demo review without pretending it is a model audit", async () => {
    process.env.AI_PROVIDER = "demo";

    const result = await reviewBlueprintWithProvider(
      createDemoBlueprint({
        name: "LaunchSpec AI",
        idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
      }),
    );

    expect(result.source).toBe("demo-rules");
  });

  it("reports an AI provider error when the selected Claude profile is unavailable", async () => {
    process.env.AI_PROVIDER = "anthropic-compatible";
    process.env.CLAUDE_CONFIG_PATH = "/tmp/launchspec-missing-claude-profile.json";

    await expect(
      generateBlueprintWithProvider({
        name: "LaunchSpec AI",
        idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
      }),
    ).rejects.toThrow("无法读取 Claude Code provider 配置");
  });

  it("uses bearer authentication when reusing a Claude Code provider profile", async () => {
    temporaryProfileDirectory = await mkdtemp(join(tmpdir(), "launchspec-claude-profile-"));
    const profilePath = join(temporaryProfileDirectory, "settings.json");
    const blueprint = createDemoBlueprint({
      name: "LaunchSpec AI",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });
    await writeFile(
      profilePath,
      JSON.stringify({
        model: "test-model",
        env: {
          ANTHROPIC_BASE_URL: "https://provider.example",
          ANTHROPIC_AUTH_TOKEN: "test-token",
        },
      }),
    );
    process.env.AI_PROVIDER = "anthropic-compatible";
    process.env.CLAUDE_CONFIG_PATH = profilePath;

    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ content: [{ type: "text", text: JSON.stringify(blueprint) }] }), {
        status: 200,
      }),
    );
    globalThis.fetch = fetchMock;

    await generateBlueprintWithProvider({
      name: "LaunchSpec AI",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "https://provider.example/v1/messages",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
          "anthropic-version": "2023-06-01",
        }),
      }),
    );
  });
});
