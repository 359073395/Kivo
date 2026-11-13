import asyncio
import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from lingxi.feedback import FeedbackStore
from lingxi.knowledge import KnowledgeStore
from lingxi import model_runtime as runtime
from web import app as web

CLIENT = httpx.AsyncClient
SETTINGS = {"EASEL_DIRECT_API_BASE_URL": "http://127.0.0.1:9999/v1", "EASEL_DIRECT_API_MODEL": "test-tool-model", "EASEL_DIRECT_API_KEY": "local-test-secret"}


@pytest.fixture
def local(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "knowledge-base.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("LINGXI_KNOWLEDGE_ROOT", str(vault))
    monkeypatch.setenv("LINGXI_DATA_ROOT", str(tmp_path / "runtime"))
    monkeypatch.setenv("LINGXI_KNOWLEDGE_AUTO", "1")
    monkeypatch.setenv("LINGXI_API_TOOLS", "1")
    for key in (*SETTINGS, "EASEL_CHAT_TRANSPORT", "EASEL_AGENT_RUNTIME"):
        monkeypatch.delenv(key, raising=False)
    KnowledgeStore().rebuild()
    return FeedbackStore()


def payload(**overrides):
    return {"platform": "douyin", "account": "测试账号", "contentId": "work-a", "title": "真实标题",
            "source": "合成验收数据", "windowHours": 24, "experiment": "开头测试", "variant": "A",
            "changedVariable": "开头", "metrics": {"views": 1000, "likes": 50}, **overrides}


def test_feedback_dedup_rates_and_unknown(local):
    a = local.add(payload())
    assert local.add(payload())["duplicate"]
    b = local.add(payload(metrics={"views": 2000, "likes": 120}))
    summary = b["learning"]
    assert summary["uniqueWorks"] == 1 and summary["snapshots"] == 2
    assert summary["observations"][0]["rates"]["likeRate"] == .06
    assert "saveRate" not in summary["observations"][0]["rates"]
    local.toggle(b["id"], False)
    assert local.summary("douyin", "测试账号")["observations"][0]["feedbackId"] == a["id"]


@pytest.mark.parametrize("metrics", [{"views": -1}, {"views": float("inf")}, {"views": True}, {"madeup": 4}, {}, {"views": None}])
def test_invalid_feedback(local, metrics):
    with pytest.raises(ValueError): local.add(payload(metrics=metrics))


def test_zero_denominator_is_not_rate(local):
    local.add(payload(metrics={"views": 0, "likes": 0}))
    assert local.summary("douyin", "测试账号")["observations"][0]["rates"] == {}


def test_comparison_respects_window_and_scope(local):
    local.add(payload())
    local.add(payload(contentId="work-b", variant="B", metrics={"views": 1000, "likes": 100}))
    summary = local.summary("douyin", "测试账号")
    comparison = summary["hypotheses"][0]["comparisons"][0]
    assert comparison["highestObservedVariant"] == "B"
    assert comparison["confidence"] == "single_work_per_variant"
    local.add(payload(account="其他账号", contentId="secret-work", title="不应串号", variant="C"))
    assert "不应串号" not in local.context("抖音", account="测试账号")
    assert local.context("抖音", account="") == ""
    assert local.context("小红书", account="测试账号") == ""
    local.add(payload(contentId="different-window", variant="C", windowHours=48))
    assert len(local.summary("douyin", "测试账号")["hypotheses"]) == 1


def test_analytics_hook_does_not_guess_metrics(local):
    result = {"loggedIn": True, "followers": 100, "likes": None,
              "notes": [{"title": "文字抓取", "stat": "1万赞", "note_id": "unknown"},
                        {"title": "结构化数据", "note_id": "structured", "views": 800, "likes": 40}]}
    report = local.ingest_analytics("douyin", "测试账号", result)
    assert report["saved"] == 2
    summary = local.summary("douyin", "测试账号")
    assert summary["uniqueWorks"] == 1
    assert not any(x["contentId"] == "unknown" for x in summary["observations"])
    assert local.ingest_analytics("douyin", "测试账号", result)["saved"] == 0


def test_manual_direct_method_and_feedback_api(local):
    client = TestClient(web.app, base_url="http://localhost:7860", headers={"Origin": "http://localhost:7860"})
    method = "适用当前国内版：先核实产品事实，再设计标题，检查正文兑现；缺少证据时停止承诺。"
    result = client.post("/api/knowledge/learn", json={"title": "手动确认方法", "text": method, "activate": True})
    assert result.status_code == 200 and result.json()["status"] == "approved"
    assert method in KnowledgeStore().context("产品事实")
    data = client.post("/api/knowledge/feedback", json=payload())
    assert data.status_code == 200 and data.json()["status"] == "observed"
    assert client.post("/api/knowledge/feedback", json=payload(metrics={"views": True})).status_code == 422
    context = client.post("/api/knowledge/brief", json={"query": "抖音复盘", "account": "测试账号", "platform": "douyin"}).json()
    assert "<feedback_evidence>" in context["feedbackContext"]
    assert client.post(f'/api/knowledge/feedback/{data.json()["id"]}/enabled', json={"enabled": False}).json()["enabled"] is False
    assert client.get("/api/knowledge/feedback/summary", params={"platform": "douyin", "account": "测试账号"}).json()["uniqueWorks"] == 0


def test_project_tools_paths_no_overwrite_and_approval(tmp_path):
    root = tmp_path
    skill = root / "skills/builtin/sample/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# 原有技能\n按事实创作。", encoding="utf-8")
    script = root / "skills/shared/scripts/safe.py"
    script.parent.mkdir(parents=True)
    script.write_text("print('local tool verified')", encoding="utf-8")
    tools = runtime.ProjectTools("test", root=root)
    async def check():
        assert (await tools.call("list_skills", {}))["skills"] == ["sample"]
        assert "原有技能" in (await tools.call("read_project_file", {"path": "skills/builtin/sample/SKILL.md"}))["text"]
        for path in ("../secret.txt", "outputs/_inbox/other/a.txt", ".env", "C:/private.txt"):
            with pytest.raises(ValueError): await tools.call("read_project_file", {"path": path})
        result = await tools.call("save_artifact", {"name": "标题.md", "text": "原有技能的真实输出"})
        assert (root / "outputs" / result["path"]).is_file()
        with pytest.raises(FileExistsError): await tools.call("save_artifact", {"name": "标题.md", "text": "不允许覆盖"})
        args = {"path": "skills/shared/scripts/safe.py", "args": [], "purpose": "本地验收"}
        assert not (await tools.call("run_builtin_script", args))["executed"]
        async def approve(request):
            assert "safe.py" in request["command"] and request["warning"]
            return True
        tools.approve = approve
        run = await tools.call("run_builtin_script", args)
        assert run["exitCode"] == 0 and "local tool verified" in run["stdout"]
    asyncio.run(check())


