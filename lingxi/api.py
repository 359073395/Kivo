"""Knowledge endpoints mounted alongside the upstream application."""
import re
import sqlite3

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel, Field, StrictFloat

from .knowledge import get_store, redact
from .feedback import FeedbackStore

router = APIRouter(prefix="/api/knowledge", tags=["Kivo知识库"])


def _call(fn):
    try:
        return fn()
    except (ValueError, OSError, sqlite3.DatabaseError) as error:
        raise HTTPException(400, str(error) if isinstance(error, ValueError) else "本地资料暂不可读，请检查知识库路径") from None


@router.get("/status")
def status():
    return _call(lambda: get_store().status())


@router.post("/rebuild")
def rebuild():
    return _call(lambda: get_store().rebuild())


@router.get("/search")
def search(q: str = Query("", max_length=2000), category: str = "", limit: int = Query(12, ge=1, le=30)):
    return {"items": _call(lambda: get_store().search(q, category, limit))}


@router.get("/document/{rid}")
def document(rid: str):
    return _call(lambda: get_store().document(rid))


@router.get("/inventory")
def inventory(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    return _call(lambda: get_store().inventory(limit, offset))


class BriefRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)
    category: str = ""
    platform: str = Field(default="", max_length=100)
    account: str = Field(default="", max_length=200)


@router.post("/brief")
def brief(req: BriefRequest):
    result = _call(lambda: get_store().brief(req.query, req.category))
    result["feedbackContext"] = _call(lambda: FeedbackStore().context(req.query, account=req.account, platform=req.platform))
    return result


class LearnRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    text: str = Field(min_length=20, max_length=300000)
    source: str = Field(default="", max_length=1500)
    category: str = "content"
    activate: bool = False


@router.get("/learned")
def learned():
    return {"items": _call(lambda: get_store()._learned())}


@router.post("/learn")
def learn(req: LearnRequest):
    if req.activate and len(req.text.strip()) > 30000:
        raise HTTPException(400, "直接使用的方法限30000字；长资料请先导入提炼")
    item = _call(lambda: get_store().learn(req.title, req.text, req.source, req.category))
    if req.activate:
        item = _call(lambda: get_store().approve(item["id"], item["sourceHash"], req.text))
    return item


class FeedbackRequest(BaseModel):
    platform: str = Field(min_length=1, max_length=100)
    account: str = Field(min_length=1, max_length=200)
    contentId: str = Field(min_length=1, max_length=500)
    title: str = Field(default="", max_length=500)
    variant: str = Field(default="", max_length=100)
    experiment: str = Field(default="", max_length=200)
    changedVariable: str = Field(default="", max_length=200)
    windowHours: StrictFloat | None = None
    metrics: dict[str, StrictFloat | None] = Field(default_factory=dict)
    source: str = Field(min_length=1, max_length=500)
    notes: str = Field(default="", max_length=3000)


@router.post("/feedback")
def add_feedback(req: FeedbackRequest):
    return _call(lambda: FeedbackStore().add(req.model_dump()))


@router.get("/feedback")
def feedback(platform: str = "", account: str = ""):
    return {"items": _call(lambda: FeedbackStore().rows(platform, account, enabled=False))}


@router.get("/feedback/summary")
def feedback_summary(platform: str, account: str):
    return _call(lambda: FeedbackStore().summary(platform, account))


class FeedbackBatch(BaseModel):
    items: list[FeedbackRequest] = Field(min_length=1, max_length=100)


@router.post("/feedback/import")
def feedback_import(req: FeedbackBatch):
    store = FeedbackStore()
    for item in req.items:
        _call(lambda item=item: store.add(item.model_dump(), validate_only=True))
    return {"items": [_call(lambda r=r: store.add(r.model_dump())) for r in req.items]}


class EnableFeedback(BaseModel):
    enabled: bool


@router.post("/feedback/{identifier}/enabled")
def enable_feedback(identifier: str, req: EnableFeedback):
    return _call(lambda: FeedbackStore().toggle(identifier, req.enabled))


@router.post("/import")
async def import_text(file: UploadFile = File(...), category: str = Form("content")):
    if not file.filename or not file.filename.lower().endswith((".md", ".txt")):
        raise HTTPException(400, "请选择已完整文字化的 Markdown 或 TXT；视频/PDF 请先使用原有转写技能")
    raw = await file.read(1200001)
    if len(raw) > 1200000: raise HTTPException(413, "文字资料不能超过1.2MB")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError:
        raise HTTPException(400, "请使用 UTF-8 编码的文字稿") from None
    return _call(lambda: get_store().learn(file.filename.rsplit(".", 1)[0], text, file.filename, category))


class ApproveRequest(BaseModel):
    sourceHash: str
    method: str = Field(min_length=20, max_length=30000)


@router.post("/learned/{item_id}/approve")
def approve(item_id: str, req: ApproveRequest):
    return _call(lambda: get_store().approve(item_id, req.sourceHash, req.method))


class CheckRequest(BaseModel):
    title: str = Field(default="", max_length=1000)
    content: str = Field(min_length=1, max_length=30000)
    facts: str = Field(default="", max_length=30000)


@router.post("/check")
def check(req: CheckRequest):
    text = req.title + "\n" + req.content
    findings = []
    if redact(text) != text:
        findings.append({"kind": "credential", "message": "含疑似凭据，不能进入对外稿件"})
    claims = sorted(set(re.findall(r"治愈|保证有效|百分百|100%|全网第一|永久有效|零风险|绝对安全|人人适用", text)))
    if claims:
        findings.append({"kind": "claim", "message": "请核对依据或改写这些承诺：" + "、".join(claims)})
    numbers = set(re.findall(r"\d+(?:\.\d+)?(?:%|小时|分钟|天|年|岁|ml|mL|g|克|件|元)?", text))
    unsupported = sorted(n for n in numbers if n not in req.facts)
    if unsupported:
        findings.append({"kind": "number", "message": "事实资料中未找到这些数字，请逐项核对：" + "、".join(unsupported[:20])})
    if not req.facts.strip():
        findings.append({"kind": "facts_pending", "message": "未提供本账号/产品事实，经历、案例、规格和功效仍待人工核验"})
    return {"titleLength": len(req.title), "contentLength": len(req.content), "findings": findings,
            "status": "needs_review" if findings else "automated_checks_clear",
            "limitation": "此检查发现可见文本问题；不能证明事实、版权、平台审核或营销效果通过",
            "evidence": get_store().brief("标题 文案 真实卖点 商品事实")["evidence"][:3]}


def augment_message(message: str) -> str:
    if "<knowledge_evidence>" in message:
        return message
    context = get_store().context(message)
    return message + "\n\n" + context if context else message
