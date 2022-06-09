
# -*- coding: utf8 -*-

cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func
    
def parse_contexts(contexts):
    """Sorts rewrite rule contexts based on the type of context (left, right, or both) into separate lists

    Args:
        contexts(list): list of contexts
    
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
    """Generates transitions for context free rewrite rules

    Args:
        IN (list): list of input symbols
        OUT (list): iist of output symbols
        q0 (str, optional): initial state. Defaults to "<λ>".

    Returns:
        list: List of transitions
    """
    t = []
    for _in, _out in zip (IN, OUT): # all CF transitions are self loops
        t.append((q0, _in, q0, _out))
        t.append((q0, "?", q0, "?")) 
    return t
    
def generate_left_context_transitions(IN, OUT, contexts, q0="<λ>"):
    """Generates transitions for left context sensitive rewrite rules

        Args:
            IN (list): list of input symbols
            OUT (list): list of output symbols
            q0 (str, optional): initial state. Defaults to "<λ>".

        Returns:
            list: List of transitions
        """
    t = []
    
    for context in contexts:
        context = context.replace("_","")
        for _in, _out in zip(IN, OUT):
            next_state = ""             
            previous_state = q0
            
            for sym in context:                           
                next_state += sym 
                t.append( (previous_state, sym, cfx(next_state), sym) )
                t.append( (previous_state, "?", q0, "?") ) # unspecified transitions. ? is a placeholder cf Chandlee 2014
                
                if len(set(dfx(previous_state))) == 1 and len(set(dfx(next_state))) == 1: # beginning of context can repeat arbitrary number of times
                    t.append( (cfx(next_state), sym, cfx(next_state), sym) )
                
                previous_state = cfx(next_state) # update previous_state 
                
            t.append( (previous_state, _in, q0, _out) ) 
            t.append( (previous_state, "?", q0, "?") )
                
    return t

def generate_right_context_transitions(IN, OUT, contexts, q0="<λ>", Lcon=[],dual=False):
    """Generates transitions for right context sensitive rewrite rules

        Args:
            IN (list): list of input symbols
            OUT (list): list of output symbols
            q0 (str, optional): initial state. Defaults to "<λ>".
            Lcon (list, optional): left context already seen. Defaults to []
            dual(bool, optional): switches transition generation to account for dual contexts. Defaults to False.

        Returns:
            list: List of transitions
        """
    t = []
    
    for context in contexts:
        context = context.replace("_", "")
        for _in, _out in zip(IN, OUT):
            if dual: # function switches behaviour when generating transitions for dual context rules
                next_state = Lcon[0]
                previous_state = cfx(next_state)
            else:
                previous_state = q0
                next_state = ""  
                 
            right_context = _in + context # input symbol is always the first contextual transition. Also don't want to include the last symbol in context when generating states
            for sym in right_context[:-1]:
                next_state += sym
                
                t.append( (previous_state, sym, cfx(next_state), "λ") ) # all transitions moving to the right will output the empty string
                
                if previous_state == q0: # initial state gets a ?:? transition
                    t.append( (previous_state, "?", q0, "?") ) 
                else:
                    try:
                        output = dfx(previous_state).replace(Lcon[0],"") # for dual contexts, subtract the left context that has already been output
                    except IndexError:
                        output = dfx(previous_state)   
                    
                    t.append( (previous_state, "?", q0, output + "?") ) # if unknown symbol, need to output the state name along with '?'

                if len(next_state) == 1 and not dual: 
                    t.append( (cfx(next_state), sym, cfx(next_state), sym) )
                    
                previous_state = cfx(next_state) 
                
            # reached the end of the context
            t.append( (previous_state, right_context[-1] , q0, _out+context) ) # transduction: output out symbol + state name       
            try:
                output = dfx(previous_state).replace(Lcon[0],"") # for dual contexts, subtract the left context that has already been output
            except IndexError:
                        output = dfx(previous_state) 
            t.append( (previous_state, "?", q0, output + "?"))    
              
    return t

def generate_dual_context_transitions(IN, OUT, contexts,q0="<λ>"):
    """Generates transitions for dual context sensitive rewrite rules

        Args:
            IN (list): list of input symbols
            OUT (list): list of output symbols
            q0 (str, optional): initial state. Defaults to "<λ>".

        Returns:
            list: List of transitions
        """
    t = []
    for context in contexts:
        left_context = [context.split("_")[0]]
        right_context = [context.split("_")[1]]
        
        left_trans = list(filter(lambda x: x[1] == x[3], generate_left_context_transitions(IN, OUT, left_context , q0))) # need to take out transduction transitions
        right_trans = generate_right_context_transitions(IN, OUT, right_context, Lcon=left_context, dual=True)
        dual_trans = left_trans + right_trans
       
        t.extend(dual_trans)  
    return t
        
def get_transitions(in_syms, out_syms, contexts):
    """Gets all possible transitions from user strings and contexts

    Args:
        in_syms (str): string of space delimited input symbols
        out_syms (str): string of space delimited output symbols
        contexts (list): list of contexts

    Returns:
        list: list of all transitions to be turned into a dictionary
    """
    
    IN, OUT = in_syms.split(), out_syms.split()
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
        
    return trans