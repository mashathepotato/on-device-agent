"""Shared production protocol plus training record preparation."""
import hashlib
import json
from spoiler.core import candidates, prepare
from spoiler.joint import VERSION, RUBRIC, build_messages, schema, validate

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def prompt(row):
    headline, article, truncated = prepare(row['headline'], row['article'])
    choices = candidates(article)
    return build_messages(headline, choices), choices, truncated
