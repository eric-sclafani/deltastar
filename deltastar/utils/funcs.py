#!/usr/bin/env python3
from typing import Iterable
    
class ContextError(Exception):
    pass

class RuleError(Exception):
    pass

PH = "?" 
cfx = lambda string: f"<{string}>" 
    
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




#! deprecated functions from first release
# def intersperse(string:str, delim=" "):
#     """This mess of a function intersperses a string with delim. Accounts for tag format as well: [XXX].

#     Args:
#         string (str): string to be delimited
#         delim (str, optional): delimiter. Defaults to " ".

#     Returns:
#         str: delimited string
#     """
#     output = ""
#     i = 0
#     while True:
#         try:
#             temp = string[i]
#         except IndexError:
#             break
        
#         if temp == "[": # if "[" is detected, every symbol leading up to "]" is included in the tag
#             j = 0
#             for char in string[i+1:]:
#                 j += 1
#                 temp += char
#                 if char == "]":
#                     break
#             i += j # update i index to whatever is after the tag
                    
#             output += delim + temp
#         else:     
#             output += delim + string[i]
#         i += 1
    
#     return output.strip(delim)

    


    
    