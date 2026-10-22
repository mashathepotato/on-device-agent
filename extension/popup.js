const status=document.getElementById('status');
chrome.storage.local.get('mode').then(s=>document.getElementById('mode').value=s.mode||'original');
document.getElementById('mode').onchange=()=>chrome.storage.local.set({mode:document.getElementById('mode').value});
chrome.runtime.sendMessage({type:'status'}).then(response=>{
  if(!response?.ok)throw Error(response?.error||'Connection failed');
  const tuned=response.data.models.tuned;
  chrome.storage.local.get('mode').then(s=>{if(!s.mode)document.getElementById('mode').value=response.data.default_mode||'original';});
  if(tuned){const option=document.querySelector('option[value=tuned]');option.disabled=false;option.textContent='Fine-tuned';}
  status.textContent='Connected. Public article fetch + local inference ready.';
}).catch(error=>status.textContent=error.message);
document.getElementById('enable').onclick=async()=>{
  try{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await chrome.scripting.executeScript({target:{tabId:tab.id},files:['content.js']});status.textContent='Buttons added to headline links. Scroll your feed and click Spoil.';window.close();}
  catch(error){status.textContent='Cannot read this page: '+error.message;}
};
document.getElementById('read').onclick=async()=>{
  const button=document.getElementById('read');button.disabled=true;status.textContent='Reading visible article text locally…';
  try {
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!/^https?:\/\//.test(tab.url || '')) throw Error('Open a normal article webpage first.');
    const [{result:page}]=await chrome.scripting.executeScript({target:{tabId:tab.id},func:()=>{
      const source=document.querySelector('article') || document.querySelector('main') || document.body;
      return {type:'spoil-visible',headline:document.querySelector('h1')?.innerText || document.title,article:source.innerText.slice(0,16001)};
    }});
    const response=await chrome.runtime.sendMessage(page);
    if(!response?.ok) throw Error(response?.error || 'Could not read this article.');
    const data=response.data;const value=data.click_value;status.replaceChildren();
    if(value){const badge=document.createElement('strong');badge.textContent=`${value.score}/100 · ${value.label}`;badge.style.color=({green:'#14532d',amber:'#713f12',red:'#991b1b'})[value.band]||'#17392e';status.append(badge);}
    const answer=document.createElement('p');answer.textContent=data.summary||data.spoiler||'No concise answer available.';status.append(answer);
  } catch(error){status.textContent=error.message;}
  finally{button.disabled=false;}
};
