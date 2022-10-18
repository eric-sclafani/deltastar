#!/usr/bin/env python3
from typing import Iterable
    
def despace(l:Iterable) -> str:
    return "".join([c for c in l if c != " "])

def remove_duplicate_states(states:list):
    """Removes duplicate states from a list of states by checking their labels"""
    for state_1 in states:
        for state_2 in states:
            if state_2 != state_1 and state_1.label == state_2.label:
                states.remove(state_2)     
    return states

def subtract_lcon(rcon:tuple, lcon:tuple):
    return rcon[len(lcon):]


    


    
    