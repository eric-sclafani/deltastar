
# -*- coding: utf8 -*-

# this file contains functions for parsing the user's specified rewrite rule(s) and 
# generating the appropriate transitions based off of contexts

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports and other instantiations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from collections import defaultdict
from dataclasses import dataclass

global PH
PH = "⊗"
cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constructors~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataclass(frozen=True) # frozen makes the class immutable so States can be dict keys
class State:
    
    label:str
    output: str = None
    initial:bool = False
    
    def __repr__(self):
        return self.label
   
@dataclass
class Tran:
    
    start:State
    insym:str
    outsym:str
    end:State
    istransduction:bool = False
    
    def __repr__(self):
        return f"({self.start} |{self.insym} -> {self.outsym}| {self.end})" 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    
    
     
def parse_contexts(contexts):
   
    Lcons, Rcons, Dualcons = [],[],[]
    for con in contexts:
        if not isinstance(con, str):
            raise TypeError(f"{con} must be of type 'str'")
        elif "_" not in con:
            raise ValueError(f"{con} not recognized: context must be specified as X_, _X, or X_X, where X = contextual symbol(s)")
    
        # this block sorts contexts into their respective lists
        if con.endswith("_"):
            Lcons.append(con)
        elif con.startswith("_"):
            Rcons.append(con)
        else:
            Dualcons.append(con)
        
    return Lcons, Rcons, Dualcons

def generate_context_free_transitions(IN, OUT,q0="<λ>"):
    
    # all CF transitions are self loops on initial state
    t = []
    for _in, _out in zip (IN, OUT): 
        t.append(Tran(State(q0),_in, _out, State(q0)))
        t.append(Tran(State(q0),PH, PH, State(q0)))
    return t
    
def generate_left_context_transitions(IN, OUT, contexts, q0="<λ>"):
    
    t = []
    for context in contexts:
        context = context.replace("_","")
        for _in, _out in zip(IN, OUT):
            start = q0
            end = ""             
            
            for sym in context:                           
                end += sym # build the next state symbol by symbol 
                t.append(Tran(State(start), sym, sym, State(cfx(end))))
                t.append(Tran(State(start), PH, PH, State(q0)))
                
                #! experimental (needs testing)
                if len(set(dfx(start))) == 1 and len(set(dfx(end))) == 1: # beginning of context can repeat arbitrary number of times. Checks to see if prev and next states contain the exact same symbols
                    t.append(Tran(State(cfx(end)), sym, sym, cfx(end)))
                    
                start = cfx(end) # update start state
            
            t.append(Tran(State(start), _in, _out, State(q0), istransduction=True)) 
            t.append(Tran(State(start), PH, PH, State(q0)))   
    return t


def generate_right_context_transitions(IN, OUT, contexts, q0="<λ>", Lcon=[],dual=False):
   
    t = []
    for context in contexts:
        context = context.replace("_", "")
        for _in, _out in zip(IN, OUT):
            
            # transitions are different when generating dual contexts (i.e. start state is different)
            end = Lcon[0] if dual else "" 
            start = cfx(end) if dual else q0
                 
            right_context = _in + context # input symbol is always the first contextual transition
            for sym in right_context[:-1]: # don't want to include the last symbol in context when generating states
                end += sym
                t.append(Tran(State(start), sym, "λ", State(cfx(end)))) # all transitions moving to the right will output the empty string ("λ")
                
                
                if start == q0: # initial state gets a PH:PH transition
                    t.append(Tran(State(start), PH,PH, State(q0)))
                else:
                    try:
                        output = dfx(start).replace(Lcon[0],"") # for dual contexts, try to subtract the left context that has already been output
                    except IndexError:
                        output = dfx(start)   

                    t.append(Tran(State(start), PH, output + PH, State(q0))) # if unknown symbol, need to output the state name along with PH symbol

                #! experimental (needs testing)
                if len(end) == 1 and not dual:  
                    t.append(Tran(State(cfx(end)), sym, sym, State(cfx(end))))
                    
                start = cfx(end) 
                
            # reached the end of the context
            t.append(Tran(State(start), right_context[-1], _out+context, State(q0), istransduction=True)) # transduction: output out symbol + state name   
                
            try:
                output = dfx(start).replace(Lcon[0],"") # for dual contexts, subtract the left context that has already been output
            except IndexError:
                output = dfx(start) 
                           
            t.append(Tran(State(start), PH, output+PH, State(q0)))      
                
    return t

