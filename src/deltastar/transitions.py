
# -*- coding: utf8 -*-

# this file contains functions for parsing the user's specified rewrite rule(s) and 
# generating the appropriate transitions based off of contexts

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports and other instantiations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from dataclasses import dataclass, field
from more_itertools import collapse

global PH
PH = "⊗"
cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@dataclass
class State:
    
    label:str
    output: str = None
    initial:bool = False
    outgoingedges:list = field(default_factory=lambda: []) # lets you use mutable default parameters
    
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
     
def parse_contexts(contexts):
   
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

                if len(end) == 1 and not dual:  # outdated block
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

def generate_final_mappings():
    pass

def prefix_transitions():
    pass


        
def get_transitions(pairs, contexts=[]):
    
    IN = [pair[0] for pair in pairs]
    OUT = [pair[1] if pair[1] else "Ø" for pair in pairs] # accounts for deletion rules

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


if __name__ == "__main__":
    doubles = [
        ("a", "b"),
        ("x", "y")
    ]    
    

    f = get_transitions(doubles, ["m_p"])


    for l in f:
        print(l)





#  #! ~~HIGHLY WIP~~~: some prefix transitions are still incorrect / not generated. Prefix transitions will be overhauled in a future update
#         # prefix transitions: need to do them here instead of transitions.py bc I need access to the delta dict
#         for state in states:
            
#             prefix = ""
#             for sym in state:
#                 prefix += sym # rebuild prefix state name symbol by symbol
                
#                 # prefix level transitions
#                 if prefix != state: # disallow self looping transitions (aka stops before it reaches last symbol of state
#                     if not delta[cfx(state)].get(prefix[-1]): # check to see if current state does not already have an outgoing transition with last symbol of prefix
#                         if state[-1] + sym == prefix: # very important check: if the last symbol of the state + current symbol == the prefix. Without this check, false transitions can be created
#                             delta[cfx(state)][prefix[-1]] = [cfx(prefix), prefix[-1]]
                        
#                 # character level transitions (need these too since the prefix level doesn't capture all possible transitions)
#                 if not delta[cfx(state)].get(sym) and state != "λ": # check if outgoing transition already exists with input char from state and disallow q0 self loop                       
#                     if sym != state and cfx(sym) in delta: 
#                         delta[cfx(state)][sym] = [cfx(sym), sym]
#         return delta
    
#     def _finals(self):
#         states = []
#         right = False
        
#         # checks to see if the machine is strictly right context:
#         # after collapsing, if second entry == lambda, then we know for sure it's a right context and not a dual one
#         # need to do this because dual contexts have different rules for state outputs than strictly right
#         check_right = list(collapse([val for state, transition in self.delta.items() for val in transition.values()]))
#         if check_right[1] == "λ":
#             right = True
        
#         for state, transitions in self.delta.items():
#             seen_left_context = ""
#             for in_sym, out_trans in transitions.items():
                
#                 if right:
#                     if out_trans[1] == "λ": # makes sure self loops arent counted by checking if out symbol is lambda (empty)
#                         state_output = dfx(out_trans[0])
#                         states.append((out_trans[0], state_output))   
                         
#                 else: # is a dual context
#                     # this condition block keeps track of left contexts and subtracts them from right context state names when processing a dual context
#                     if out_trans[1] != "λ" and in_sym not in seen_left_context and in_sym != PH and in_sym == out_trans[1]:
#                         seen_left_context += in_sym
                        
#                     elif out_trans[1] == "λ": 
#                         if dfx(out_trans[0]).startswith(seen_left_context) and seen_left_context != dfx(out_trans[0]): 
                            
#                             state_output = dfx(out_trans[0]).replace(seen_left_context,"",1)
#                         else:
#                             state_output = dfx(out_trans[0]) 
#                         states.append((out_trans[0], state_output))
#         return states