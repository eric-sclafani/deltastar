

PH = "?" 
cfx = lambda string: f"<{string}>" 

def intersperse(string, delim=" "):
    return delim.join([c for c in string])

def despace(string):
    return "".join([c for c in string if c != " "])

def string_complement(s1, s2, pad):
    """Performs the relative complement operation on two strings. """
    
    output = ""
    if pad == "right":
        s2 = s2.rjust(len(s1), " ")
    elif pad == "left":
        s2 = s2.ljust(len(s1), " ")
        
    for i, s in enumerate(s1):
        if s != s2[i]:
            output += s
    return output