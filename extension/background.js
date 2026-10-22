const API = 'http://127.0.0.1:8765';
let pairingToken = '';
async function pair() {
  const response = await fetch(API + '/api/pair', {method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Cannot pair with local server');
  pairingToken = data.token;
  return data;
}
async function spoil(message) {
  if (!pairingToken) await pair();
  const {mode = 'original'} = await chrome.storage.local.get('mode');
  let response = await fetch(API + '/api/spoil-link', {method:'POST',headers:{'Content-Type':'application/json','X-Spoiler-Token':pairingToken},body:JSON.stringify({url:message.url,headline:message.headline,mode})});
  if(response.status === 403) {await pair();response = await fetch(API + '/api/spoil-link',{method:'POST',headers:{'Content-Type':'application/json','X-Spoiler-Token':pairingToken},body:JSON.stringify({url:message.url,headline:message.headline,mode})});}
  const data = await response.json();
  if(!response.ok) throw Error(data.error || 'Article request failed');
  return data;
}
chrome.runtime.onMessage.addListener((message,sender,respond) => {
  if(!['spoil-link','status'].includes(message?.type)) return;
  const task = message.type === 'status' ? pair() : spoil(message);
  task.then(data=>respond({ok:true,data})).catch(error=>respond({ok:false,error:error.message + ' · Check that the local server is running.'}));
  return true;
});
