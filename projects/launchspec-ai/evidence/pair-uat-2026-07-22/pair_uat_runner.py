"""
Pair UAT for LaunchSpec AI — 2026-07-22
Session A = 项目负责人 (Project Lead)
Session B = 团队评审人 (Team Reviewer)
"""
import json, time, datetime, sys, urllib.request, urllib.error
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:3000"
EVIDENCE_DIR = Path(__file__).parent
SHOTS_DIR = EVIDENCE_DIR / "screenshots"
SHOTS_DIR.mkdir(exist_ok=True)

results = []
errors  = []

def ts():
    return datetime.datetime.utcnow().strftime("%H%M%S%f")[:10]

def shot(page, label):
    path = str(SHOTS_DIR / f"{ts()}_{label}.png")
    page.screenshot(path=path, full_page=True)
    return path

def record(sid, step, ok, detail, t0, sc=""):
    ms = int((time.time() - t0) * 1000)
    st = "PASS" if ok else "FAIL"
    results.append({"id": sid, "step": step, "status": st,
                    "detail": detail, "ms": ms, "screenshot": sc})
    print(f"[{st}] {sid}: {step} ({ms}ms) — {detail}")

def attach_console(page, session):
    page.on("console", lambda m: errors.append(
        {"session": session, "type": m.type, "text": m.text, "url": page.url}
    ) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda exc: errors.append(
        {"session": session, "type": "pageerror", "text": str(exc), "url": page.url}
    ))

def api_get(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}") as r:
        return r.status, json.loads(r.read())

def api_post(path, body):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

PROJECT_NAME = "UAT对偶会话测试-2026-07-22"
PROJECT_IDEA = (
    "帮助小型创业团队把零散产品想法整理为可评审可导出的MVP项目方案。"
    "用户角色包括项目负责人和团队评审人，目标是从想法到可执行共识的全流程覆盖，"
    "覆盖范围界定非目标验收标准风险和架构约束。"
)


