const $ = id => document.getElementById(id);
let models={};
fetch('/api/status').then(r=>r.json()).then(status=>{
  models=status.models;
  $('mode').value=status.default_mode||'original';
  $('connection').textContent='Local LFM2.5 · article links fetched on demand';
  if(models.tuned){const tuned=$('mode').querySelector('[value=tuned]');tuned.disabled=false;tuned.textContent='Fine-tuned';const compare=$('mode').querySelector('[value=compare]');compare.disabled=false;compare.textContent='Compare both';}
}).catch(()=>$('connection').textContent='Local server unavailable');
function render(target,data,label){
  const section=document.createElement('section');
  if(label){const name=document.createElement('p');name.className='model-label';name.textContent=label;section.append(name);}
  if(data.click_value){
    const value=data.click_value;
    const badge=document.createElement('div');badge.className='click-score '+value.band;badge.textContent=`${value.score}/100 · ${value.label}`;section.append(badge);
  }
  const answer=document.createElement('p');answer.textContent=data.summary||data.spoiler||'No concise answer available.';section.append(answer);
  target.append(section);
}
async function spoil(card){
  const button=card.querySelector('button');const target=card.querySelector('.answer');const link=card.querySelector('h2 a');
  button.disabled=true;target.textContent='Fetching the linked article, then reading locally…';
  try{
    const selected=$('mode').value;const modes=selected==='compare'?['original','tuned']:[selected];target.replaceChildren();
    for(const mode of modes){
      const response=await fetch('/api/spoil-link',{method:'POST',headers:{'Content-Type':'application/json','X-Spoiler-Token':$('token').textContent},body:JSON.stringify({url:link.href,headline:card.dataset.useArticleTitle?'':link.textContent,mode})});
      const data=await response.json();if(!response.ok)throw Error(data.error);
      if(card.dataset.useArticleTitle){link.textContent=data.article_title;delete card.dataset.useArticleTitle;}
      render(target,data,selected==='compare'?mode:null);
    }
  }catch(error){const message=document.createElement('p');message.className='error';message.textContent=error.message;target.replaceChildren(message);}
  finally{button.disabled=false;button.textContent='Spoil again';}
}
document.querySelectorAll('.story').forEach(card=>card.querySelector('button').onclick=()=>spoil(card));
$('add-link').onsubmit=event=>{
  event.preventDefault();let url;try{url=new URL($('url').value);if(!['https:','http:'].includes(url.protocol))throw Error();}catch{return;}
  const card=document.createElement('article');card.className='story';card.dataset.useArticleTitle='true';
  const publisher=document.createElement('p');publisher.className='publisher';publisher.textContent=url.hostname;
  const heading=document.createElement('h2');const link=document.createElement('a');link.setAttribute('data-spoiler-native','');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';link.textContent=url.href;heading.append(link);
  const button=document.createElement('button');button.type='button';button.textContent='Spoil';button.onclick=()=>spoil(card);
  const answer=document.createElement('div');answer.className='answer';answer.setAttribute('aria-live','polite');card.append(publisher,heading,button,answer);$('feed').prepend(card);$('url').value='';spoil(card);
};
