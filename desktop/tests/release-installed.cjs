// Actual installed executable, clean profile under real AppData. No copied user index or credentials.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const version=require('../package.json').version;
const executable=process.argv[2];
if(!executable || !fs.existsSync(executable)) throw new Error('Provide installed Kivo.exe');
const standard=process.argv.includes('--standard');
const dataArgument=process.argv.indexOf('--data-root');
const user=dataArgument>=0?path.resolve(process.argv[dataArgument+1]):standard?`F:/资料库/03_项目与素材/lingxi-platform/release-${version}-clean-profile`:path.join(process.env.APPDATA,`kivo-release-${version}-validation`);
const qa=path.resolve(__dirname,`../../.test-tmp/release-${version}`);
const resume=process.argv.includes('--resume');
const resumeStart=process.argv.includes('--resume-start');
const upgrade=process.argv.includes('--upgrade');
if(fs.existsSync(user)&&!resume&&!resumeStart&&!upgrade) throw new Error('Clean profile already exists; inspect before reusing');
if(upgrade&&!fs.existsSync(path.join(user,'installed-platform.json'))) throw new Error('Upgrade test requires an installed previous profile');
fs.mkdirSync(user,{recursive:true}); fs.mkdirSync(qa,{recursive:true});
const env={...process.env};
for(const key of Object.keys(env)) if(/API_KEY|TOKEN|SECRET|PASSWORD|ELECTRON_RUN_AS_NODE|LINGXI_|KIVO_|EASEL_|OPENAI_|ANTHROPIC_|PYTHONPATH|PYTHONHOME/.test(key)) delete env[key];
Object.assign(env,{LINGXI_DESKTOP_TEST:'1',LINGXI_DESKTOP_TEST_DATA:user,LINGXI_KNOWLEDGE_ROOT:path.join(user,'knowledge-vault')});
async function run(label){
  await new Promise((resolve,reject)=>{
    const child=spawn(executable,[],{env,windowsHide:true,stdio:'ignore'});
    const timer=setTimeout(()=>{spawn('taskkill',['/PID',String(child.pid),'/T','/F'],{windowsHide:true});reject(new Error('Installed smoke timeout'));},1200000);
    child.once('error',e=>{clearTimeout(timer);reject(e)});
    child.once('exit',code=>{clearTimeout(timer);code===0?resolve():reject(new Error('Smoke failed '+code+'; '+user))});
  });
  record(label);
}
function record(label){
  if(standard)label+='-standard';
  const result=JSON.parse(fs.readFileSync(path.join(user,'desktop-smoke.json')));
  if(result.version!==version||!result.packaged||!result.backendReady||result.skillCount!==114||!result.noPrivilegedBridge) throw new Error('Smoke acceptance failed');
  if(!fs.existsSync(path.join(user,'knowledge-vault/knowledge-base.json'))) throw new Error('Bundled local knowledge missing');
  if(!fs.existsSync(path.join(user,'knowledge/knowledge.sqlite3'))) throw new Error('Local knowledge index missing');
  const keyFile=fs.readFileSync(path.join(user,'model.env'),'utf8');
  if(keyFile.split(/\r?\n/).some(x=>x.trim()&&!x.trim().startsWith('#'))) throw new Error('Expected empty provider settings');
  fs.copyFileSync(path.join(user,'desktop-smoke.png'),path.join(qa,label+'.png'));
  fs.writeFileSync(path.join(qa,label+'.json'),JSON.stringify(result,null,2));
  console.log(label+': '+JSON.stringify(result));
}
(async()=>{
 if(resume){
   const deadline=Date.now()+1200000;
   while(!fs.existsSync(path.join(user,'desktop-smoke.json'))){
     if(fs.existsSync(path.join(user,'desktop-error.txt'))||Date.now()>deadline)throw Error('Pending clean startup failed');
     await new Promise(r=>setTimeout(r,2000));
   }
   await new Promise(r=>setTimeout(r,3000));record('installed-clean');
 }else await run(upgrade?'installed-upgrade':'installed-clean');
 await run('installed-warm');
})().catch(e=>{console.error(e);process.exitCode=1});
