import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { test } from 'node:test';

const require = createRequire(new URL('../../web/frontend/package.json', import.meta.url));
const { build } = await import(pathToFileURL(require.resolve('vite')).href);
const result = await build({ root: fileURLToPath(new URL('../../web/frontend', import.meta.url)),
  build: { write: false, emptyOutDir: false }, logLevel: 'silent' });
const output = (Array.isArray(result) ? result : [result]).flatMap(bundle => bundle.output);
const html = output.find(asset => asset.fileName === 'index.html').source;
const linkedStyles = [...html.matchAll(/<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"/g)].map(match => match[1].replace(/^\.\//, ''));
const eagerCss = output.filter(asset => linkedStyles.includes(asset.fileName)).map(asset => asset.source).join('\n');

test('production HTML eagerly loads shell logo and shared controls before any page chunk', () => {
  assert.ok(linkedStyles.length > 0, 'initial page must link its styles');
  for (const selector of ['.sidebar{', '.kivo-logo{', '.lingxi-logo{', '.settings-feedback{', '.board .cell-result{', '.lx-feedback-metrics{', '.lx-feedback-row{']) {
    assert.ok(eagerCss.includes(selector), `missing initial CSS: ${selector}`);
  }
  assert.match(eagerCss, /\.kivo-logo\{[^}]*width:36px/);
  assert.match(eagerCss, /\.kivo-logo\{[^}]*height:36px/);
  assert.ok(!eagerCss.includes('.lx-knowledge{'), 'knowledge page styles should retain lazy loading');
});

test('sidebar logo has intrinsic dimensions before CSS arrives', () => {
  const ts = require('typescript');
  const source = readFileSync(new URL('../../web/frontend/src/components/Sidebar.tsx', import.meta.url), 'utf8');
  const ast = ts.createSourceFile('Sidebar.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  let logo;
  function visit(node) {
    if (ts.isJsxSelfClosingElement(node) && node.tagName.getText(ast) === 'img'
      && node.attributes.properties.some(prop => ts.isJsxAttribute(prop) && prop.name.getText(ast) === 'className' && prop.initializer?.text === 'kivo-logo')) logo = node;
    ts.forEachChild(node, visit);
  }
  visit(ast);
  assert.ok(logo);
  for (const name of ['width', 'height']) {
    assert.equal(logo.attributes.properties.find(prop => ts.isJsxAttribute(prop) && prop.name.getText(ast) === name)?.initializer?.expression?.getText(ast), '36');
  }
});