def generate_dual_context_transitions(IN, OUT, contexts,q0="<λ>"):

    t = []
    for context in contexts:
        left_context = [context.split("_")[0]]
        right_context = [context.split("_")[1]]
        
        left_trans = list(filter(lambda x: not x.istransduction, generate_left_context_transitions(IN, OUT, left_context , q0))) # filter out transduction transitions
        
        right_trans = generate_right_context_transitions(IN, OUT, right_context, Lcon=left_context, dual=True)
        
        dual_trans = left_trans + right_trans
       
        t.extend(dual_trans)  
    return t

def prefix_transitions(delta, Q, sigma):
    """Updates delta with prefix transitions by reference"""
    
    Q = list(map(lambda x: dfx(x.label), Q)) # remove < > from states
    Q.remove("λ") # remove λ state 
    sigma = list(sigma)
    sigma.remove(PH) # remove PH symbol from sigma since it doesnt have prefix transitions
    
    possible_states = defaultdict(lambda:[])   
    for state in Q:
        # edge case: if state consists of one symbol (beginning of context), it does not get prefix transitions
        if len(state) == 1:
            possible_states[State(state)] = [State(s) for s in sigma]
        else:
            # exclude the first symbol because first symbol marks beginning of a "branch" of states (i.e. all states branching from state <a> begin with an "a")
            # this also lets us jump from one "branch" to another (i.e. <b> branch, <c> branch, etc..)
            prefixstate = state[1:]  
            
            for _ in range(len(prefixstate)+1):
                # generate all possible states each state can reach by combining the prefix with all symbols in sigma
                possible_states[State(state)].extend([State(prefixstate + sym) for sym in sigma])
                prefixstate = prefixstate[1:]
    
    for state, pos_states in possible_states.items():
        print(state, pos_states)
            
    
            
             
def generate_final_mappings():
    pass

def trans_to_dict(trans):
    
    transdict = defaultdict(lambda: defaultdict(dict))
    
    for trans in trans:
        start, insym = trans.start, trans.insym
        end, outsym = trans.end, trans.outsym 
        transdict[start][insym] = [end, outsym]
        
    return transdict

        
def get_transitions(IN, OUT, contexts):
    
    trans = [] # list of all transitions 
    Lcons, Rcons, Dualcons= parse_contexts(contexts)
    
    
    #! maybe find a neater way of doing this? (more_itertools?)
    if not contexts:
        trans += generate_context_free_transitions(IN, OUT)
    if Lcons:
        trans += generate_left_context_transitions(IN, OUT, Lcons)  
    if Rcons:
        trans += generate_right_context_transitions(IN, OUT, Rcons)  
    if Dualcons:
        trans += generate_dual_context_transitions(IN, OUT, Dualcons)
        
    delta = trans_to_dict(trans)
    Q = list(delta.keys())
    
    #! maybe find a neater way of doing this? (more_itertools?)
    sigma =  set(sym for transitions in delta.values() for sym in transitions.keys())
    gamma = set(sym[1] for transitions in delta.values() for sym in transitions.values()) 
    
    # updates delta with prefix transitions by reference
    prefix_transitions(delta, Q, sigma)
    
    #! perform final mappings and return them to dfst.py
    
   
    return delta, Q, sigma, gamma




def main():
    
    d,q,s,g = get_transitions(["a"],["b"], ["acab_", "b_", "c_"])
    

if __name__ == "__main__":
    szfz = "poop"
    
    main()
   
    
    

