
# -*- coding: utf8 -*-

# this file contains functions for parsing the user's specified rewrite rule(s) and 
# generating the appropriate transitions based off of contexts

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports and other instantiations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from collections import defaultdict
from dataclasses import dataclass

PH = "⊗"
subtract_lcon = lambda s1, s2: "".join([i for i in s1 if i in s2]) # take the intersection of the two strings (retain order)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constructors~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataclass(frozen=True) # frozen makes the class immutable so States can be dict keys in delta
class State:
    
    label:str
    output:str = None
    initial:bool = False
    
    def __len__(self):
        return len(self.label)

    def __repr__(self):
        return self.label
    
    def __getitem__(self, idx):
        string = self.label
        if isinstance(idx, slice): # idx is a slice object in this case
            start,stop,step = idx.indices(len(string))
            return "".join([string[i] for i in range(start,stop,step)])
        else:
            return string[idx]

@dataclass
class Edge:
    
    start:State
    insym:str
    outsym:str
    end:State
    is_transduction:bool = False 
    context_type:str = None
    seen_left_context:str = None
    
    
    def __repr__(self):
        return f"({self.start} | {self.insym} -> {self.outsym} | {self.end})" 


@dataclass
class Transitions:
    pass
    
    
    
    
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

def parse_contexts(contexts):
   
    Lcons, Rcons, Dualcons = [],[],[]
    for con in contexts:
        
        if not isinstance(con, str):
            raise TypeError(f"{con} must be of type 'str'")
        elif "_" not in con:
            raise ValueError(f"{con} not recognized: context must be specified as X_, _X, or X_X, where X = contextual symbol(s)")
    
        con = tuple(con.split())
        
        # this block sorts contexts into their respective lists
        if con[-1] =="_":
            Lcons.append(con)
        elif con[0] == "_":
            Rcons.append(con)
        else:
            Dualcons.append(con)
    return Lcons, Rcons, Dualcons

def generate_context_free_transitions(IN, OUT,q0="λ"):
    
    # all CF transitions are self loops on initial state
    t = []
    for _in, _out in zip (IN, OUT): 
        t.append(Edge(State(q0),_in, _out, State(q0)))
        t.append(Edge(State(q0),PH, PH, State(q0)))
    return t
    
def generate_left_context_transitions(IN, OUT, contexts, q0="λ"):
    
    t = []
    
    for context in contexts:
        
        for _in, _out in zip(IN, OUT):
            start = q0
            end = ""             
            
            for sym in context:                        
                end += sym # build the next state symbol by symbol 
                t.append(Edge(State(start), sym, sym, State(end)))
                t.append(Edge(State(start), PH, PH, State(q0)))
                
                #! experimental (needs testing, but seems to be working right now)
                if len(set(start)) == 1 and len(set(end)) == 1: # beginning of context can repeat arbitrary number of times. Checks to see if prev and next states contain the exact same symbols
                    t.append(Edge(State(end), sym, sym, end))
                    
                start = end # update start state
            
            t.append(Edge(State(start), _in, _out, State(q0), is_transduction=True)) 
            t.append(Edge(State(start), PH, PH, State(q0)))   
    return t


def generate_right_context_transitions(IN, OUT, contexts, q0="λ", Lcon=[],dual=False):
   
    t = []
    
    for context in contexts:
        for _in, _out in zip(IN, OUT):
        
            # transitions are different when generating dual contexts 
            if dual:
                leftcon = "".join(Lcon[0]) # join the left context to subtract it later in this func
                context_type = "dual"
                start = leftcon
                end = leftcon
            else:
                context_type = "right"
                start = q0
                start = ""
        
            right_context = (_in,) + context # input symbol is always the first contextual transition. context is a tuple, so cast _in as a tuple and concat
            
            for sym in right_context[:-1]: # rightmost symbol is treated as the input for the transduction
                end += sym
                
                # all transitions moving to the right will output the empty string ("λ")
                
                seen_left_context = subtract_lcon(start, leftcon) if dual else None
                
                t.append(Edge(State(start), sym, "λ", State(end), seen_left_context = seen_left_context, context_type=context_type))
                    
                if start == q0: # initial state gets a PH:PH transition
                    t.append(Edge(State(start), PH,PH, State(q0)))
                    
                elif dual:
                    output = start.replace(leftcon,"") # for dual contexts, subtract the left context that has already been output
                else:
                    output = start
                     
                t.append(Edge(State(start), PH, output + PH, State(q0))) # if unknown symbol, need to output the state name along with PH symbol

                # beginning of context can repeat arbitrary times
                if len(end) == 1 and not dual: #! experimental (needs testing)
                    t.append(Edge(State(end), sym, sym, State(end)))
                    
                start = end
                
            # reached the end of the context
            # transduction handling is a little different because its not part of the context
            
            if dual: # for dual contexts, subtract the left context that has already been output
                output = start.replace(leftcon,"") 
            else:
                output = start
               
            # transduction: output out symbol + state name   
            mapping = _out + "".join(context)
            t.append(Edge(State(start), right_context[-1], mapping, State(q0), is_transduction=True, context_type=context_type)) 
            t.append(Edge(State(start), PH, output+PH, State(q0), context_type=context_type))      
                
    return t