def sse(*events):
    return "".join("data: " + (e if isinstance(e, str) else json.dumps(e)) + "\n\n" for e in events)


def test_builtin_scripts_and_media_commands_execute_with_approval(tmp_path, monkeypatch):
    script = tmp_path / "skills/builtin/video-test/scripts/render.py"
    script.parent.mkdir(parents=True)
    (script.parent.parent / "SKILL.md").write_text("# Video", encoding="utf-8")
    script.write_text("import os; print('rendered', os.environ.get('https_proxy'))", encoding="utf-8")
    for key in ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("EASEL_PROXY", "http://127.0.0.1:19876")
    requests = []

    async def approve(request):
        requests.append(json.loads(request["command"]))
        return True

    async def check():
        tools = runtime.ProjectTools("media", root=tmp_path, approve=approve)
        result = await tools.call("run_builtin_script", {
            "path": script.relative_to(tmp_path).as_posix(), "args": [], "purpose": "render"})
        assert result["exitCode"] == 0 and "rendered http://127.0.0.1:19876" in result["stdout"]
        result = await tools.call("run_project_command", {
            "command": ["python", "-c", "from pathlib import Path; print(Path.cwd().name)"],
            "cwd": "skills/builtin/video-test", "purpose": "check working directory"})
        assert result["exitCode"] == 0 and result["stdout"].strip() == "video-test"
        assert requests[-1]["cwd"] == str(script.parent.parent)
        with pytest.raises(ValueError):
            await tools.call("run_project_command", {"command": ["python"], "cwd": "../outside"})
        tools.approve = None
        assert not (await tools.call("run_project_command", {
            "command": ["python", "-c", "raise AssertionError"], "cwd": "."}))["executed"]

    asyncio.run(check())


