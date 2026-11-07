const fs = require('node:fs');
const path = require('node:path');
const version = require('./package.json').version;
(async () => {
  const { marked } = await import('../web/frontend/node_modules/marked/lib/marked.esm.js');
  const source = fs.readFileSync(path.join(__dirname, '../docs/Kivo-新手使用指南.md'), 'utf8');
  let i = 0;
  const entries = [];
  const body = marked.parse(source.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')).replace(/<h2>(.*?)<\/h2>/g, (_, title) => {
    const id = `section-${++i}`; entries.push(`<a href="#${id}">${title}</a>`); return `<h2 id="${id}">${title}</h2>`;
  });
  const html = `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:"><title>Kivo 新手使用指南 · ${version}</title><style>
  :root{font-family:"Microsoft YaHei",system-ui,sans-serif;color:#23313c;background:#f4f6f8;font-size:16px;line-height:1.85}*{box-sizing:border-box}body{margin:0}header{padding:28px 5vw;background:#17232f;color:white}header b{font-size:28px}header span{display:block;color:#b8c9d4}main{max-width:1220px;margin:auto;display:grid;grid-template-columns:250px minmax(0,1fr);gap:28px;padding:28px}nav{position:sticky;top:20px;align-self:start;background:white;border:1px solid #dae1e6;border-radius:12px;padding:18px;font-size:14px}nav a{display:block;padding:7px 0;text-decoration:none;color:#215f6b}article{min-width:0;background:#fff;padding:32px 40px;border-radius:12px;border:1px solid #dae1e6}h1{font-size:28px;line-height:1.4}h2,h3{font-size:20px;line-height:1.55;scroll-margin-top:20px}h2{border-top:1px solid #dae1e6;margin-top:36px;padding-top:24px}h3{color:#215f6b}p,li{overflow-wrap:anywhere}blockquote{background:#edf8f7;border-left:4px solid #248c88;margin:20px 0;padding:10px 20px}table{border-collapse:collapse;width:100%;font-size:14px;table-layout:fixed}th,td{border:1px solid #dce4e8;text-align:left;vertical-align:top;padding:10px;overflow-wrap:anywhere}th{background:#edf2f5}li{margin:8px 0}a{color:#146c76}code{background:#f2f4f6;padding:2px 5px}strong{font-weight:700}@media(max-width:850px){main{display:block;padding:16px}nav{position:static;margin-bottom:16px}article{padding:20px}}@media print{header,nav{display:none}main{display:block;padding:0;max-width:none}article{border:0;padding:0}body{background:white}h2,h3{break-after:avoid}tr,blockquote{break-inside:avoid}table{font-size:12px}a{color:inherit}}
  </style><header><b>Kivo · 从安装到第一份作品</b><span>新手使用指南 · 国内版 ${version} · 可离线阅读 / Ctrl+P 打印</span></header><main><nav aria-label="目录">${entries.join('')}</nav><article>${body}</article></main></html>`;
  fs.writeFileSync(path.join(__dirname, 'user-guide.html'), html);
  console.log(JSON.stringify({sections:i,bytes:Buffer.byteLength(html)}));
})().catch(e=>{console.error(e);process.exitCode=1});
