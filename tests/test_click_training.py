import unittest
from training.click_model.protocol import prompt, validate

class JointProtocolTests(unittest.TestCase):
    def test_invalid_scores_cannot_be_training_targets(self):
        for score in (True, -1, 101, '60', None):
            with self.assertRaises(ValueError): validate({'sentence':1,'worth_clicking':score},2)
        for sentence in (True, -1, 3):
            with self.assertRaises(ValueError): validate({'sentence':sentence,'worth_clicking':60},2)

    def test_untrusted_content_is_delimited_and_input_is_bounded(self):
        row = {'headline':'Why?', 'article':'A useful sentence explaining the result. '*600}
        messages, choices, truncated = prompt(row)
        self.assertTrue(truncated)
        self.assertIn('untrusted',messages[0]['content'])
        self.assertTrue(choices)
        self.assertEqual(validate({'sentence':0,'worth_clicking':0},len(choices))['sentence'],0)
