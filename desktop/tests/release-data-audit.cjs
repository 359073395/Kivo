const fs=require('node:fs'),path=require('node:path'),{sha}=require('../runtime.cjs');
const root=path.join(process.env.APPDATA,'kivo-desktop');
const report=path.resolve(__dirname,`../../.test-tmp/release-${require('../package.json').version}/protected-data.json`);
const hashes={};
function scan(file){if(!fs.existsSync(file))return;const st=fs.lstatSync(file);if(st.isSymbolicLink())throw new Error('Unexpected linked user file');if(st.isDirectory())for(const n of fs.readdirSync(file))scan(path.join(file,n));else hashes[path.relative(root,file)]=sha(fs.readFileSync(file));}
for(const p of ['model.env','desktop-settings.json','platform/.env','platform/outputs','platform/profiles','knowledge'])scan(path.join(root,p));
if(process.argv.includes('--before')){if(fs.existsSync(report))throw new Error('Audit evidence exists');fs.mkdirSync(path.dirname(report),{recursive:true});fs.writeFileSync(report,JSON.stringify(hashes,null,2));console.log('Recorded '+Object.keys(hashes).length+' protected files');}
else{const old=JSON.parse(fs.readFileSync(report));const changed=Object.keys(old).filter(p=>old[p]!==hashes[p]);console.log(JSON.stringify({checked:Object.keys(old).length,changed}));if(changed.length)process.exitCode=1;}
