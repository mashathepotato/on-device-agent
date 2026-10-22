const result = document.getElementById('result');
document.getElementById('origin').textContent = chrome.runtime.getURL('').replace(/\/$/, '');
fetch('http://127.0.0.1:8765/api/status').then(r=>r.json()).then(s=>{if(s.models.tuned){const option=document.querySelector('option[value=tuned]');option.disabled=false;option.textContent='Fine-tuned';}}).catch(()=>{});
chrome.storage.local.get('token').then(s => document.getElementById('token').value = s.token || '');
document.getElementById('save').onclick = () => chrome.storage.local.set({token:document.getElementById('token').value});
document.getElementById('reveal').onclick = async () => {
  const button = document.getElementById('reveal'); button.disabled = true; result.textContent = 'Reading locally…';
  try {
    const [tab] = await chrome.tabs.query({active:true,currentWindow:true});
    const [{result:page}] = await chrome.scripting.executeScript({target:{tabId:tab.id},func:() => {
      const article = document.querySelector('article') || document.querySelector('main') || document.body;
      return {headline:document.querySelector('h1')?.innerText || document.title,article:article.innerText.slice(0,100000),mode:'original'};
    }});
    page.mode=document.getElementById('mode').value;
    const response = await fetch('http://127.0.0.1:8765/api/spoil',{method:'POST',headers:{'Content-Type':'application/json','X-Spoiler-Token':document.getElementById('token').value},body:JSON.stringify(page)});
    const data = await response.json(); if(!response.ok) throw Error(data.error);
    result.textContent = `${data.spoiler || data.status}\n\n${data.evidence ? '“'+data.evidence+'”' : ''}\n\n${data.request_ms} ms request · ${data.cache_hit ? 'cache hit' : 'local inference'}\n${data.truncated ? 'PARTIAL ARTICLE: first 16,000 characters only.\n' : ''}${data.status}`;
  } catch(error) { result.textContent = error.message + '\nCheck server, extension origin, and pairing token. Restricted browser pages cannot be read.'; }
  finally {button.disabled = false;}
};
