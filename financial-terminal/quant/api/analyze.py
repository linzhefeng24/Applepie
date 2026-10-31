"""Pure request handler for the numerical optimizer API."""
from engine import analyze

def handle(payload):
    return analyze(payload)
