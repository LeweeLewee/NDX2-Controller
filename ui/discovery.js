// Voice clips and AI requests are explicit actions; neither can start playback.
let brief='', musicPrompt='', suggestions=[], recording=null, recordingTimer=null, voiceStream=null, voiceGeneration=0;
const originalRender=render;
render=function(){
 originalRender();
 if(page==='search')$('.search').insertAdjacentHTML('beforeend','<button type="button" data-voice aria-label="Speak search">Mic</button><button type="button" data-discovery>Ask for music</button>');
 if(page==='discover')$('#view').innerHTML=`<div class="heading"><h2>What are you in the mood for?</h2><button data-new-brief>Start fresh</button></div><form id="discovery-form"><textarea aria-label="Describe your music" maxlength="1000" placeholder="Chilled electronic bass, like Bonobo but a little more upbeat…">${esc(musicPrompt)}</textarea><div class="discovery-actions"><button type="button" data-voice>${recording?'Stop recording':'Speak'}</button><button type="button" data-cancel-voice ${recording?'':'hidden'}>Cancel</button><button class="primary" type="submit" ${config.ai?'':'disabled'}>${brief?'Refine suggestions':'Find my music'}</button><span class="muted" id="voice-state">${recording?'Recording · tap Stop when done':config.ai?'AI discovery ready':'AI service not configured'}</span></div></form><p class="discovery-summary">${esc(brief||'Describe a mood, a sound or an artist. Speak or type, then choose a suggestion to explore.')}</p><div class="suggestions">${suggestions.map((s,i)=>`<button class="suggestion" data-explore="${i}"><b>${esc(s.query)} <span>Explore →</span></b><small>${esc(s.reason)}</small></button>`).join('')}</div><p class="discovery-privacy">Short recordings and requests are sent to OpenAI. Suggestions are AI recommendations; TIDAL availability is checked separately. Nothing plays automatically.</p>`;
 if(page==='search'&&recording){$('[data-voice]').textContent='Stop';$('.search').insertAdjacentHTML('beforeend','<button type="button" data-cancel-voice>Cancel</button>')}
 if(busy)$('#view').querySelectorAll('button').forEach(b=>b.disabled=true);
};
function stopVoice(cancel=false){
 clearTimeout(recordingTimer);
 if(cancel)voiceGeneration++;
 const active=recording;recording=null;
 if(active&&active.state!=='inactive')active.stop();
 voiceStream?.getTracks().forEach(t=>t.stop());voiceStream=null;
}
async function voice(){
 if(busy)return;
 if(recording){stopVoice();return}
 if(!config.ai){notice('Voice transcription needs the AI service enabled.');return}
 if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){notice('Microphone recording is unavailable here. Open this page in a browser with microphone support, or type your request.');return}
 const originPage=page, generation=++voiceGeneration;
 try{
  const stream=await navigator.mediaDevices.getUserMedia({audio:true});
  if(generation!==voiceGeneration||page!==originPage){stream.getTracks().forEach(t=>t.stop());return}
  voiceStream=stream;
  const mime=['audio/webm;codecs=opus','audio/webm','audio/mp4'].find(t=>MediaRecorder.isTypeSupported(t));
  if(!mime)throw Error('This browser has no supported recording format. Please type instead.');
  const recorder=new MediaRecorder(stream,{mimeType:mime}), chunks=[];let total=0;
  recording=recorder;
  recorder.ondataavailable=e=>{total+=e.data.size;if(total>3*1024*1024){stopVoice(true);notice('Recording is too large. Please try a shorter request.');render()}else if(e.data.size)chunks.push(e.data)};
  recorder.onerror=()=>{stopVoice(true);notice('Recording failed. Please type or try again.');render()};
  recorder.onstop=async()=>{
   stream.getTracks().forEach(t=>t.stop());
   if(generation!==voiceGeneration||page!==originPage)return;
   recording=null;clearTimeout(recordingTimer);
   await run(async()=>{notice('Transcribing your request…');const blob=new Blob(chunks,{type:mime});if(!blob.size)throw Error('No audio was recorded.');
    const r=await fetch('/api/transcribe',{method:'POST',headers:{'Content-Type':mime},body:blob});const d=await r.json();if(!r.ok)throw Error(d.error||'Transcription failed');
    if(generation!==voiceGeneration||page!==originPage)return;
    if(originPage==='discover')musicPrompt=d.text;else query=d.text;
    notice('Review the words, then search when ready.');});
  };
  recorder.start(500);recordingTimer=setTimeout(()=>stopVoice(),30000);render();
 }catch(e){stopVoice(true);notice(e.name==='NotAllowedError'?'Microphone access was not granted. You can still type your request.':e.message);render()}
}
document.addEventListener('input',e=>{if(e.target.matches('#discovery-form textarea'))musicPrompt=e.target.value;if(e.target.matches('.search input'))query=e.target.value});
// Cancel capture before the main navigation handler starts an async request.
document.addEventListener('click',e=>{if(e.target.closest('[data-page]'))stopVoice(true)},true);
document.addEventListener('submit',e=>{if(e.target.id!=='discovery-form')return;e.preventDefault();if(recording){notice('Stop recording before searching.');return}run(async()=>{const prompt=musicPrompt.trim();if(!prompt)throw Error('Describe the music you would like.');notice('Finding a few directions for you…');const data=await api('discover',{prompt,context:brief});brief=data.summary;suggestions=data.suggestions;musicPrompt='';notice('Suggestions ready. Explore one or describe a refinement.');})});
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||busy)return;
 if(b.dataset.page||b.hasAttribute('data-discovery'))stopVoice(true);
 if(b.hasAttribute('data-discovery')){page='discover';render()}
 if(b.hasAttribute('data-voice'))voice();
 if(b.hasAttribute('data-cancel-voice')){stopVoice(true);render();notice('Recording discarded.')}
 if(b.hasAttribute('data-new-brief')){stopVoice(true);brief='';musicPrompt='';suggestions=[];render()}
 if(b.dataset.explore!==undefined)run(async()=>{query=suggestions[Number(b.dataset.explore)].query;kind='artists';page='search';if(!config.catalog){results=[];cursor=null;notice('Live TIDAL is not configured. This artist is a suggestion, not a verified catalogue result.');return}await search()});
});
window.addEventListener('pagehide',()=>stopVoice(true));
document.addEventListener('visibilitychange',()=>{if(document.hidden){stopVoice(true);render()}});
render();
