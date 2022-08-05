import pytest
from src.transitions import *



def test_parse_contexts():
    
    mappings = [
        ("a", "b"),
        ("[]")
        ]
    
    lcons, rcons, dualcons = parse_contexts([""])