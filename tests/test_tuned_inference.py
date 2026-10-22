import io
import json
import unittest
from unittest.mock import patch
from spoiler.core import Engine

class TunedInferenceTests(unittest.TestCase):
    article='The gardener saves banana peels because they enrich compost. Mix scraps with dry leaves and turn the pile regularly.'

    def engine(self):
        with patch.dict('os.environ',{'SPOILER_TUNED_MODEL':'lfm-click-tuned:checkpoint128','SPOILER_DEFAULT_MODE':'tuned'}):
            return Engine()

    def test_default_tuned_and_baseline_share_protocol_but_not_weights(self):
        engine=self.engine(); payloads=[]
        def answer(request,**kwargs):
            payloads.append(json.loads(request.data))
            return io.BytesIO(json.dumps({'message':{'content':'{"sentence":1,"worth_clicking":63}'}}).encode())
        with patch('urllib.request.urlopen',side_effect=answer):
            tuned=engine.generate('Why save banana peels?',self.article)
            baseline=engine.generate('Why save banana peels?',self.article,'original')
        self.assertEqual(tuned['mode'],'tuned')
        self.assertNotEqual(payloads[0]['model'],payloads[1]['model'])
        for field in ('messages','format','options'):
            self.assertEqual(payloads[0][field],payloads[1][field])
        self.assertEqual(tuned['click_value']['score'],63)
        self.assertEqual(tuned['click_value']['band'],'green')
        self.assertIn('Fine-tuned',tuned['click_value']['disclaimer'])
        self.assertIn('Original',baseline['click_value']['disclaimer'])
        self.assertEqual(tuned['protocol'],'sentence-click-score-v2')

    def test_malformed_score_is_not_silently_replaced_by_heuristic(self):
        for value in (True,101,'70',None):
            raw=io.BytesIO(json.dumps({'message':{'content':json.dumps({'sentence':1,'worth_clicking':value})}}).encode())
            with patch('urllib.request.urlopen',return_value=raw):
                with self.assertRaises(ValueError):self.engine().generate('Why save peels?',self.article)

    def test_preview_api_omitted_mode_uses_configured_default(self):
        from spoiler import server
        body=json.dumps({'url':'https://example.com/a','headline':'A useful guide','snippet':'Three practical steps.'}).encode()
        handler=object.__new__(server.Handler)
        handler.path='/api/preview'
        handler.headers={'Host':'127.0.0.1:8765','Origin':server.ORIGIN,'X-Spoiler-Token':server.TOKEN,'Content-Length':str(len(body))}
        handler.rfile=io.BytesIO(body)
        handler.reply=lambda status,data:None
        with patch.object(server.ENGINE,'default_mode','tuned'),patch.object(server.ENGINE,'preview',return_value={'request_ms':1}) as call:
            handler.do_POST()
        self.assertEqual(call.call_args[0][-1],'tuned')

    def test_metadata_fallback_keeps_original_model_for_untrained_preview_task(self):
        raw=io.BytesIO(json.dumps({'message':{'content':'{"score":45,"summary":"A guide to saving energy."}'}}).encode())
        engine=self.engine()
        with patch('urllib.request.urlopen',return_value=raw) as call:
            result=engine.preview('https://example.com/guide','Save energy')
        self.assertEqual(result['requested_mode'],'tuned')
        self.assertEqual(result['mode'],'original')
        self.assertEqual(json.loads(call.call_args[0][0].data)['model'],engine.models['original'])
