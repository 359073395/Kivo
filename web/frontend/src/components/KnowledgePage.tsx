import { useCallback, useEffect, useState } from 'react';
import FeedbackLearning from './FeedbackLearning';
import '../styles/knowledge.css';

type Entry = { id: string; title: string; body: string; excerpt: string; source: string; status: string; scope: string; categoryLabel: string; sha256: string; start_line: number; end_line: number };
type Learned = { id: string; title: string; text: string; source: string; sourceHash: string; status: string; method: string };
type Status = { ready: boolean; files: number; chunks: number; methodCards: number; domesticMethods: number; learned: number; generatedAt: string; categories: Record<string, number>; labels: Record<string, string>; decisions: Record<string, number> };
type Check = { status: string; titleLength: number; contentLength: number; findings: { kind: string; message: string }[]; limitation: string };
type Inventory = { path: string; size: number; category: string; decision: string; canonical: string };
const STATUS: Record<string, string> = { active_project: '国内方法', approved: '已审核方法', candidate: '待审核', reviewed_reference: '已整理参考', reference: '参考资料', source_view: '来源观点' };
const DECISIONS: Record<string, string> = { indexed: '已索引', duplicate: '重复镜像', historical_or_project_context: '历史 / 项目资料', binary_or_tool_catalog_only: '原件 / 工具', maintenance_catalog_only: '维护资料', local_metadata_excluded: '本机配置', human_mirror_catalog_only: '人读镜像', encoding_pending: '编码待处理', oversize_pending: '大文件待处理', linked_path_excluded: '外部链接' };

async function request<T>(path: string, data?: unknown): Promise<T> {
  const res = await fetch(`./api/knowledge/${path}`, data === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
  });
  const result = await res.json();
  if (!res.ok) throw new Error(typeof result.detail === 'string' ? result.detail : '资料处理失败，请检查输入');
  return result as T;
}

