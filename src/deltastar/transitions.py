
# -*- coding: utf8 -*-


cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func

    
def parse_contexts(contexts):
    """Sorts rewrite rule contexts based on the type of context (left, right, or both)

    Returns:
        dict: dictionary of contexts sorted by context type
    """
    contexts_dict = {"L":set(), "R":set(), "LR":set()}
    
    for context in contexts:
        
        if not isinstance(context, str):
            raise TypeError(f"{context} must be of type 'str'")
        if "_" not in context:
            raise ValueError(f"{context} not recognized: context must be specified as X_, _X, or X_X, where X = contextual symbol(s)")
    
        con = context.split("_")
        
        if con[0] and con[1]: # dual contexts
            contexts_dict["LR"].add(f"{con[0]}_{con[1]}")
        elif con[0]: # strictly left context
            contexts_dict["L"].add(f"{con[0]}_")
        elif con[1]: # strictly right context
            contexts_dict["R"].add(f"_{con[1]}")   
            
    return contexts_dict

def generate_context_free_transitions(IN, OUT):
    t = []
    for _in, _out in zip (IN, OUT): 
        t.append(("<λ>", _in, "<λ>", _out))
        t.append(("<λ>", "?", "<λ>", "?")) 
    return t
    
def generate_left_context_transitions(IN, OUT, contexts):
    t = []
    
    for context in contexts:
        context = context.replace("_","")
        for _in, _out in zip(IN, OUT):
            next_state = ""             
            previous_state = "<λ>"
            
            for sym in context:                           
                next_state += sym 
                
                t.append( (previous_state, sym, cfx(next_state), sym) )
                t.append( (previous_state, "?", "<λ>", "?") ) # unspecified transitions. ? is a placeholder cf Chandlee 2014
                
                if len(next_state) == 1: # beginning of context can repeat arbitrary number of times
                    t.append( (cfx(next_state), sym, cfx(next_state), sym) )
                
                previous_state = cfx(next_state) # update previous_state 
                
                if next_state == context: # reached the last state of context
                    t.append( (previous_state, _in, "<λ>", _out) )
                    t.append( (previous_state, "?", "<λ>", "?") )
    return t

def generate_right_context_transitions(IN, OUT, contexts):
    t = []
    
    for context in contexts:
        context = context.replace("_", "")
        for _in, _out in zip(IN, OUT):
            next_state = ""       
            right_context = _in + context # input symbol is always the first contextual transition. Also don't want to include the last symbol in context when generating states
            previous_state = "<λ>"
            
            for sym in right_context[:-1]:
                next_state += sym
                t.append( (previous_state, sym, cfx(next_state), "λ") ) # all transitions moving to the right will output the empty string
                
                if previous_state == "<λ>": # initial state gets a ?:? transition
                    t.append( (previous_state, "?", "<λ>", "?") ) 
                else:
                    t.append( (previous_state, "?", "<λ>", dfx(previous_state) + "?") ) # if unknown symbol, need to output the state name along with '?'
                
                if len(next_state) == 1: 
                    t.append( (cfx(next_state), sym, cfx(next_state), sym) )
                    
                previous_state = cfx(next_state) 
                
                if next_state == right_context[:-1]: 
                    t.append( (previous_state, right_context[-1] , "<λ>", _out+context) ) # transduction: output out symbol + state name
                    t.append( (previous_state, "?", "<λ>", next_state + "?") )
    return t

    
def generate_dual_context_transitions(IN, OUT, contexts):
    return []
    

    
      
def get_transitions(in_strings, out_strings, contexts):
    
    IN, OUT = in_strings.split(), out_strings.split()
    if not IN or not OUT:
        raise NotImplementedError("Insertion and deletion rules not implemented yet. Stay tuned!")
    
    trans = [] # list of all transitions for current DFST
    
    context_dict= parse_contexts(contexts)
    
    if not contexts:
        trans.extend([con for con in generate_context_free_transitions(IN, OUT)])
        
    if context_dict.get("L"):
        trans += generate_left_context_transitions(IN, OUT, context_dict.get("L"))
        
    if context_dict.get("R"):
        trans += generate_right_context_transitions(IN, OUT, context_dict.get("R"))
        
    if context_dict.get("LR"):
        trans += generate_dual_context_transitions(IN, OUT, context_dict.get("LR"))
        
    return trans
    