def generate_dual_context_transitions(IN, OUT, contexts,q0="λ"):

    t = []
    
    for context in contexts:
        hyphen = context.index("_")
        left_context = [context[:hyphen]]
        right_context = [context[hyphen+1:]]
        
        #! turn this into a for loop after renaming context functions
        left_trans = list(filter(lambda x: not x.is_transduction, generate_left_context_transitions(IN, OUT, left_context , q0))) # filter out transduction transitions
        
        right_trans = generate_right_context_transitions(IN, OUT, right_context, Lcon=left_context, dual=True)
        
        dual_trans = left_trans + right_trans
       
        t.extend(dual_trans)  
    return t

def prefix_transitions(trans, Q, sigma):
    
    Q.remove(State("λ")) # remove λ state 
    sigma = list(sigma)
    sigma.remove(PH) # remove PH symbol from sigma since it doesnt have prefix transitions
    
    possible_prefix_states = defaultdict(lambda:[])   
    # possible_prefix_states = []
    
    for q in Q:
        q = q.label 
        
        # edge case: if len(state) is 1 (beginning of context), does not get prefix transitions, only single symbol ones
        if len(q) == 1:
            possible_prefix_states[State(q)] = [State(s) for s in sigma]
            
            #possible_prefix_states.append((State(q), [State(s) for s in sigma]))
            
        else:
            # exclude the first symbol because first symbol marks beginning of a "branch" of states (i.e. all states branching from state <a> begin with an "a")
            # this also lets us jump from one "branch" to another (i.e. <b> branch, <c> branch, etc..)
            prefixstate = q[1:]  
            
            for _ in range(len(prefixstate)+1):
                # generate all possible states each state can reach by combining the prefix with all symbols in sigma
                possible_prefix_states[State(q)].extend([State(prefixstate + sym) for sym in sigma])
                
                #possible_prefix_states.append((State(q), [State(prefixstate + sym) for sym in sigma]))
                
                # shift prefix window to the right
                prefixstate = prefixstate[1:]
        
    # # this loop checks each entry in the list of context transitions and generates prefix transitions
    
    for state, pfx_states in sorted(possible_prefix_states.items(), key = lambda x: len(x[0])): # sort by state length
        for pfxstate in pfx_states:
            for transition in trans:
                
                
                
                
                
    #             # 1. check if possible pfxstate exists within trans (filter over all trans)
    #                 # 2. if pfxstate[-1] == "]": last_seen_symbol = pfxstate else last_seen_symbol = pfxstate[-1] 
    #                 # 3. for each tran with start = state, check if they have last_seen_symbol
                
    
                
        
        
        
        
        
    #TODO: prefix transitions for trandsuction       
            
            
            
            
            
            
def trans_to_dict(trans):
    
    transdict = defaultdict(lambda: defaultdict(dict))
    
    for trans in trans:
        start, insym = trans.start, trans.insym
        end, outsym = trans.end, trans.outsym 
        transdict[start][insym] = [outsym, end]
        
    return transdict

def get_Q_sigma_gamma(trans):
    
    Q = set(t.start for t in trans)
    sigma = set(t.insym for t in trans)
    gamma = set(t.outsym for t in trans)  
    return Q, sigma, gamma





  
def generate_final_mappings():
    pass

def get_transitions(IN, OUT, contexts):
    
    trans = [] # list of all transitions 
    Lcons, Rcons, Dualcons= parse_contexts(contexts)
    
    
    #! maybe find a neater way of doing this?
    if not contexts:
        trans += generate_context_free_transitions(IN, OUT)
    if Lcons:
        trans += generate_left_context_transitions(IN, OUT, Lcons)  
    if Rcons:
        trans += generate_right_context_transitions(IN, OUT, Rcons)  
    if Dualcons:
        trans += generate_dual_context_transitions(IN, OUT, Dualcons)
        
        
    #transitions = Transitions()
       
    # for t in trans:
    #     print(t,"\n",t.start, t.seen_left_context,"\n" )
     
    Q, sigma, gamma = get_Q_sigma_gamma(trans)
    
    prefix_transitions(trans, Q, sigma) 
    
    
    delta = trans_to_dict(trans)
    
    
    
   
    
    
    #! perform final mappings and return them to dfst.py
    
   
    return delta, Q, sigma, gamma




def main():
    
    d,q,s,g = get_transitions(["a"],["b"], ["x y _ z w"])
 
    
    

if __name__ == "__main__":
    szfz = "poop"
    
    main()
   
    
    

