import type { AcceptanceCriterion, Blueprint, NewProjectInput, Risk } from "./types";

const PROJECT_NAME_MIN_LENGTH = 2;
const PROJECT_NAME_MAX_LENGTH = 120;
const IDEA_MIN_LENGTH = 20;
const IDEA_MAX_LENGTH = 4_000;

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ValidationError";
  }
}

type JsonRecord = Record<string, unknown>;

function asRecord(value: unknown): JsonRecord {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new ValidationError("请求体必须是 JSON 对象");
  }

  return value as JsonRecord;
}

function readText(
  record: JsonRecord,
  field: string,
  minimum: number,
  maximum: number,
  displayName = field,
): string {
  const value = record[field];

  if (typeof value !== "string") {
    throw new ValidationError(`${displayName} 必须是文本`);
  }

  const normalized = value.trim();
  if (normalized.length < minimum || normalized.length > maximum) {
    throw new ValidationError(`${displayName} 长度必须在 ${minimum} 到 ${maximum} 个字符之间`);
  }

  return normalized;
}

function readTextArray(
  record: JsonRecord,
  field: string,
  minimum: number,
  maximum: number,
): string[] {
  const value = record[field];

  if (!Array.isArray(value) || value.length < minimum || value.length > maximum) {
    throw new ValidationError(`${field} 必须包含 ${minimum} 到 ${maximum} 项`);
  }

  return value.map((item, index) => {
    if (typeof item !== "string" || item.trim().length === 0 || item.trim().length > 600) {
      throw new ValidationError(`${field}[${index}] 必须是 1 到 600 个字符的文本`);
    }
    return item.trim();
  });
}

function readAcceptanceCriteria(record: JsonRecord): AcceptanceCriterion[] {
  const value = record.acceptanceCriteria;
  if (!Array.isArray(value) || value.length < 2 || value.length > 8) {
    throw new ValidationError("acceptanceCriteria 必须包含 2 到 8 项");
  }

  return value.map((item, index) => {
    const criterion = asRecord(item);
    return {
      operation: readText(criterion, "operation", 2, 300, `acceptanceCriteria[${index}].operation`),
      expected: readText(criterion, "expected", 2, 300, `acceptanceCriteria[${index}].expected`),
    };
  });
}

function readRisks(record: JsonRecord): Risk[] {
  const value = record.risks;
  if (!Array.isArray(value) || value.length < 1 || value.length > 8) {
    throw new ValidationError("risks 必须包含 1 到 8 项");
  }

  return value.map((item, index) => {
    const risk = asRecord(item);
    return {
      risk: readText(risk, "risk", 2, 300, `risks[${index}].risk`),
      mitigation: readText(risk, "mitigation", 2, 300, `risks[${index}].mitigation`),
    };
  });
}

export function validateNewProject(payload: unknown): NewProjectInput {
  const record = asRecord(payload);

  return {
    name: readText(record, "name", PROJECT_NAME_MIN_LENGTH, PROJECT_NAME_MAX_LENGTH),
    idea: readText(record, "idea", IDEA_MIN_LENGTH, IDEA_MAX_LENGTH),
  };
}

export function validateBlueprint(payload: unknown): Blueprint {
  const record = asRecord(payload);

  return {
    projectTitle: readText(record, "projectTitle", 2, PROJECT_NAME_MAX_LENGTH),
    oneSentencePitch: readText(record, "oneSentencePitch", 8, 300),
    targetUsers: readTextArray(record, "targetUsers", 1, 5),
    problem: readText(record, "problem", 8, 1_000),
    coreScenario: readText(record, "coreScenario", 8, 1_000),
    mvpScope: readTextArray(record, "mvpScope", 1, 8),
    nonGoals: readTextArray(record, "nonGoals", 1, 8),
    acceptanceCriteria: readAcceptanceCriteria(record),
    risks: readRisks(record),
    architecture: readTextArray(record, "architecture", 1, 8),
    aiBoundary: readTextArray(record, "aiBoundary", 1, 8),
  };
}
