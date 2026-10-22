"""Fast, transparent click-value heuristic; not a trained or calibrated model."""
import re

VERSION = 'click-value-heuristic-v1'


def click_value(headline, article, has_answer):
    """Estimate whether opening the article offers useful detail beyond the spoiler."""
    text = article.lower()
    words = re.findall(r"\b[\w'-]+\b", text)
    score = 45
    signals = []

    def add(points, reason):
        nonlocal score
        score += points
        signals.append((points, reason))

    if len(words) >= 300:
        add(10, 'There is substantial detail beyond the one-line answer.')
    elif len(words) < 100:
        add(-15, 'The article is short; the spoiler may cover most of its value.')
    if re.search(r'\b(how to|step.by.step|instructions|guide|checklist)\b', headline.lower()):
        add(15, 'The headline promises practical guidance worth opening.')
    if re.search(r'\b(because|explains?|mechanism|causes?|how it works)\b', text):
        add(8, 'The text includes explanations beyond the headline.')
    if re.search(r'\b(study|research|experiment|survey|report|data)\b', text) and re.search(r'\b(found|measured|published|results|according to)\b', text):
        add(12, 'The text refers to research or reported findings; inspect the source.')
    if re.search(r'\d+(?:\.\d+)?\s*(?:%|percent|participants|patients|people|years|months|hours|degrees)\b', text):
        add(5, 'It contains concrete measurements or quantities.')
    if re.search(r"\b(you (?:won.t|will not) believe|shocking|mind.blowing|doctors hate|one weird trick|this changes everything|what happened next)\b", headline.lower()):
        add(-20, 'The headline relies on hype or a curiosity gap.')
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 15]
    if len(sentences) >= 4 and len(set(sentences)) / len(sentences) < .6:
        add(-20, 'Much of the extracted text repeats itself.')
    if not has_answer:
        add(-10, 'The baseline could not select a useful answer, so value is uncertain.')
        score = min(score, 60)

    score = max(0, min(100, score))
    band = 'green' if score >= 65 else 'red' if score < 40 else 'amber'
    label = {'green': 'Worth a click', 'amber': 'Maybe worth it', 'red': 'Probably skip'}[band]
    signals.sort(key=lambda item: abs(item[0]), reverse=True)
    reasons = [reason for _, reason in signals[:3]]
    if not reasons:
        reasons = ['Limited signals either way; open it if the topic interests you.']
    return {'score': score, 'band': band, 'label': label,
            'reason': ' '.join(reasons), 'method': VERSION,
            'disclaimer': 'Baseline guess · not fine-tuned',
            'scope': 'Estimated reading value from the scanned text; not a truth or credibility rating.'}