export default function KnowledgePage({ onCreate, accountName = '' }: { onCreate: (prompt: string) => void; accountName?: string }) {
  const [tab, setTab] = useState<'search' | 'create' | 'learn' | 'feedback' | 'inventory'>('search');
  const [status, setStatus] = useState<Status | null>(null);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [items, setItems] = useState<Entry[]>([]);
  const [selected, setSelected] = useState<Entry | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [goal, setGoal] = useState('');
  const [platform, setPlatform] = useState('小红书');
  const [mode, setMode] = useState('标题与文案');
  const [facts, setFacts] = useState('');
  const [draftTitle, setDraftTitle] = useState('');
  const [draft, setDraft] = useState('');
  const [check, setCheck] = useState<Check | null>(null);
  const [learned, setLearned] = useState<Learned[]>([]);
  const [learnTitle, setLearnTitle] = useState('');
  const [learnSource, setLearnSource] = useState('');
  const [learnText, setLearnText] = useState('');
  const [activate, setActivate] = useState(false);
  const [review, setReview] = useState<Learned | null>(null);
  const [method, setMethod] = useState('');
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [offset, setOffset] = useState(0);

  const refresh = useCallback(async () => {
    const [st, li] = await Promise.all([request<Status>('status'), request<{ items: Learned[] }>('learned')]);
    setStatus(st); setLearned(li.items);
  }, []);
  useEffect(() => { void refresh().catch((e: Error) => setError(e.message)); }, [refresh]);
  useEffect(() => {
    const ctl = new AbortController();
    const timer = setTimeout(() => {
      void fetch(`./api/knowledge/search?q=${encodeURIComponent(query)}&category=${category}&limit=20`, { signal: ctl.signal })
        .then(async (r) => { if (!r.ok) throw new Error('知识检索暂不可用'); return r.json(); })
        .then((r: { items: Entry[] }) => setItems(r.items))
        .catch((e: Error) => { if (e.name !== 'AbortError') setError(e.message); });
    }, 180);
    return () => { clearTimeout(timer); ctl.abort(); };
  }, [query, category, status?.generatedAt]);
  useEffect(() => {
    if (tab !== 'inventory') return;
    void request<{ items: Inventory[] }>(`inventory?limit=100&offset=${offset}`).then((r) => setInventory(r.items)).catch((e: Error) => setError(e.message));
  }, [tab, offset, status?.generatedAt]);

  const run = async (action: () => Promise<void>) => {
    setBusy(true); setError(''); setNotice('');
    try { await action(); } catch (e) { setError(e instanceof Error ? e.message : '处理失败'); }
    finally { setBusy(false); }
  };
  const create = () => onCreate(`请使用Kivo国内版知识库及当前画像，为${platform}完成${mode}。\n主题与目标：${goal}\n已确认的账号/产品事实：${facts || '尚未提供；请标记待确认，不编造经历、数字或功效。'}\n请先匹配定位、人群、场景和内容目的，生成可审阅成稿，检查标题是否兑现、事实是否有据，最后简列实际采用的知识来源。`);

  return <div className="lx-knowledge">
    <header className="lx-k-header">
      <div><div className="lx-eyebrow">Kivo · 国内版</div><h1>让每次创作，都有知识可依</h1><p>整理您的经验，连接选题、标题、文案与复盘。</p></div>
      <button className="btn" disabled={busy} onClick={() => void run(async () => { await request('rebuild', {}); await refresh(); setNotice('知识索引已更新，原始资料保留在原位置。'); })}>{busy ? '整理中…' : '同步本地知识'}</button>
    </header>
    <div className="lx-k-stats">
      {[[status?.files || 0, '已盘点文件'], [status?.methodCards || 0, '结构化方法卡'], [status?.domesticMethods || 0, '国内通用方法'], [status?.learned || 0, '新增学习资料']].map(([n, label]) => <div key={label}><strong>{Number(n).toLocaleString()}</strong><span>{label}</span></div>)}
    </div>
    <nav className="lx-k-tabs" aria-label="知识库功能">
      {([['search', '检索知识'], ['create', '辅助创作与校验'], ['learn', '学习新资料'], ['feedback', '数据反馈与自学习'], ['inventory', '全库整理清单']] as const).map(([value, label]) => <button key={value} className={tab === value ? 'active' : ''} onClick={() => setTab(value)}>{label}</button>)}
    </nav>
    {error && <p className="lx-k-error" role="alert">{error}</p>}{notice && <p className="lx-k-notice" role="status">{notice}</p>}
    {status && !status.ready && <p className="lx-k-note">知识库尚未建立索引，点击“同步本地知识”完成第一次整理。</p>}

    {tab === 'search' && <>
      <div className="lx-k-search"><input aria-label="搜索知识" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="搜索人群定位、开头钩子、卖点、信任、复盘…" /><select aria-label="知识分类" value={category} onChange={(e) => setCategory(e.target.value)}><option value="">全部分类</option>{Object.entries(status?.labels || {}).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></div>
      <div className="lx-k-grid">
        <div className="lx-k-results">{items.length === 0 && <div className="lx-k-empty">没有找到相关资料。可以换一个关键词，或添加新的学习资料。</div>}{items.map((item) => <button className={`lx-k-result ${selected?.id === item.id ? 'selected' : ''}`} key={item.id} onClick={() => setSelected(item)}><div><span className="lx-k-tag">{item.categoryLabel}</span><span className="lx-k-status">{STATUS[item.status] || item.status}</span></div><h3>{item.title}</h3><p>{item.excerpt}</p><small>{item.source}</small></button>)}</div>
        <aside className="lx-k-reader">{selected ? <><span className="lx-k-tag">{STATUS[selected.status] || selected.status}</span><h2>{selected.title}</h2><pre>{selected.body}</pre><details><summary>查看来源与版本</summary><p>{selected.source}</p><p>原文行：{selected.start_line}—{selected.end_line}</p><p>片段指纹：{selected.sha256}</p><p>适用范围：{selected.scope}</p></details><button className="btn btn-primary" onClick={() => { setGoal(`结合「${selected.title}」为当前账号策划内容`); setTab('create'); }}>用于本次创作</button></> : <div className="lx-k-empty"><strong>选择一条知识，查看依据</strong><p>国内方法可用于执行；参考资料保留观点和边界。新学习资料审核后进入创作。</p></div>}</aside>
      </div>
    </>}

    {tab === 'create' && <div className="lx-k-two">
      <section className="lx-k-card"><h2>带着知识写内容</h2><p>知识库会自动进入原有对话与技能工作流，沿用当前账号画像。</p><div className="lx-k-inline"><label>目标平台<select value={platform} onChange={(e) => setPlatform(e.target.value)}>{['小红书', '抖音', '快手', '知乎', 'B站', '视频号', '公众号'].map((p) => <option key={p}>{p}</option>)}</select></label><label>需要产出<select value={mode} onChange={(e) => setMode(e.target.value)}>{['标题与文案', '选题与角度', '短视频脚本', '内容改写', '内容复盘'].map((p) => <option key={p}>{p}</option>)}</select></label></div><label>主题与目标<textarea value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="例如：面向刚开始做自媒体的实体店老板，写一条关于如何找到内容方向的笔记。" rows={5} /></label><label>已确认事实<textarea value={facts} onChange={(e) => setFacts(e.target.value)} placeholder="账号定位、真实经历、产品规格、案例证据、目标受众和承接方式…" rows={5} /></label><button className="btn btn-primary" disabled={!goal.trim() || !status?.ready} onClick={create}>结合知识开始创作 →</button></section>
      <section className="lx-k-card"><h2>交付前再核一遍</h2><p>检查可见的承诺、数字与事实缺口，并可交给原有 AI 工作流深审。</p><label>待检查标题<input value={draftTitle} onChange={(e) => setDraftTitle(e.target.value)} placeholder="粘贴标题" /></label><label>待检查正文<textarea value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="粘贴文案或脚本" rows={10} /></label><div className="lx-k-inline"><button className="btn" disabled={busy || !draft.trim()} onClick={() => void run(async () => { setCheck(await request<Check>('check', { title: draftTitle, content: draft, facts })); })}>检查文本</button><button className="btn" disabled={!draft.trim()} onClick={() => onCreate(`请结合Kivo知识库和当前画像深审以下${platform}内容，核对定位、标题兑现、真实性、论据、表达和行动引导。先列具体问题，再给一版修改稿；不能把缺失证据补写成事实。\n事实：${facts || '未提供'}\n标题：${draftTitle}\n正文：${draft}`)}>AI 深审与修改</button></div>{check && <div className="lx-k-check"><p>标题 {check.titleLength} 字 · 正文 {check.contentLength} 字</p>{check.findings.length ? check.findings.map((f) => <p key={f.kind}>• {f.message}</p>) : <p>本次自动检查未发现命中项。</p>}<small>{check.limitation}</small></div>}</section>
    </div>}

    {tab === 'feedback' && <FeedbackLearning accountName={accountName} onCreate={onCreate} />}

    {tab === 'learn' && <div className="lx-k-two">
      <section className="lx-k-card"><h2>把新经验变成下一次的帮助</h2><p>完整资料可先提炼；您已确认的方法可直接加入并用于后续创作。</p><label>资料标题<input value={learnTitle} onChange={(e) => setLearnTitle(e.target.value)} placeholder="课程、文章或实战复盘名称" /></label><label>来源说明<input value={learnSource} onChange={(e) => setLearnSource(e.target.value)} placeholder="来源链接、作者或实际工作记录" /></label><label>完整文字稿<textarea value={learnText} onChange={(e) => setLearnText(e.target.value)} rows={12} placeholder="粘贴完整文本。视频、音频、PDF可先通过原有技能转写，再导入文字稿。" /></label><label className="lx-direct-apply"><input type="checkbox" checked={activate} onChange={(e) => setActivate(e.target.checked)} />这是我已确认的方法，保存后直接用于后续创作</label><div className="lx-k-inline"><button className="btn btn-primary" disabled={busy || !learnTitle.trim() || learnText.trim().length < 20} onClick={() => void run(async () => { const item = await request<Learned>('learn', { title: learnTitle, text: learnText, source: learnSource, activate }); setReview(item); setMethod(item.method); await refresh(); setLearnText(''); setNotice(item.status === 'approved' ? '方法已保存，可直接用于后续创作。' : '资料已保存，当前为待审核；请核对候选方法。'); })}>{activate ? '保存并直接使用' : '保存并进入学习'}</button><label className="btn lx-k-upload">导入 Markdown / TXT<input type="file" accept=".md,.txt" disabled={busy} onChange={(e) => { const file = e.target.files?.[0]; if (!file) return; void run(async () => { const form = new FormData(); form.append('file', file); const res = await fetch('./api/knowledge/import', { method: 'POST', body: form }); const result = await res.json(); if (!res.ok) throw new Error(result.detail); setReview(result); setMethod(result.method || ''); await refresh(); setNotice('完整文字稿已保存，等待方法审核。'); }); e.target.value = ''; }} /></label></div></section> 
      <section className="lx-k-card"><h2>学习与审核</h2>{learned.length === 0 && <p className="lx-k-empty">尚无新增资料；已有本地知识可在“检索知识”中直接使用。</p>}<div className="lx-k-learning-list">{learned.map((item) => <button key={item.id} onClick={() => { setReview(item); setMethod(item.method); }}><strong>{item.title}</strong><span>{STATUS[item.status] || item.status}</span></button>)}</div>{review && <><h3>{review.title}</h3><details><summary>核对完整来源</summary><p>{review.source || '用户本地导入'}</p><pre>{review.text}</pre></details><button className="btn" onClick={() => onCreate(`请学习以下完整文字稿并提炼供Kivo国内版使用的候选方法，逐项写出触发、适用/不适用、输入、步骤、检查、停止条件与反馈；区分事实、作者观点和未知，并检查与已有知识冲突。只交付候选，不修改活动规则。\n资料：${review.title}\n来源：${review.source}\n完整文字稿：\n${review.text}`)}>AI 提炼候选方法</button><label>审核后的方法<textarea value={method} onChange={(e) => setMethod(e.target.value)} rows={9} placeholder="核对AI提炼结果后填入：适用、输入、步骤、检查、停止条件和来源。" /></label><button className="btn btn-primary" disabled={busy || method.trim().length < 20} onClick={() => void run(async () => { const item = await request<Learned>(`learned/${review.id}/approve`, { sourceHash: review.sourceHash, method }); setReview(item); await refresh(); setNotice('方法已加入国内版创作知识；原始知识库规则未自动改写。'); })}>确认方法并用于后续创作</button></>}</section>
    </div>}

    {tab === 'inventory' && <section className="lx-k-card"><h2>全库资料，各归其位</h2><p>完整盘点保留每个文件的去向。重复镜像共享检索内容，历史项目、原件和维护工具保留清单。</p><div className="lx-k-chips">{Object.entries(status?.decisions || {}).map(([key, count]) => <span key={key}>{DECISIONS[key] || key} · {count}</span>)}</div><div className="lx-k-table"><table><thead><tr><th>资料</th><th>分类</th><th>整理结果</th></tr></thead><tbody>{inventory.map((item) => <tr key={item.path}><td>{item.path}{item.canonical && <small>对应：{item.canonical}</small>}</td><td>{status?.labels[item.category] || item.category}</td><td>{DECISIONS[item.decision] || item.decision}</td></tr>)}</tbody></table></div><div className="lx-k-inline"><button className="btn" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 100))}>上一页</button><span>{offset + 1}—{Math.min(offset + 100, status?.files || 0)} / {status?.files || 0}</span><button className="btn" disabled={offset + 100 >= (status?.files || 0)} onClick={() => setOffset(offset + 100)}>下一页</button></div></section>}
    <footer className="lx-k-footer">知识整理与业务效果分别验证 · 基于 Easel 构建，保留原有七平台工作流</footer>
  </div>;
}
