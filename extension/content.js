(() => {
  if(globalThis.__getToThePointInstalled) return;
  globalThis.__getToThePointInstalled = true;
  const handled = new WeakSet();
  function sourceURL(anchor) {
    try {
      let url = new URL(anchor.href, location.href);
      // Google often wraps outbound result links in /url?q= or /url?url=.
      if(/(^|\.)google\.[a-z.]+$/.test(url.hostname) && url.pathname === '/url') url = new URL(url.searchParams.get('q') || url.searchParams.get('url'));
      return ['https:','http:'].includes(url.protocol) ? url.href : '';
    } catch {return '';}
  }
  function attach(anchor) {
    if(handled.has(anchor) || anchor.hasAttribute('data-spoiler-native') || anchor.closest('[data-spoiler-control]')) return;
    const headingNode = anchor.querySelector('h1,h2,h3');
    const headline = (headingNode?.innerText || anchor.innerText).trim().replace(/\s+/g,' ');
    const url = sourceURL(anchor);
    const heading = anchor.matches('h1 a,h2 a,h3 a') || headingNode;
    let mount = anchor;
    let previewContainer = anchor.closest('article') || anchor.parentElement;
    if(/(^|\.)google\.[a-z.]+$/.test(location.hostname) && location.pathname === '/search') {
      const organic = anchor.closest('.MjjYud');
      const topStory = anchor.matches('a.aJWbwf[jsname=YKoRaf]');
      if(organic?.querySelector('h3') && !topStory) {
        if(!heading) return; // Do not decorate the publisher/About this source link.
        mount = organic; // Outside Google's tracked and transformed citation wrappers.
        previewContainer = organic;
      } else if(topStory) {
        mount = anchor.closest('.m7jPZ') || anchor;
        previewContainer = mount;
      }
    }
    if(!url || url.split('#')[0] === location.href.split('#')[0] || headline.length < 20 || headline.length > 350 || headline.split(' ').length < 4) return;
    if(!heading && (headline.length < 40 || !anchor.closest('main,article,[role=main],section'))) return;
    if(anchor.closest('nav,header,footer,[role=navigation]') || !anchor.getClientRects().length) return;
    handled.add(anchor);
    const host=document.createElement('span'); host.dataset.spoilerControl='';
    host.style.cssText='display:inline-block;position:relative;z-index:2;transform:none;rotate:none;vertical-align:middle;margin:3px 6px;max-width:min(100%,650px);';
    const root=host.attachShadow({mode:'open'});
    const style=document.createElement('style');
    style.textContent=':host{font:13px system-ui;color:#17392e}button{font:600 12px system-ui;border:1px solid #8cae9a;background:#edf6ef;color:#174c36;border-radius:20px;padding:5px 11px;cursor:pointer}button:disabled{opacity:.6}.panel{display:block;box-sizing:border-box;max-width:620px;min-width:220px;white-space:normal;background:#f8fcf6;border:1px solid #b2c9b5;border-radius:8px;padding:13px;margin-top:7px;text-align:left;color:#17392e;font:14px/1.5 system-ui;overflow-wrap:anywhere}.quote{border-left:2px solid #91b09a;padding-left:10px;font-size:12px}.meta{font-size:11px;color:#526b5d}a{color:#175b44}';
    const button=document.createElement('button');button.textContent='Spoil';button.type='button';button.title='Fetch this linked article and reveal its answer locally';
    root.append(style,button);mount.insertAdjacentElement('afterend',host);
    host.addEventListener('pointerdown',event=>event.stopPropagation());
    host.addEventListener('mousedown',event=>event.stopPropagation());
    button.addEventListener('click',async event=>{
      event.preventDefault();event.stopPropagation();button.disabled=true;
      root.querySelector('.panel')?.remove();const panel=document.createElement('div');panel.className='panel';panel.setAttribute('role','status');panel.textContent='Fetching the linked article, then reading locally…';root.append(panel);
      try {
        // Read only this result card's visible preview, excluding our own controls.
        const visibleSnippet=previewContainer.querySelector('.VwiC3b,.IsZvec,[data-sncf="1"],.st');
        const previewParts=[];
        if(!visibleSnippet){
          const walker=document.createTreeWalker(previewContainer,NodeFilter.SHOW_TEXT);
          let node;
          while((node=walker.nextNode())){
            const parent=node.parentElement;
            if(parent && parent.getClientRects().length && !parent.closest('[data-spoiler-control],script,style,nav,button'))previewParts.push(node.textContent);
          }
        }
        const snippet=(visibleSnippet?.innerText || previewParts.join(' ')).replace(headline,'').replace(/\s+/g,' ').trim().slice(0,1500);
        const response=await chrome.runtime.sendMessage({type:'spoil-link',url,headline,snippet});
        if(!response?.ok) throw Error(response?.error || 'The extension was reloaded; refresh this page.');
        const data=response.data;panel.replaceChildren();
        if(data.click_value){
          const value=data.click_value;
          const colors={green:['#d9f3e2','#14532d'],amber:['#fff1c2','#713f12'],red:['#fee2e2','#991b1b']};
          const [background,color]=colors[value.band]||colors.amber;
          const badge=document.createElement('div');badge.style.cssText=`display:inline-block;padding:7px 11px;margin-bottom:8px;border-radius:8px;font:750 16px system-ui;background:${background};color:${color}`;badge.textContent=`${value.score}/100 · ${value.label}`;panel.append(badge);
        }
        const answer=document.createElement('p');answer.style.margin='0';answer.textContent=data.summary || data.spoiler || 'No concise answer available.';panel.append(answer);
      } catch(error){
        panel.textContent=error.message;
        const source=document.createElement('a');source.href=url;source.target='_blank';source.rel='noopener noreferrer';source.textContent='Open source normally';source.style.display='block';panel.append(source);
      }
      finally{button.disabled=false;button.textContent='Spoil again';}
    });
  }
  function scan(){document.querySelectorAll('a[href]').forEach(attach);}
  scan();let timer;new MutationObserver(()=>{clearTimeout(timer);timer=setTimeout(scan,350);}).observe(document.body,{childList:true,subtree:true});
})();
