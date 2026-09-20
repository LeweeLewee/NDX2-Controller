// Hearts represent TIDAL My Collection, never a second local 'likes' database.
const demoSaved=new Set(demo.filter(i=>i.kind==='albums').map(i=>i.reference));
const savedStates=new Map();
const libraryRender=render, nativeSelect=select;
function isLibraryItem(item){return /^inputs\/tidal\/(tracks|albums|artists|playlists)\/[A-Za-z0-9_-]+$/.test(item?.reference||'')}
function saveButton(item){
 if(!isLibraryItem(item))return '';
 if(!config.library&&(config.live||config.catalog))return '<button data-library="connect">Connect TIDAL to save</button>';
 const saved=config.library?savedStates.get(item.reference):demoSaved.has(item.reference);
 if(saved===undefined)return '<button data-save="refresh">Check saved state</button>';
 const name=item.kind==='tracks'?'Liked track':item.kind==='artists'?'Following artist':'Saved to collection';
 return `<button data-save="${saved?'remove':'add'}" class="${saved?'saved':''}" aria-pressed="${saved}" aria-label="${saved?'Remove from':'Save to'} TIDAL collection">${saved?'♥ '+name:'♡ '+(item.kind==='tracks'?'Like track':item.kind==='artists'?'Follow artist':'Save '+item.kind.slice(0,-1))}</button>`;
}
select=async function(item,more=false){
 const previous=snapshot();
 try{await nativeSelect(item,more)}catch(e){({page,kind,query,results,selected,children,playable,offset,browseRef,cursor,resultId,collectionKind,collectionCursor}=previous);throw e}
 if(['tracks','albums'].includes(selected.kind)){
  selected.related=[];
  if(config.catalog){try{selected.related=(await api('related',{reference:selected.reference})).items}catch(e){notice('Album/artist links unavailable. '+e.message)}}
  else if(!config.live)selected.related=demo.filter(i=>i.kind==='artists'||(selected.kind==='tracks'&&i.kind==='albums'&&i.title===(selected.title==='Unfinished Sympathy'?'Blue Lines':'Mezzanine')));
 }
 if(config.library&&isLibraryItem(selected)){
  savedStates.delete(selected.reference);
  try{savedStates.set(selected.reference,(await api('library_state',{reference:selected.reference})).saved)}catch(e){notice(e.message)}
 }
};
collection=async function(more=false){
 config=await api('config');
 if(config.library){const d=await api('library_page',{kind:collectionKind,cursor:more?collectionCursor:null});results=more?results.concat(d.items):d.items;collectionCursor=d.cursor;d.items.forEach(i=>savedStates.set(i.reference,true))}
 else{results=config.live?(await api('browse')).items:demo.filter(i=>demoSaved.has(i.reference));collectionCursor=null}
 render();
};
render=function(){
 libraryRender();
 if(page==='now'&&config.live&&state.sourceDetail==='tidal')$('.now section').insertAdjacentHTML('beforeend','<button data-current style="margin-top:8px">Track details / save</button>');
 if(page==='now'&&config.live&&config.catalog&&state.sourceDetail==='tidal'){
  const metadata=$('.now section .muted');
  metadata.innerHTML=`<button class="metadata-link" data-current-related="artists">${esc(state.artist||state.artistName||'View artist')}</button><br><button class="metadata-link" data-current-related="albums">${esc(state.album||'View album')}</button>`;
 }
 if(page==='detail'&&selected){
  $('.actions').insertAdjacentHTML('beforeend',saveButton(selected));
  const links=selected.related||[];
  if(links.length)$('.detail section').insertAdjacentHTML('beforeend',`<div class="actions">${links.map((i,n)=>`<button data-related="${n}">${i.kind==='albums'?'Album':'Artist'} · ${esc(i.title)}</button>`).join('')}</div>`);
 }
 if(page==='collection')$('#view').innerHTML=`<div class="heading"><h2>Your collection</h2><button data-refresh="collection">Refresh</button></div>${config.library?`<div class="filters">${['albums','tracks','artists','playlists'].map(k=>`<button data-library-kind="${k}" class="${collectionKind===k?'selected':''}">${k==='tracks'?'Liked tracks':k[0].toUpperCase()+k.slice(1)}</button>`).join('')}</div>`:''}<div class="rows">${rows(results)}</div>${collectionCursor?'<button data-library-more>More saved music</button>':''}<p class="muted library-note">${config.library?'Your TIDAL account collection. Hearts save here.':config.live?'Browsing the collection available to your Naim player. Connect TIDAL to save or remove music.':'Demo collection · hearts are simulated for this session.'}</p>${config.catalog?`<button data-library="${config.library?'disconnect':'connect'}">${config.library?'Disconnect library':'Connect TIDAL library'}</button>`:''}`;
 if(busy)$('#view').querySelectorAll('button').forEach(b=>b.disabled=true);
};
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b||!b.matches('[data-library],[data-save],[data-library-kind],[data-library-more],[data-current],[data-related],[data-current-related]'))return;
 run(async()=>{
  if(b.dataset.library==='connect'){const d=await api('library_connect');const url=new URL(d.url);if(url.origin!=='https://login.tidal.com'||url.pathname!=='/authorize')throw Error('Invalid TIDAL sign-in URL');window.location.assign(d.url);return}
  if(b.dataset.library==='disconnect'){notice((await api('library_disconnect')).message);savedStates.clear();await collection();return}
  if(b.dataset.libraryKind){collectionKind=b.dataset.libraryKind;pendingScroll=0;await collection();return}
  if(b.hasAttribute('data-library-more')){await collection(true);return}
  if(b.dataset.related!==undefined){await select(selected.related[Number(b.dataset.related)]);return}
  if(b.dataset.currentRelated){
   const current=await api('current_item');
   const items=(await api('related',{reference:current.reference})).items.filter(i=>i.kind===b.dataset.currentRelated);
   if(!items.length)throw Error('No '+(b.dataset.currentRelated==='albums'?'album':'artist')+' link is available for this track.');
   if(items.length===1)await select(items[0]);
   else{goPage('detail');selected={title:b.dataset.currentRelated==='artists'?'Choose artist':'Choose album',kind:b.dataset.currentRelated};children=items;playable=false;offset=0;browseRef='';render()}
   return;
  }
  if(b.hasAttribute('data-current')){await select(await api('current_item'));return}
  if(b.dataset.save){
   const reference=selected.reference;
   if(config.library){
    savedStates.delete(reference);
    const data=await api(b.dataset.save==='refresh'?'library_state':'library_save',b.dataset.save==='refresh'?{reference,fresh:true}:{reference,saved:b.dataset.save==='add'});
    savedStates.set(reference,data.saved);if(!data.saved)history.forEach(h=>{if(h.page==='collection')h.results=h.results.filter(i=>i.reference!==reference)});if(data.message)notice(data.message);
   }else if(!config.live&&!config.catalog){if(demoSaved.has(reference))demoSaved.delete(reference);else demoSaved.add(reference);notice('Demo collection updated · no TIDAL account changes.')}
  }
 });
});
render();
