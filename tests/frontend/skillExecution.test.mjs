import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { runInNewContext } from 'node:vm';
import { test } from 'node:test';

const require = createRequire(new URL('../../web/frontend/package.json', import.meta.url));
const ts = require('typescript');

test('技能详情通过交互式对话入口执行并关闭抽屉', () => {
  const source = readFileSync(new URL('../../web/frontend/src/components/SkillDrawer.tsx', import.meta.url), 'utf8');
  const { outputText } = ts.transpileModule(source, { compilerOptions: {
    module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX,
  } });
  const values = [null, '', {}, false, '', '  验证本地视频制作  '];
  let state = 0;
  const modules = {
    react: { useState: () => [values[state++], () => {}], useEffect() {},
      useMemo: callback => callback(), useRef: value => ({ current: value }) },
    'react/jsx-runtime': { jsx: (type, props) => ({ type, props }), jsxs: (type, props) => ({ type, props }) },
    '../lib/api': {},
    '../lib/sanitize': { renderMarkdown: value => value },
    '../lib/skillDisplayNames': { displayName: value => value },
    './SettingsSelect': {},
  };
  const exports = {};
  runInNewContext(outputText, { exports, require: name => modules[name] });
  const calls = [];
  const tree = exports.default({ skillName: 'video-production', onRun: (...args) => calls.push(args),
    onClose: () => calls.push('closed'), onConfigured() {} });
  function nodes(node) {
    if (Array.isArray(node)) return node.flatMap(nodes);
    if (!node || typeof node !== 'object') return [];
    return [node, ...nodes(node.props?.children)];
  }
  const execute = nodes(tree).find(node => node.type === 'button' && node.props.children === '在对话中执行');
  assert.ok(execute);
  assert.ok(!execute.props.disabled);
  execute.props.onClick();
  assert.deepEqual(calls, [['video-production', '验证本地视频制作'], 'closed']);
});
