import io
import json
import unittest
from unittest.mock import patch

from spoiler.core import Engine
from spoiler.preview import prepare_preview, preview_rating, preview_summary
from spoiler.articles import ArticleError
from spoiler import server


class PreviewTests(unittest.TestCase):
    def test_url_context_uses_slug_without_query_or_network(self):
        with patch('socket.getaddrinfo',side_effect=AssertionError('No DNS for metadata')):
            data=prepare_preview('https://example.com/how-to-save-energy?token=secret#part','Save energy','Three practical steps.')
        self.assertEqual(data['url_context'],'example.com/how-to-save-energy')
        self.assertNotIn('secret',json.dumps(data))

    def test_invalid_preview_cannot_become_confident_output(self):
        for value in [{'score':True},{'score':101},[],{'score':'50'}]:
            with self.assertRaises(ValueError):preview_rating(value)

    def test_preview_inference_never_claims_article_was_read(self):
        response=io.BytesIO(json.dumps({'message':{'content':json.dumps({'score':72,'summary':'Three steps can help lower energy bills.'})},'eval_count':11}).encode())
        with patch('urllib.request.urlopen',return_value=response) as call:
            data=Engine().preview('https://example.com/guide','A practical energy guide','Three steps to lower energy bills.')
        payload=json.loads(call.call_args[0][0].data)
        self.assertIn('energy bills',payload['messages'][1]['content'])
        self.assertTrue(data['preview_only'])
        self.assertEqual(data['summary'],'Three steps can help lower energy bills.')
        self.assertEqual(data['spoiler'],'')
        self.assertEqual(data['evidence'],'')
        self.assertFalse(data['evidence_verified'])
        self.assertEqual(data['click_value']['band'],'green')
        self.assertIn('Article not read',data['status'])

    def test_summary_is_one_sentence_and_rejects_empty_output(self):
        self.assertEqual(preview_summary({'summary':'A practical guide. Extra commentary.'}),'A practical guide.')
        for value in [None,'',True,'x'*501]:
            with self.assertRaises(ValueError):preview_summary({'summary':value})

    def handler(self,path):
        body=json.dumps({'url':'https://example.com/article','headline':'A useful guide','snippet':'Three concrete tips'}).encode()
        handler=object.__new__(server.Handler)
        handler.path=path
        handler.headers={'Host':'127.0.0.1:8765','Origin':server.ORIGIN,'X-Spoiler-Token':server.TOKEN,'Content-Length':str(len(body))}
        handler.rfile=io.BytesIO(body)
        handler.reply=lambda status,data:setattr(handler,'result',(status,data))
        return handler

    def test_blocked_fetch_automatically_uses_only_preview(self):
        handler=self.handler('/api/spoil-link')
        with patch('spoiler.server.fetch_article',side_effect=ArticleError('Blocked','publisher_http_error',403)), \
             patch.object(server.ENGINE,'preview',return_value={'request_ms':1,'preview_only':True}) as preview, \
             patch.object(server.ENGINE,'generate') as generate:
            handler.do_POST()
        self.assertEqual(handler.result[0],200)
        self.assertTrue(handler.result[1]['preview_only'])
        self.assertEqual(handler.result[1]['publisher_status'],403)
        self.assertEqual(preview.call_args[0][2],'Three concrete tips')
        generate.assert_not_called()

    def test_explicit_preview_endpoint_never_fetches_article(self):
        handler=self.handler('/api/preview')
        with patch('spoiler.server.fetch_article') as fetch,patch.object(server.ENGINE,'preview',return_value={'request_ms':1}):
            handler.do_POST()
        self.assertEqual(handler.result[0],200)
        fetch.assert_not_called()
