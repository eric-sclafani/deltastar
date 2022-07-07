
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
@dataclass
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
   
    # sanity checks
    for context in contexts:
        if not isinstance(context, str):
            raise TypeError(f"{context} must be of type 'str'")
        if "_" not in context:
            raise ValueError(f"{context} not recognized: context must be specified as X_, _X, or X_X, where X = contextual symbol(s)")
    
    # after splitting, check which side of list is not the empty string
    Lcons = list(filter(lambda x: x.split("_")[0] and not x.split("_")[1], contexts))
    Rcons = list(filter(lambda x: x.split("_")[1] and not x.split("_")[0], contexts))
    Dualcons = list(filter(lambda x: x.split("_")[1] and x.split("_")[0], contexts))
            
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


def prefix_transitions():
    pass

def generate_final_mappings():
    pass

def trans_to_dict(trans):
    
    transdict = defaultdict(lambda: defaultdict(dict))
    
    for trans in trans:
        start, insym = str(trans.start), trans.insym
        end, outsym = str(trans.end), trans.outsym 
        transdict[start][insym] = [end, outsym]
        
    return transdict

        
def get_transitions(IN, OUT, contexts):
    
    trans = [] # list of all transitions 
    Lcons, Rcons, Dualcons= parse_contexts(contexts)
    
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
    sigma =  set(sym for transitions in delta.values() for sym in transitions.keys())
    gamma = set(sym[1] for transitions in delta.values() for sym in transitions.values()) 
    
        
    #! perform prefix gen 
    
    #! perform final mappings and return alongside delta
    
   
    return delta, Q, sigma, gamma