def test_media_source_files_can_be_created_and_revised_without_lost_updates(tmp_path):
    async def check():
        tools = runtime.ProjectTools("media", root=tmp_path)
        created = await tools.call("save_artifact", {"name": "video/src/Main.tsx", "text": "export const value = 1;\r\n"})
        read = await tools.call("read_project_file", {"path": "outputs/" + created["path"]})
        assert read["sha256"] == created["sha256"]
        updated = await tools.call("save_artifact", {
            "name": "video/src/Main.tsx", "text": "export const value = 2;\n", "expected_sha256": read["sha256"]})
        assert updated["updated"] and not updated["created"]
        with pytest.raises(ValueError, match="作品已变化"):
            await tools.call("save_artifact", {
                "name": "video/src/Main.tsx", "text": "stale", "expected_sha256": read["sha256"]})
        for name in ("../escape.py", "/escape.py", "nested/.env", "nested/../../escape.py"):
            with pytest.raises(ValueError):
                await tools.call("save_artifact", {"name": name, "text": "escape"})
    asyncio.run(check())


def test_api_video_pipeline_uses_the_active_project_outputs(tmp_path, monkeypatch):
    import importlib.util
    script = Path(__file__).resolve().parents[1] / 'skills/builtin/video-production/scripts/video_pipeline.py'
    spec = importlib.util.spec_from_file_location('api_video_pipeline', script)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    (tmp_path / 'easel').mkdir()
    (tmp_path / 'skills/builtin').mkdir(parents=True)
    monkeypatch.setenv('EASEL_AGENT_RUNTIME', 'api')
    monkeypatch.setenv('EASEL_ROOT', str(tmp_path))
    assert pipeline._workspace_root() == tmp_path.resolve()


def chunk(**delta):
    return {"choices": [{"delta": delta, "finish_reason": None}]}


def finish(reason):
    return {"choices": [{"delta": {}, "finish_reason": reason}]}


def mock_api(monkeypatch, handler):
    def client(**kwargs):
        assert kwargs["trust_env"] is False and kwargs["follow_redirects"] is False
        return CLIENT(transport=httpx.MockTransport(handler), **kwargs)
    monkeypatch.setattr(runtime.httpx, "AsyncClient", client)


def test_generic_api_real_tool_cycle_and_history(local, tmp_path, monkeypatch):
    tools = runtime.ProjectTools("api-cycle", root=tmp_path)
    seen = []
    def respond(request):
        body = json.loads(request.content)
        seen.append(body)
        assert request.headers["Authorization"] == "Bearer local-test-secret"
        assert "tools" in body and not any(k.startswith("x-openclaw") for k in request.headers)
        if len(seen) == 1:
            return httpx.Response(200, text=sse(
                chunk(tool_calls=[{"index": 0, "id": "call1", "function": {"name": "save_artifact", "arguments": '{"name":"test.md",'}}]),
                chunk(tool_calls=[{"index": 0, "function": {"arguments": '"text":"API独立工作流的本地作品"}'}}]), finish("tool_calls"), "[DONE]"))
        assert json.loads(body["messages"][-1]["content"])["created"] is True
        return httpx.Response(200, text=sse(chunk(content="作品已保存"), finish("stop"), "[DONE]"))
    mock_api(monkeypatch, respond)
    history = tmp_path / "history.json"
    async def collect(): return [x async for x in runtime.stream_agent(SETTINGS, "写标题并保存", system=runtime.AGENT_PROMPT, tools=tools, history_file=history)]
    events = asyncio.run(collect())
    assert events[-1] == ("finish", "stop")
    assert len(seen) == 2 and json.loads(history.read_text(encoding="utf-8"))[-2]["role"] == "tool"
    assert len(list((tmp_path / "outputs").rglob("test.md"))) == 1


