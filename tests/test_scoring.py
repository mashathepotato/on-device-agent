import unittest

from spoiler.scoring import click_value


class ClickValueTests(unittest.TestCase):
    def test_substantive_guide_outranks_repetitive_clickbait(self):
        useful = ('A published study measured the results for 250 participants. '
                  'The guide explains how to inspect a battery because temperature causes degradation. '
                  'Check the terminals and follow the manufacturer instructions before using it. ')
        guide = click_value('How to check your battery safely', useful, True)
        bait = click_value("You won't believe this shocking trick", 'Nothing happened at the event. ' * 8, True)
        self.assertGreater(guide['score'], bait['score'])
        self.assertEqual(guide['band'], 'green')
        self.assertEqual(bait['band'], 'red')
        self.assertIn('not fine-tuned', guide['disclaimer'])

    def test_no_answer_does_not_get_green_recommendation(self):
        rating = click_value('How to understand this study', 'A published study measured results because data explains causes. ' * 50, False)
        self.assertLess(rating['score'], 65)
        self.assertNotEqual(rating['band'], 'green')

    def test_rating_is_bounded_and_has_an_explanation(self):
        for title, article in [('', ''), ('SHOCKING!', 'Repeated filler. ' * 100), ('A useful guide', 'Some text.')]:
            rating = click_value(title, article, True)
            self.assertTrue(0 <= rating['score'] <= 100)
            self.assertTrue(rating['reason'])
