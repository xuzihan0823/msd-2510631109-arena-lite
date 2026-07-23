import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { createDemoBlueprint } from "./blueprint";
import { createProjectRepository } from "./repository";

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((directory) => rm(directory, { recursive: true, force: true })));
});

describe("project repository", () => {
  it("persists an editable blueprint and returns projects newest first", async () => {
    const directory = await mkdtemp(join(tmpdir(), "launchspec-test-"));
    temporaryDirectories.push(directory);
    const repository = createProjectRepository(join(directory, "data", "projects.json"));

    const first = await repository.create({
      name: "第一份方案",
      idea: "帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。",
    });
    const second = await repository.create({
      name: "第二份方案",
      idea: "帮助高校社团把活动需求整理为可执行的排期、分工和风险说明。",
    });
    const saved = await repository.saveBlueprint(
      first.id,
      createDemoBlueprint({ name: first.name, idea: first.idea }),
    );

    expect(saved?.blueprint?.projectTitle).toBe("第一份方案");
    expect((await repository.list()).map((project) => project.id)).toEqual([first.id, second.id]);
  });
});
