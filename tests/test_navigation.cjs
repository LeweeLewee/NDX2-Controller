// Run: node --test tests/test_navigation.cjs
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
function controller(){
 const view={scrollTop:0,querySelectorAll:()=>[]};
 const document={querySelector:()=>view,querySelectorAll:()=>[],addEventListener:()=>{}};
 const context=vm.createContext({document,setTimeout,clearTimeout,URL,window:{addEventListener:()=>{}},navigator:{}});
 const html=fs.readFileSync(path.join(__dirname,'../ui/index.html'),'utf8');
 vm.runInContext(html.split('<script>')[1].split('</script>')[0].split('start();let polling')[0],context);
 vm.runInContext('render=()=>{};notice=()=>{};',context);
 return {context,view,run:s=>vm.runInContext(s,context)};
}
test('Back restores query, filter, pagination and scroll after nested navigation',()=>{
 const c=controller();
 c.run("page='search';query='Bonobo';kind='albums';results=[{title:'Migration'}];cursor='next';resultId='ranked';offset=40");
 c.view.scrollTop=310;
 c.run("goPage('discover');goPage('search');query='Four Tet';kind='artists';results=[];cursor=null;goBack()");
 assert.equal(c.run('page'),'discover');
 c.run('goBack();applyScroll()');
 assert.equal(c.run('page'),'search');assert.equal(c.run('query'),'Bonobo');assert.equal(c.run('kind'),'albums');
 assert.equal(c.run('results[0].title'),'Migration');assert.equal(c.run('cursor'),'next');assert.equal(c.run('resultId'),'ranked');
 assert.equal(c.view.scrollTop,310);
});
test('failed native browse retains the previous selection and results',async()=>{
 const c=controller();
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../ui/library.js'),'utf8'),c.context);
 c.run("page='search';query='Rhye';results=[{title:'Blood'}];config.live=true;api=async()=>{throw Error('offline')}");
 await assert.rejects(c.run("select({reference:'inputs/tidal/albums/123',kind:'albums',title:'Blood'})"),/offline/);
 assert.equal(c.run('page'),'search');assert.equal(c.run('query'),'Rhye');assert.equal(c.run('results[0].title'),'Blood');
 assert.equal(c.run('selected'),null);assert.equal(c.run('history.length'),0);
});
test('unknown saved state never displays an empty or filled heart',()=>{
 const c=controller();
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../ui/library.js'),'utf8'),c.context);
 c.run("config.library=true;selected={reference:'inputs/tidal/albums/123',kind:'albums'}");
 assert.match(c.run('saveButton(selected)'),/Check saved state/);
 c.run("savedStates.set(selected.reference,true)");
 assert.match(c.run('saveButton(selected)'),/aria-pressed="true"/);
 c.run("savedStates.set(selected.reference,false)");
 assert.match(c.run('saveButton(selected)'),/aria-pressed="false"/);
});
test('album result hearts are separate controls with the correct row identity',()=>{
 const c=controller();
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../ui/library.js'),'utf8'),c.context);
 c.run("page='search';kind='albums';config.library=true;results=[{kind:'albums',reference:'inputs/tidal/albums/1',title:'First'},{kind:'albums',reference:'inputs/tidal/albums/2',title:'Second'}];savedStates.set(results[0].reference,true);savedStates.set(results[1].reference,false)");
 const html=c.run('rows(results)');
 assert.match(html,/data-album-save="0" data-intent="remove"/);
 assert.match(html,/data-album-save="1" data-intent="add"/);
 assert.match(html,/class="number">02/);
 assert.match(html,/<\/button><button class="album-heart/);
});
test('saving a result targets that album and preserves the current detail selection',async()=>{
 const c=controller();
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../ui/library.js'),'utf8'),c.context);
 c.run("config.library=true;selected={reference:'inputs/tidal/tracks/9'};calls=[];api=async(action,args)=>{calls.push({action,args});return {saved:args.saved}};");
 await c.run("changeSaved({reference:'inputs/tidal/albums/2'},'add')");
 assert.equal(c.run('calls[0].args.reference'),'inputs/tidal/albums/2');
 assert.equal(c.run('calls[0].args.saved'),true);
 assert.equal(c.run('selected.reference'),'inputs/tidal/tracks/9');
 assert.equal(c.run("savedStates.get('inputs/tidal/albums/2')"),true);
 await c.run("changeSaved({reference:'inputs/tidal/albums/2'},'remove')");
 assert.equal(c.run('calls[1].args.saved'),false);
});
