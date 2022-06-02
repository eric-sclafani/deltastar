
# -*- coding: utf8 -*-


cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func
    
def parse_contexts(contexts):
    """Sorts rewrite rule contexts based on the type of context (left, right, or both)

    Returns:
        list: list of contexts sorted by context type
    """
    for context in contexts:
        if not isinstance(context, str):
            raise TypeError(f"{context} must be of type 'str'")
        if "_" not in context:
            raise ValueError(f"{context} not recognized: context must be specified as X_, _X, or X_X, where X = contextual symbol(s)")
    
    # after splitting, check which side of list is True (i.e. not the empty string)
    Lcons = list(filter(lambda x: x.split("_")[0] and not x.split("_")[1], contexts))
    Rcons = list(filter(lambda x: x.split("_")[1] and not x.split("_")[0], contexts))
    Dualcons = list(filter(lambda x: x.split("_")[1] and x.split("_")[0], contexts))
            
    return Lcons, Rcons, Dualcons

def generate_context_free_transitions(IN, OUT,q0="<λ>"):
    t = []
    for _in, _out in zip (IN, OUT): # all CF transitions are self loops
        t.append((q0, _in, q0, _out))
        t.append((q0, "?", q0, "?")) 
    return t
    
def generate_left_context_transitions(IN, OUT, contexts, q0="<λ>"):
    t = []
    
    for context in contexts:
        context = context.replace("_","")
        for _in, _out in zip(IN, OUT):
            next_state = ""             
            previous_state = q0
            
            for sym in context:                           
                next_state += sym 
                
                t.append( (previous_state, sym, cfx(next_state), sym) )
                
                if len(next_state) == 1: # beginning of context can repeat arbitrary number of times
                    t.append( (cfx(next_state), sym, cfx(next_state), sym) )
                
                previous_state = cfx(next_state) # update previous_state 
                
            # reached the end of the context
            t.append( (previous_state, _in, q0, _out) )
    return t

def generate_right_context_transitions(IN, OUT, contexts, q0="<λ>", Lcon=[],dual=False):
    t = []
    
    for context in contexts:
        context = context.replace("_", "")
        for _in, _out in zip(IN, OUT):
           
            if dual: # function switches behaviour when generating transitions for dual context rules
                next_state = Lcon[0] #! weird index error 
                previous_state = cfx(next_state)
            else:
                next_state = ""
                previous_state = q0
                
            right_context = _in + context # input symbol is always the first contextual transition. Also don't want to include the last symbol in context when generating states
            for sym in right_context[:-1]:
                next_state += sym
                t.append( (previous_state, sym, cfx(next_state), "λ") ) # all transitions moving to the right will output the empty string
                
                if len(next_state) == 1 and not dual: 
                    t.append( (cfx(next_state), sym, cfx(next_state), sym) )
                    
                previous_state = cfx(next_state) 
                
            # reached the end of the context
            t.append( (previous_state, right_context[-1] , q0, _out+context) ) # transduction: output out symbol + state name             
    return t

def generate_dual_context_transitions(IN, OUT, contexts,q0="<λ>"):
    
    t = []
    for context in contexts:
        left_context = [context.split("_")[0]]
        right_context = [context.split("_")[1]]
        
        left_trans = list(filter(lambda x: x[1] == x[3], generate_left_context_transitions(IN, OUT, left_context , q0))) # need to take out transduction transitions
        right_trans = generate_right_context_transitions(IN, OUT, right_context, Lcon=left_context, dual=True)
        dual_trans = left_trans + right_trans
       
        t.extend(dual_trans)  
    return t

   
       
       
def prefix_transitions(trans):
    pass
        
def get_transitions(in_strings, out_strings, contexts):
    
    IN, OUT = in_strings.split(), out_strings.split()
    if not IN or not OUT:
        raise NotImplementedError("Insertion and deletion rules not implemented yet. Stay tuned!")
    
    trans = [] # list of all transitions for current DFST
    Lcons, Rcons, Dualcons= parse_contexts(contexts)
    
    if not contexts:
        trans += generate_context_free_transitions(IN, OUT)
    if Lcons:
        trans += generate_left_context_transitions(IN, OUT, Lcons)  
    if Rcons:
        trans += generate_right_context_transitions(IN, OUT, Rcons)  
    if Dualcons:
        trans += generate_dual_context_transitions(IN, OUT, Dualcons)
        
    statenames = set(map(lambda x: dfx(x[0]), trans))
    #! prefix trans    
    
    return trans



    
