import { describe, expect, it } from "vitest";

import { createDemoBlueprint } from "./blueprint";

describe("createDemoBlueprint", () => {
  it("turns one product idea into an editable, bounded proposal", () => {
    const blueprint = createDemoBlueprint({
      name: "LaunchSpec AI",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });

    expect(blueprint.projectTitle).toBe("LaunchSpec AI");
    expect(blueprint.mvpScope).toHaveLength(4);
    expect(blueprint.acceptanceCriteria).toHaveLength(3);
    expect(blueprint.aiBoundary.join(" ")).toContain("人工");
  });
});
