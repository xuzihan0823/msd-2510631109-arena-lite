import { generateBlueprintWithProvider } from "@/lib/ai-provider";
import { errorResponse } from "@/lib/api";
import { projectRepository } from "@/lib/repository";
import type { IdRouteContext } from "@/lib/route-context";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(_request: Request, context: IdRouteContext) {
  try {
    const { id } = await context.params;
    const project = await projectRepository.get(id);
    if (!project) {
      return Response.json({ error: "未找到该项目。" }, { status: 404 });
    }

    const generated = await generateBlueprintWithProvider({
      name: project.name,
      idea: project.idea,
    });
    const savedProject = await projectRepository.saveBlueprint(id, generated.blueprint);

    return Response.json({ project: savedProject, provider: generated.source });
  } catch (error) {
    return errorResponse(error);
  }
}
