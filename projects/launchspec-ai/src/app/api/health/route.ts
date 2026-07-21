import { getProviderStatus } from "@/lib/ai-provider";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return Response.json({
    status: "ok",
    storage: "local-json",
    provider: await getProviderStatus(),
  });
}
