import { describe, expect, it } from "vitest";

import { createDemoBlueprint } from "./blueprint";
import { ValidationError, validateBlueprint, validateNewProject } from "./validation";

describe("validateNewProject", () => {
  it("accepts a focused product name and a sufficiently detailed idea", () => {
    expect(
      validateNewProject({
        name: "LaunchSpec AI",
        idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
      }),
    ).toEqual({
      name: "LaunchSpec AI",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });
  });

  it("rejects an idea that cannot support a testable proposal", () => {
    expect(() => validateNewProject({ name: "A", idea: "做个应用" })).toThrow(
      ValidationError,
    );
  });

  it("rejects non-object payloads", () => {
    expect(() => validateNewProject(null)).toThrow("请求体必须是 JSON 对象");
  });

  it("accepts a complete blueprint with nested acceptance criteria and risks", () => {
    const blueprint = createDemoBlueprint({
      name: "LaunchSpec AI",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });

    expect(validateBlueprint(blueprint)).toEqual(blueprint);
  });
});
