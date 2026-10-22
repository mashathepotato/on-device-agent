const $ = id => document.getElementById(id);
let models = {};
fetch('/api/status').then(r => r.json()).then(s => { models = s.models; if(models.tuned) $('tuned').textContent = 'Ready: ' + models.tuned; });
$('reveal').onclick = async () => {
  $('reveal').disabled = true; $('notice').textContent = 'Reading locally… first load may take longer.';
  try {
    for (const mode of ['original','tuned'].filter(m => models[m])) {
      const response = await fetch('/api/spoil', {method:'POST', headers:{'Content-Type':'application/json','X-Spoiler-Token':$('token').textContent},body:JSON.stringify({headline:$('headline').value, article:$('article').value, mode})});
      const data = await response.json(); if(!response.ok) throw Error(data.error);
      const target = $(mode); target.replaceChildren();
      const answer = document.createElement('p'); answer.textContent = data.spoiler || data.status; target.append(answer);
      const quote = document.createElement('blockquote'); quote.textContent = data.evidence; target.append(quote);
      const detail = document.createElement('small'); detail.textContent = `${data.cache_hit ? 'Cached response' : 'Inference'} · ${data.request_ms} ms request · ${data.inference_ms} ms model inference · load ${data.load_ms} ms · ${data.output_tokens} output tokens\n${data.truncated ? 'PARTIAL ARTICLE: first 16,000 characters only. ' : ''}${data.status}`; target.append(detail);
    }
    $('notice').textContent = 'Check that the quoted passage supports the answer.';
  } catch(error) { $('notice').textContent = error.message; }
  finally { $('reveal').disabled = false; }
};

fetch('/api/examples').then(r=>r.json()).then(({examples})=>{examples.forEach((example,index)=>{const option=document.createElement('option');option.value=index;option.textContent=example.headline;$('examples').append(option);});$('examples').onchange=()=>{const example=examples[$('examples').value];if(example){$('headline').value=example.headline;$('article').value=example.article;}};});
