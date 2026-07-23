import { errorResponse } from "@/lib/api";
import { projectRepository } from "@/lib/repository";
import { reviewBlueprintWithProvider } from "@/lib/ai-provider";
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
    if (!project.blueprint) {
      return Response.json({ error: "请先生成方案后再执行审查。" }, { status: 409 });
    }

    const review = await reviewBlueprintWithProvider(project.blueprint);
    const savedProject = await projectRepository.saveReview(id, review);
    return Response.json({ project: savedProject, reviewer: review.source });
  } catch (error) {
    return errorResponse(error);
  }
}
