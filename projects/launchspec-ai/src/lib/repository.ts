import { randomUUID } from "node:crypto";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

import type { Blueprint, NewProjectInput, Project, ProjectStore, ReviewReport } from "./types";

function defaultDataFile(): string {
  return process.env.LAUNCHSPEC_DATA_FILE ?? join(process.cwd(), "data", "launchspec.json");
}

function emptyStore(): ProjectStore {
  return { projects: [] };
}

function isProjectStore(value: unknown): value is ProjectStore {
  return (
    typeof value === "object" &&
    value !== null &&
    "projects" in value &&
    Array.isArray((value as { projects?: unknown }).projects)
  );
}

export function createProjectRepository(dataFile = defaultDataFile()) {
  async function readStore(): Promise<ProjectStore> {
    try {
      const contents = await readFile(dataFile, "utf8");
      const parsed: unknown = JSON.parse(contents);
      if (!isProjectStore(parsed)) {
        throw new Error("本地数据文件不是有效的项目列表。");
      }
      return parsed;
    } catch (error) {
      if (error instanceof Error && "code" in error && error.code === "ENOENT") {
        return emptyStore();
      }
      if (error instanceof SyntaxError) {
        throw new Error("本地数据文件无法解析；请恢复备份后重试。");
      }
      throw error;
    }
  }

  async function writeStore(store: ProjectStore): Promise<void> {
    const directory = dirname(dataFile);
    await mkdir(directory, { recursive: true });
    const temporaryFile = `${dataFile}.${randomUUID()}.tmp`;
    await writeFile(temporaryFile, `${JSON.stringify(store, null, 2)}\n`, "utf8");
    await rename(temporaryFile, dataFile);
  }

  async function mutate(
    mutateStore: (store: ProjectStore) => Project | undefined,
  ): Promise<Project | undefined> {
    const store = await readStore();
    const result = mutateStore(store);
    if (result) {
      await writeStore(store);
    }
    return result;
  }

  return {
    async list(): Promise<Project[]> {
      const store = await readStore();
      return [...store.projects].sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
    },

    async get(id: string): Promise<Project | undefined> {
      const store = await readStore();
      return store.projects.find((project) => project.id === id);
    },

    async create(input: NewProjectInput): Promise<Project> {
      const now = new Date().toISOString();
      const project: Project = {
        id: randomUUID(),
        name: input.name,
        idea: input.idea,
        stage: "draft",
        createdAt: now,
        updatedAt: now,
      };
      const store = await readStore();
      store.projects.push(project);
      await writeStore(store);
      return project;
    },

    async saveBlueprint(id: string, blueprint: Blueprint): Promise<Project | undefined> {
      return mutate((store) => {
        const project = store.projects.find((candidate) => candidate.id === id);
        if (!project) {
          return undefined;
        }

        project.blueprint = blueprint;
        project.review = undefined;
        project.stage = "generated";
        project.updatedAt = new Date().toISOString();
        return project;
      });
    },

    async saveReview(id: string, review: ReviewReport): Promise<Project | undefined> {
      return mutate((store) => {
        const project = store.projects.find((candidate) => candidate.id === id);
        if (!project) {
          return undefined;
        }

        project.review = review;
        project.stage = "reviewed";
        project.updatedAt = new Date().toISOString();
        return project;
      });
    },
  };
}

export const projectRepository = createProjectRepository();
