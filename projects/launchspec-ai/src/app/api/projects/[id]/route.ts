import { errorResponse, readField, readJsonBody } from "@/lib/api";
import { projectRepository } from "@/lib/repository";
import type { IdRouteContext } from "@/lib/route-context";
import { validateBlueprint } from "@/lib/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(_request: Request, context: IdRouteContext) {
  try {
    const { id } = await context.params;
    const project = await projectRepository.get(id);
    return project
      ? Response.json({ project })
      : Response.json({ error: "未找到该项目。" }, { status: 404 });
  } catch (error) {
    return errorResponse(error);
  }
}

export async function PUT(request: Request, context: IdRouteContext) {
  try {
    const { id } = await context.params;
    const payload = await readJsonBody(request);
    const blueprint = validateBlueprint(readField(payload, "blueprint"));
    const project = await projectRepository.saveBlueprint(id, blueprint);
    return project
      ? Response.json({ project })
      : Response.json({ error: "未找到该项目。" }, { status: 404 });
  } catch (error) {
    return errorResponse(error);
  }
}
