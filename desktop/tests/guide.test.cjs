const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
test('offline beginner guide is included and all table-of-contents targets exist',()=>{
  const root=path.resolve(__dirname,'..'),s=fs.readFileSync(path.join(root,'user-guide.html'),'utf8');
  for(let i=1;i<=11;i++) assert.ok(s.includes(`id="section-${i}"`)&&s.includes(`href="#section-${i}"`));
  assert.ok(!/<script|<img[^>]+https?:|<link[^>]+https?:/.test(s));
  assert.ok(JSON.parse(fs.readFileSync(path.join(root,'package.json'))).build.files.includes('user-guide.html'));
  assert.ok(fs.readFileSync(path.join(root,'main.cjs'),'utf8').includes("label: '新手使用指南'"));
});
