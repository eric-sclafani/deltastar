#!/usr/bin/env python3

    
class ContextError(Exception):
    pass

class RuleError(Exception):
    pass


PH = "?" 
cfx = lambda string: f"<{string}>" 

def intersperse(string:str, delim=" "):
    """This mess of a function intersperses a string with delim. Accounts for tag format as well: [XXX].

    Args:
        string (str): string to be delimited
        delim (str, optional): delimiter. Defaults to " ".

    Returns:
        str: delimited string
    """
    output = ""
    i = 0
    while True:
        try:
            temp = string[i]
        except IndexError:
            break
        
        if temp == "[": # if "[" is detected, every symbol leading up to "]" is included in the tag
            j = 0
            for char in string[i+1:]:
                j += 1
                temp += char
                if char == "]":
                    break
            i += j # update i index to whatever is after the tag
                    
            output += delim + temp
        else:     
            output += delim + string[i]
        i += 1
    
    return output.strip(delim)

def despace(string):
    return "".join([c for c in string if c != " "])

def string_complement(s1, s2, pad=None):
    """Performs the relative complement operation on two strings."""
    
    if pad == "right":
        s2 = s2.rjust(len(s1), " ")
    elif pad == "left":
        s2 = s2.ljust(len(s1), " ")
    
    output = ""
    for i, s in enumerate(s1):
        if s != s2[i]:
            output += s
    return output
    
    
def subslices(iterable) -> tuple[list]:
    l = []
    for j in range(1,len(iterable)+1):
        l.append(iterable[0:j])
    return tuple(l)


    
    