def test_api_workflow_can_continue_past_twelve_tool_rounds(local, tmp_path, monkeypatch):
    tools = runtime.ProjectTools("long-workflow", root=tmp_path)
    rounds = []

    def respond(request):
        rounds.append(json.loads(request.content))
        if len(rounds) <= 13:
            return httpx.Response(200, text=sse(chunk(tool_calls=[{
                "index": 0, "id": f"call{len(rounds)}", "function": {"name": "list_skills", "arguments": "{}"}
            }]), finish("tool_calls"), "[DONE]"))
        return httpx.Response(200, text=sse(chunk(content="工作流完成"), finish("stop"), "[DONE]"))

    mock_api(monkeypatch, respond)

    async def collect():
        return [event async for event in runtime.stream_agent(SETTINGS, "执行制作流程", system="", tools=tools)]

    assert asyncio.run(collect())[-1] == ("finish", "stop")
    assert len(rounds) == 14


@pytest.mark.parametrize("response", [httpx.Response(401, text="local-test-secret"), httpx.Response(200, text="data: not-json\n\n"), httpx.Response(200, text=sse(chunk(content="不完整"), "[DONE]"))])
def test_api_failures_are_safe_and_not_success(local, tmp_path, monkeypatch, response):
    mock_api(monkeypatch, lambda request: response)
    path = tmp_path / "history.json"
    async def collect(): return [x async for x in runtime.stream_agent(SETTINGS, "hello", system="", history_file=path)]
    with pytest.raises(runtime.DirectAPIError) as error: asyncio.run(collect())
    assert "local-test-secret" not in str(error.value) and not path.exists()


def test_web_api_does_not_invoke_any_client(local, tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("EASEL_AGENT_RUNTIME=api\n" + "\n".join(f"{k}={v}" for k, v in SETTINGS.items()), encoding="utf-8")
    monkeypatch.setattr(web, "ENV_FILE", env)
    monkeypatch.setattr(web, "SESSIONS_DIR", tmp_path / "sessions")
    monkeypatch.setattr(web, "OPENCLAW_SESSIONS_DIR", tmp_path / "oc-sessions")
    monkeypatch.setattr(web, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(web, "_session_locks", {})
    monkeypatch.setattr(web, "_RUNNING_CHAT", {})
    def forbidden(*args, **kwargs): raise AssertionError("不能启动客户端")
    for name in ("openclaw_base_cmd", "_gateway_http_ready", "check_gateway", "_run_harness_chat"):
        monkeypatch.setattr(web, name, forbidden)
    mock_api(monkeypatch, lambda request: httpx.Response(200, text=sse(chunk(content="独立API测试通过"), finish("stop"), "[DONE]")))
    client = TestClient(web.app, base_url="http://localhost:7860", headers={"Origin": "http://localhost:7860"})
    response = client.post("/api/chat", json={"message": "你好", "sessionId": "new-api"})
    assert response.status_code == 200 and response.json()["response"] == "独立API测试通过"
    assert client.get("/api/chat/last/new-api").json()["clean_end"] is True
    monkeypatch.setattr(web, "find_skill", lambda name: "sample")
    skill = client.post("/api/skill", json={"skill": "sample", "input": "本地API技能验收"})
    assert skill.status_code == 200 and skill.json()["response"] == "独立API测试通过"
