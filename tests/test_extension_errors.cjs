const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../extension/background.js'), 'utf8');

async function run(fetch) {
  let listener;
  const chrome = {storage:{local:{get:async()=>({mode:'original'})}},
    runtime:{onMessage:{addListener:callback=>listener=callback}}};
  vm.runInNewContext(source, {fetch,chrome});
  return new Promise(resolve=>listener({type:'spoil-link',url:'https://example.com/article',headline:'Article'}, {}, resolve));
}

(async()=>{
  let articleCalls=0;
  const publisher = await run(async url=>{
    if(url.endsWith('/api/pair'))return {ok:true,json:async()=>({token:'test'})};
    articleCalls++;
    return {ok:false,status:422,json:async()=>({error:'The publisher refused the article fetch (HTTP 403). The local server is connected.'})};
  });
  assert.equal(articleCalls,1,'Publisher errors must not trigger pairing retries');
  assert.equal(publisher.ok,false);
  assert.match(publisher.error,/publisher/);
  assert.doesNotMatch(publisher.error,/Check that the local server is running/);
  const offline = await run(async()=>{throw new TypeError('Failed to fetch');});
  assert.match(offline.error,/Cannot reach the local server/);
  console.log('Extension publisher/transport error tests passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
