const API = 'http://127.0.0.1:8765';
let pairingToken = '';
async function localRequest(path, body, token) {
  let response;
  try {
    response = await fetch(API + path, {method:'POST',headers:{'Content-Type':'application/json',...(token ? {'X-Spoiler-Token':token} : {})},body:JSON.stringify(body)});
  } catch {
    throw Error('Cannot reach the local server. Start it at http://127.0.0.1:8765 and try again.');
  }
  const data = await response.json();
  if(!response.ok) {
    const error = Error(data.error || `Local request failed (HTTP ${response.status})`);
    error.status = response.status;
    throw error;
  }
  return data;
}
async function pair() {
  const data = await localRequest('/api/pair', {});
  pairingToken = data.token;
  return data;
}
async function spoil(message) {
  if (!pairingToken) await pair();
  const {mode = 'original'} = await chrome.storage.local.get('mode');
  const visible = message.type === 'spoil-visible';
  const path = visible ? '/api/spoil' : '/api/spoil-link';
  const body = visible ? {headline:message.headline,article:message.article,mode} : {url:message.url,headline:message.headline,snippet:message.snippet||'',mode};
  let data;
  try {data = await localRequest(path, body, pairingToken);}
  catch(error) {
    // This is our API's pairing denial, not a publisher's HTTP 403 (reported as 422).
    if(error.status !== 403) throw error;
    await pair();
    data = await localRequest(path, body, pairingToken);
  }
  return data;
}
chrome.runtime.onMessage.addListener((message,sender,respond) => {
  if(!['spoil-link','spoil-visible','status'].includes(message?.type)) return;
  const task = message.type === 'status' ? pair() : spoil(message);
  task.then(data=>respond({ok:true,data})).catch(error=>respond({ok:false,error:error.message}));
  return true;
});
