const status=document.getElementById('status');
chrome.storage.local.get('mode').then(s=>document.getElementById('mode').value=s.mode||'original');
document.getElementById('mode').onchange=()=>chrome.storage.local.set({mode:document.getElementById('mode').value});
chrome.runtime.sendMessage({type:'status'}).then(response=>{
  if(!response?.ok)throw Error(response?.error||'Connection failed');
  const tuned=response.data.models.tuned;
  if(tuned){const option=document.querySelector('option[value=tuned]');option.disabled=false;option.textContent='Fine-tuned';}
  status.textContent='Connected. Public article fetch + local inference ready.';
}).catch(error=>status.textContent=error.message);
document.getElementById('enable').onclick=async()=>{
  try{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});await chrome.scripting.executeScript({target:{tabId:tab.id},files:['content.js']});status.textContent='Buttons added to headline links. Scroll your feed and click Spoil.';window.close();}
  catch(error){status.textContent='Cannot read this page: '+error.message;}
};
