import io
import json
import unittest
from unittest.mock import patch
from spoiler.core import Engine, MAX_CHARS, prepare
from tools.prepare_data import adapt


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self,*args): self.close()


class SpoilerTests(unittest.TestCase):
    article = 'The gardener saves banana peels because they enrich compost. ' * 4

    def response(self, output):
        return Response(json.dumps({'message':{'content':json.dumps(output)},'load_duration':123000000,'eval_count':12}).encode())

    def test_preprocessing_is_explicit(self):
        self.assertTrue(prepare('Hook', 'x'*(MAX_CHARS+1))[2])
        for article in ('short',None):
            with self.assertRaises(ValueError): prepare('Hook',article)

    def test_verified_quote_and_cache(self):
        engine=Engine()
        with patch('urllib.request.urlopen',return_value=self.response({'sentence':1})) as call:
            first=engine.generate('What does he save?',self.article)
            second=engine.generate('What does he save?',self.article)
        self.assertTrue(first['evidence_verified']);self.assertTrue(second['cache_hit']);self.assertEqual(call.call_count,1)
        self.assertEqual(first['load_ms'],123)
        self.assertEqual(first['spoiler'], 'The gardener saves banana peels because they enrich compost.')
        self.assertIn(first['spoiler'], first['evidence'])

    def test_rejects_invalid_sentence_ids_and_malformed_outputs(self):
        for output in [{'sentence':0}, {'sentence':999}, {'sentence':'1'}, {'sentence':True}, [], 'text']:
            with patch('urllib.request.urlopen',return_value=self.response(output)):
                self.assertFalse(Engine().generate('Hook',self.article)['evidence_verified'])

    def test_unavailable_and_identical_tuned(self):
        engine=Engine();engine.models['tuned']=''
        with self.assertRaises(ValueError): engine.generate('Hook',self.article,'tuned')
        engine.models['tuned']=engine.models['original']
        with self.assertRaises(ValueError): engine.generate('Hook',self.article,'tuned')

    def test_official_fields_preserved(self):
        row={'uuid':'a','postText':['Hook'],'targetParagraphs':['a','b'],'spoiler':['b'],'spoilerPositions':[[[1,0],[1,1]]],'tags':['phrase']}
        result=adapt(row)
        self.assertEqual(result['article'],'a\n\nb');self.assertEqual(result['positions'],row['spoilerPositions'])

    def test_api_origin_and_host_allowlist(self):
        from spoiler.server import Handler
        handler=object.__new__(Handler)
        handler.headers={'Host':'127.0.0.1:8765','Origin':'http://127.0.0.1:8765'}
        self.assertTrue(handler.allowed())
        handler.headers['Origin']='https://evil.example'
        self.assertFalse(handler.allowed())
        handler.headers={'Host':'evil.example:8765','Origin':'http://127.0.0.1:8765'}
        self.assertFalse(handler.allowed())
