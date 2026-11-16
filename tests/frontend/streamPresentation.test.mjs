import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { runInNewContext } from 'node:vm';
import { test } from 'node:test';

const require = createRequire(new URL('../../web/frontend/package.json', import.meta.url));
const ts = require('typescript');
const options = { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX };
const helpers = {};
runInNewContext(ts.transpileModule(readFileSync(new URL('../../web/frontend/src/lib/streamPresentation.ts', import.meta.url), 'utf8'), {
  compilerOptions: options,
}).outputText, { exports: helpers });
const app = readFileSync(new URL('../../web/frontend/src/App.tsx', import.meta.url), 'utf8');
const appAst = ts.createSourceFile('App.tsx', app, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
let pump, sync;
function find(node) {
  if (ts.isVariableDeclaration(node) && node.name.getText(appAst) === 'pumpTyping') pump = node.getText(appAst);
  if (ts.isVariableDeclaration(node) && node.name.getText(appAst) === 'syncStreamPresentation') sync = node.getText(appAst);
  ts.forEachChild(node, find);
}
find(appAst);

function setup({ page = 'chat', active = 'session', visibility = 'visible', text = '完整回复🙂'.repeat(40) } = {}) {
  const owner = { content: '', thinking: '' }, typingBuf = { current: { session: text } };
  const presentationDirty = { current: new Set() };
  const streamAcc = { current: { session: owner } };
  let updates = 0, stopped = 0, state = { session: { content: '' } };
  const currentPageRef = { current: page }, activeIdRef = { current: active };
  const pumpTyping = runInNewContext(ts.transpileModule(`const ${pump}; pumpTyping;`, { compilerOptions: options }).outputText, {
    typingBuf, presentationDirty, streamAcc, currentPageRef, activeIdRef, document: { visibilityState: visibility },
    streamFrameLength: helpers.streamFrameLength,
    clearTyping() { stopped++; },
    setStreams(update) { updates++; state = update(state); },
  });
  return { pump: () => pumpTyping('session'), owner, typingBuf, presentationDirty, currentPageRef, activeIdRef,
    get updates() { return updates; }, get stopped() { return stopped; }, get state() { return state; } };
}

test('visible streaming preserves complete Unicode text with substantially fewer UI updates', () => {
  const text = '## 验收🙂\n这是一段较长的回复。\n'.repeat(200);
  const h = setup({ text });
  let previous = '';
  while (h.typingBuf.current.session) {
    h.pump();
    assert.ok(h.owner.content.startsWith(previous));
    assert.ok(!/[\uD800-\uDBFF]$/.test(h.owner.content), 'no half surrogate visible at frame end');
    previous = h.owner.content;
  }
  assert.equal(h.owner.content, text);
  assert.equal(h.state.session.content, text);
  assert.ok(h.updates < 50, `a batched reply should not need hundreds of root renders: ${h.updates}`);
  let oldBuffer = text, oldFrames = 0;
  while (oldBuffer) { oldBuffer = oldBuffer.slice(Math.max(1, Math.floor(oldBuffer.length / 80))); oldFrames++; }
  assert.ok(h.updates < oldFrames / 5);
  assert.ok(h.updates * helpers.STREAM_FRAME_MS < oldFrames * 12 / 2, 'display drains faster as well as rendering less');
});

for (const background of [{ page: 'dashboard' }, { active: 'another-session' }, { visibility: 'hidden' }]) {
  test(`background stream retains output without repainting another view: ${JSON.stringify(background)}`, () => {
    const h = setup({ ...background, text: '后台完整回复🙂' });
    h.pump();
    assert.equal(h.owner.content, '后台完整回复🙂');
    assert.equal(h.typingBuf.current.session, '');
    assert.equal(h.updates, 0);
    h.pump();
    assert.equal(h.stopped, 1);
  });
}

test('an empty stream frame does not schedule a root render', () => {
  const h = setup({ text: '' });
  h.pump();
  assert.equal(h.updates, 0);
  assert.equal(h.stopped, 1);
});

test('thinking-only updates coalesce into one display frame and retain the latest text', () => {
  const h = setup({ text: '' });
  for (let i = 0; i < 100; i++) { h.owner.thinking += '思考'; h.presentationDirty.current.add('session'); }
  assert.equal(h.updates, 0);
  h.pump();
  assert.equal(h.updates, 1);
  assert.equal(h.state.session.thinking, '思考'.repeat(100));
  assert.equal(h.state.session.stillWorking, undefined);
});

test('returning to a conversation synchronizes background text and thinking even without another token', () => {
  const owner = { content: '后台结果', thinking: '后台思考' };
  let state = { session: { content: '旧结果', thinking: '' } };
  const synchronize = runInNewContext(ts.transpileModule(`const ${sync}; syncStreamPresentation;`, { compilerOptions: options }).outputText, {
    useCallback: fn => fn, streamAcc: { current: { session: owner } }, flushTyping() {},
    setStreams(update) { state = update(state); },
  });
  synchronize('session');
  assert.equal(state.session.content, owner.content);
  assert.equal(state.session.thinking, owner.thinking);
  const unchanged = state;
  synchronize('session');
  assert.equal(state, unchanged, 'unchanged snapshots should not re-render the page');
});

const chat = readFileSync(new URL('../../web/frontend/src/components/ChatPage.tsx', import.meta.url), 'utf8');
const chatAst = ts.createSourceFile('ChatPage.tsx', chat, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const history = chatAst.statements.find(node => ts.isVariableStatement(node)
  && node.declarationList.declarations.some(d => d.name.getText(chatAst) === 'ChatHistory'));
const Bubble = () => null, Questions = () => null;
const historyRenderer = runInNewContext(ts.transpileModule(`${history.getText(chatAst)}; ChatHistory;`, { compilerOptions: options }).outputText, {
  exports: {}, require, memo: component => component, MessageBubble: Bubble, QuestionCards: Questions,
  navigator: { clipboard: { writeText: () => Promise.resolve() } },
});

function children(node) { return (Array.isArray(node.props.children) ? node.props.children : [node.props.children]).filter(Boolean); }
test('completed history retains attachments for retry and question cards while streaming', () => {
  const retried = [], questions = [{ id: 'question' }];
  const user = { role: 'user', content: '问题', attachments: [{ path: 'outputs/a.png' }], agentContent: '旧指令' };
  const messages = [user, { role: 'assistant', content: '回答', questions }];
  const props = { messages, onResend: (...args) => retried.push(args), onQuestionAnswered() {}, onQuestionClosed() {} };
  const final = historyRenderer({ ...props, isStreaming: false });
  const first = children(final[0]).find(child => child.type === Bubble);
  const last = children(final[1]).find(child => child.type === Bubble);
  assert.equal(first.props.actions.onRetry, undefined);
  assert.equal(last.props.actions.canModify, true);
  last.props.actions.onRetry();
  assert.deepEqual(retried[0], [0, '问题', user.attachments, '旧指令']);
  const running = historyRenderer({ ...props, isStreaming: true });
  assert.equal(children(running[1]).find(child => child.type === Bubble).props.actions.canModify, false);
  const card = children(running[1]).find(child => child.type === Questions);
  assert.equal(card.props.questions, questions);
  assert.equal(card.props.onDone, props.onQuestionAnswered);
});

test('attachment-only final user message still passes structured retry data', () => {
  const retried = [];
  const refs = [{ path: 'outputs/large.mp4' }];
  const tree = historyRenderer({ messages: [{ role: 'user', content: '', attachments: refs }],
    isStreaming: false, onResend: (...args) => retried.push(args) });
  children(tree[0]).find(child => child.type === Bubble).props.actions.onRetry();
  assert.deepEqual(retried[0], [0, '', refs, undefined]);
});