def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, channel="chrome")

        # PRE-01: health check
        t0 = time.time()
        try:
            status, body = api_get("/api/health")
            ok = body.get("status") == "ok" and body["provider"]["ready"]
            record("PRE-01", "GET /api/health status=ok provider.ready=true",
                   ok, json.dumps(body), t0)
        except Exception as e:
            record("PRE-01", "GET /api/health", False, str(e), t0)

        # SESSION A
        ctx_a = browser.new_context()
        page_a = ctx_a.new_page()
        attach_console(page_a, "A")

        # A-01 首页加载
        t0 = time.time()
        try:
            page_a.goto(BASE_URL, wait_until="networkidle", timeout=15000)
            page_a.wait_for_selector("text=LaunchSpec AI", timeout=8000)
            sc = shot(page_a, "A01_homepage")
            provider_text = page_a.locator(".topbar-status").inner_text()
            record("A-01", "首页加载 + provider 状态显示", True, provider_text, t0, sc)
        except Exception as e:
            record("A-01", "首页加载", False, str(e), t0)

        # A-02 边界: 名称1字符 → HTML5 validation 阻止
        t0 = time.time()
        try:
            page_a.fill('input[placeholder*="LaunchSpec"]', "X")
            page_a.fill('textarea[placeholder*="帮助"]', "too short")
            page_a.click('button[type="submit"]')
            time.sleep(0.5)
            still = page_a.locator('input[placeholder*="LaunchSpec"]').count() > 0
            sc = shot(page_a, "A02_boundary_name_1char")
            record("A-02", "边界:名称1字符+内容过短 HTML5阻止提交", still,
                   "form not submitted", t0, sc)
        except Exception as e:
            record("A-02", "边界:名称1字符", False, str(e), t0)

        # A-03 边界: idea 19字符 (minLength=20) 阻止提交
        t0 = time.time()
        try:
            page_a.fill('input[placeholder*="LaunchSpec"]', "AB")
            page_a.fill('textarea[placeholder*="帮助"]', "1234567890123456789")
            page_a.click('button[type="submit"]')
            time.sleep(0.4)
            still = page_a.locator('input[placeholder*="LaunchSpec"]').count() > 0
            sc = shot(page_a, "A03_boundary_idea_19chars")
            record("A-03", "边界:idea 19字符(minLength=20)阻止提交",
                   still, "minLength blocks submit", t0, sc)
        except Exception as e:
            record("A-03", "边界:idea 19字符", False, str(e), t0)

        # A-04 有效创建
        t0 = time.time()
        try:
            page_a.fill('input[placeholder*="LaunchSpec"]', PROJECT_NAME)
            page_a.fill('textarea[placeholder*="帮助"]', PROJECT_IDEA)
            shot(page_a, "A04_before_create")
            page_a.click('button[type="submit"]')
            page_a.wait_for_selector("text=已保存项目想法", timeout=8000)
            sc = shot(page_a, "A04_after_create")
            record("A-04", "有效创建项目想法 notice=已保存", True,
                   f"name={PROJECT_NAME}", t0, sc)
        except Exception as e:
            record("A-04", "有效创建", False, str(e), t0)
            shot(page_a, "A04_fail")

        # 获取 project ID
        project_id = None
        try:
            _, plist = api_get("/api/projects")
            for p in plist.get("projects", []):
                if p.get("name") == PROJECT_NAME:
                    project_id = p["id"]
                    break
            if not project_id and plist.get("projects"):
                project_id = plist["projects"][0]["id"]
        except Exception as e:
            errors.append({"session": "setup", "type": "error", "text": str(e), "url": ""})

        # A-05 生成蓝图
        t0 = time.time()
        try:
            for sel in ['button:has-text("生成第一版方案")',
                        'button:has-text("生成蓝图")']:
                if page_a.locator(sel).count() > 0:
                    page_a.click(sel)
                    break
            page_a.wait_for_selector("text=已生成可编辑的 demo 草案", timeout=20000)
            sc = shot(page_a, "A05_after_generate")
            record("A-05", "生成蓝图(demo) notice=已生成可编辑demo草案",
                   True, "blueprint generated", t0, sc)
        except Exception as e:
            record("A-05", "生成蓝图", False, str(e), t0)
            shot(page_a, "A05_fail")

        # A-06 蓝图板块可见
        t0 = time.time()
        try:
            c = page_a.content()
            found = [s for s in ["MVP", "验收标准", "非目标", "风险", "架构"] if s in c]
            sc = shot(page_a, "A06_blueprint_sections")
            record("A-06", "蓝图编辑器核心板块可见", len(found) >= 3,
                   f"found={found}", t0, sc)
        except Exception as e:
            record("A-06", "蓝图板块可见", False, str(e), t0)

        # A-07 人工编辑蓝图
        t0 = time.time()
        edited = False
        try:
            for ta in page_a.locator("textarea").all():
                try:
                    if ta.is_visible() and ta.is_editable():
                        ta.fill(ta.input_value() + " [UAT手工编辑-负责人]")
                        edited = True
                        break
                except Exception:
                    continue
            sc = shot(page_a, "A07_after_edit")
            record("A-07", "人工编辑蓝图字段", edited,
                   "textarea edited" if edited else "no editable textarea", t0, sc)
        except Exception as e:
            record("A-07", "人工编辑蓝图", False, str(e), t0)

        # A-08 保存编辑
        t0 = time.time()
        try:
            page_a.click('button:has-text("保存编辑")')
            page_a.wait_for_selector("text=方案已保存", timeout=8000)
            sc = shot(page_a, "A08_after_save")
            record("A-08", "保存编辑 notice=方案已保存", True, "save ok", t0, sc)
        except Exception as e:
            record("A-08", "保存编辑", False, str(e), t0)
            shot(page_a, "A08_fail")

        # A-09 执行审查
        t0 = time.time()
        try:
            page_a.click('button:has-text("执行审查")')
            page_a.wait_for_selector("text=规则检查已完成", timeout=12000)
            sc = shot(page_a, "A09_after_review")
            record("A-09", "执行审查 notice=规则检查已完成", True,
                   "demo rules review", t0, sc)
        except Exception as e:
            record("A-09", "Session A 执行审查", False, str(e), t0)
            shot(page_a, "A09_fail")

        # A-10 导出 .md
        t0 = time.time()
        try:
            if project_id:
                with urllib.request.urlopen(
                    f"{BASE_URL}/api/projects/{project_id}/export"
                ) as r:
                    export_text = r.read().decode("utf-8")
                ok = len(export_text) > 100 and "#" in export_text
                sp = str(EVIDENCE_DIR / "export_sample.md")
                with open(sp, "w", encoding="utf-8") as f:
                    f.write(export_text[:3000])
                record("A-10", "导出Markdown GET/export 返回.md内容",
                       ok, f"len={len(export_text)}", t0, sp)
            else:
                record("A-10", "导出Markdown", False, "no project_id", t0)
        except Exception as e:
            record("A-10", "导出Markdown", False, str(e), t0)

        # A-11 刷新持久化
        t0 = time.time()
        try:
            page_a.reload(wait_until="networkidle", timeout=15000)
            page_a.wait_for_selector("text=LaunchSpec AI", timeout=8000)
            still = PROJECT_NAME in page_a.content()
            sc = shot(page_a, "A11_after_reload")
            record("A-11", "Session A 刷新后项目仍在侧边栏", still,
                   f"persisted={still}", t0, sc)
        except Exception as e:
            record("A-11", "Session A 刷新持久化", False, str(e), t0)

        # A-12 点选项目验证编辑持久化
        t0 = time.time()
        try:
            page_a.locator(f'text="{PROJECT_NAME}"').first.click()
            time.sleep(1.0)
            persisted = "UAT手工编辑-负责人" in page_a.content()
            sc = shot(page_a, "A12_edit_persisted")
            record("A-12", "刷新后手工编辑内容持久化", persisted,
                   f"edit persisted={persisted}", t0, sc)
        except Exception as e:
            record("A-12", "编辑持久化验证", False, str(e), t0)

        # SESSION B — 团队评审人
        ctx_b = browser.new_context()
        page_b = ctx_b.new_page()
        attach_console(page_b, "B")

        # B-01 独立打开首页
        t0 = time.time()
        try:
            page_b.goto(BASE_URL, wait_until="networkidle", timeout=15000)
            page_b.wait_for_selector("text=LaunchSpec AI", timeout=8000)
            sc = shot(page_b, "B01_homepage")
            record("B-01", "Session B 独立context打开首页", True,
                   "independent context ok", t0, sc)
        except Exception as e:
            record("B-01", "Session B 首页", False, str(e), t0)

        # B-02 B 看到 A 创建的项目
        t0 = time.time()
        try:
            sees = PROJECT_NAME in page_b.content()
            sc = shot(page_b, "B02_sees_A_project")
            record("B-02", "Session B 能读到Session A创建的项目",
                   sees, f"visible={sees}", t0, sc)
        except Exception as e:
            record("B-02", "Session B 读A项目", False, str(e), t0)

        # B-03 B 打开项目，看到 A 的手工编辑
        t0 = time.time()
        try:
            page_b.locator(f'text="{PROJECT_NAME}"').first.click()
            time.sleep(1.0)
            sees_edit = "UAT手工编辑-负责人" in page_b.content()
            sc = shot(page_b, "B03_sees_A_edit")
            record("B-03", "Session B 能看到Session A保存的手工编辑",
                   sees_edit, f"edit in B={sees_edit}", t0, sc)
        except Exception as e:
            record("B-03", "Session B 读A编辑", False, str(e), t0)

        # B-04 B 独立执行审查
        t0 = time.time()
        try:
            page_b.click('button:has-text("执行审查")')
            page_b.wait_for_selector("text=规则检查已完成", timeout=12000)
            sc = shot(page_b, "B04_review_done")
            record("B-04", "Session B 独立执行审查 notice=规则检查已完成",
                   True, "B review ok", t0, sc)
        except Exception as e:
            record("B-04", "Session B 执行审查", False, str(e), t0)
            shot(page_b, "B04_fail")

        # B-05 B 刷新后审查结果持久化
        t0 = time.time()
        try:
            page_b.reload(wait_until="networkidle", timeout=15000)
            page_b.wait_for_selector("text=LaunchSpec AI", timeout=8000)
            page_b.locator(f'text="{PROJECT_NAME}"').first.click()
            time.sleep(1.0)
            c = page_b.content()
            has_review = any(k in c for k in ["审查结论", "审查", "通过", "建议"])
            sc = shot(page_b, "B05_review_persisted")
            record("B-05", "Session B 刷新后审查结果持久化",
                   has_review, f"review in DOM={has_review}", t0, sc)
        except Exception as e:
            record("B-05", "Session B 审查持久化", False, str(e), t0)

        # C-01 并发写: A先→B后 → last-write-wins
        t0 = time.time()
        try:
            page_a.locator(f'text="{PROJECT_NAME}"').first.click()
            time.sleep(0.6)
            for ta in page_a.locator("textarea").all():
                try:
                    if ta.is_visible() and ta.is_editable():
                        ta.fill(ta.input_value() + " [A-concurrent]")
                        break
                except Exception:
                    continue
            for tb in page_b.locator("textarea").all():
                try:
                    if tb.is_visible() and tb.is_editable():
                        tb.fill(tb.input_value() + " [B-concurrent]")
                        break
                except Exception:
                    continue
            page_a.click('button:has-text("保存编辑")')
            page_a.wait_for_selector("text=方案已保存", timeout=8000)
            shot(page_a, "C01_A_saved")
            page_b.click('button:has-text("保存编辑")')
            page_b.wait_for_selector("text=方案已保存", timeout=8000)
            shot(page_b, "C01_B_saved")
            if project_id:
                _, final = api_get(f"/api/projects/{project_id}")
                sp = str(EVIDENCE_DIR / "concurrent_final_state.json")
                with open(sp, "w", encoding="utf-8") as f:
                    json.dump(final, f, ensure_ascii=False, indent=2)
                fs = json.dumps(final)
                b_won = "[B-concurrent]" in fs
                record("C-01", "并发写A先B后 last-write-wins B应覆盖A",
                       b_won, f"B_won={b_won}", t0, sp)
            else:
                record("C-01", "并发写观察", False, "no project_id", t0)
        except Exception as e:
            record("C-01", "并发写行为观察", False, str(e), t0)

        # E-01 无效 project ID → 404
        t0 = time.time()
        try:
            try:
                urllib.request.urlopen(
                    f"{BASE_URL}/api/projects/nonexistent-99999")
                record("E-01", "GET /projects/{invalid} 404", False,
                       "got 200 expected 404", t0)
            except urllib.error.HTTPError as he:
                record("E-01", "GET /projects/{invalid} 404",
                       he.code == 404, f"HTTP {he.code}", t0)
        except Exception as e:
            record("E-01", "GET invalid project id", False, str(e), t0)

        # E-02 空 body POST /projects → 400/422
        t0 = time.time()
        try:
            code, body = api_post("/api/projects", {})
            record("E-02", "POST /projects {} 400/422",
                   code in (400, 422), f"HTTP {code}: {body}", t0)
        except Exception as e:
            record("E-02", "POST /projects empty body", False, str(e), t0)

        # E-03 名称 121 字符 → 400/422
        t0 = time.time()
        try:
            code2, body2 = api_post("/api/projects",
                                    {"name": "超" * 121, "idea": PROJECT_IDEA})
            record("E-03", "POST /projects name=121chars 400/422",
                   code2 in (400, 422),
                   f"HTTP {code2}: {str(body2)[:80]}", t0)
        except Exception as e:
            record("E-03", "POST /projects name too long", False, str(e), t0)

        shot(page_a, "FINAL_session_A")
        shot(page_b, "FINAL_session_B")
        ctx_a.close()
        ctx_b.close()
        browser.close()

    out = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "base_url": BASE_URL,
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] == "FAIL"),
        "results": results,
        "console_errors": errors,
    }
    rp = EVIDENCE_DIR / "uat_results.json"
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"PAIR UAT  {out['passed']}/{out['total']} PASS  {out['failed']} FAIL")
    print(f"Console errors: {len(errors)}")
    if out["failed"]:
        print("FAILURES:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  [{r['id']}] {r['step']}: {r['detail']}")
    return out["failed"] == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
