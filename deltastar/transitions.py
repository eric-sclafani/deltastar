
# -*- coding: utf8 -*-

# this file contains functions for parsing the user's specified rewrite rule(s) and 
# generating the appropriate transitions based off of contexts

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports and other instantiations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from collections import defaultdict
from dataclasses import dataclass

PH = "?" #"⊗"
get_lcon = lambda s1, s2: "".join([i for i in s1 if i in s2])
subtract_lcon = lambda s1, s2: "".join([i for i in s1 if i not in s2])
intersperse = lambda s: " ".join([i for i in s])
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constructors~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataclass(frozen=True) # frozen makes the class immutable so States can be dict keys in delta
class State:
    
    label:str
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
    ctype:str = None
    is_transduction:bool = False 
    seen_Lcon:str = ""
    
    def __repr__(self):
        return f"({self.start} | {self.insym} -> {self.outsym} | {self.end})"   
    
class ContextError(Exception):
    pass

    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

def parse_contexts(contexts):
   
    Lcons, Rcons, Dualcons = [],[],[]
    for con in contexts:
        
        if not isinstance(con, str):
            raise ContextError(f"{con} must be of type 'str'")
        elif "_" not in con:
            raise ContextError(f"{con} not recognized: context must be specified as X_, _X, or X_X, where X = contextual symbol(s)")
    
        con = tuple(con.split())
        
        # this block sorts contexts into their respective lists
        if con[-1] =="_":
            Lcons.append(con)
        elif con[0] == "_":
            Rcons.append(con)
        else:
            Dualcons.append(con)
            
    return Lcons, Rcons, Dualcons

def cf_transitions(insyms, outsyms,q0="λ"):
    
    # all CF transitions are self loops on initial state
    t = []
    for _in, _out in zip (insyms, outsyms): 
        t.append(Edge(State(q0),_in, _out, State(q0), ctype="cf"))
        
    t.append(Edge(State(q0),PH, PH, State(q0), ctype="cf"))
    return t
    
def Lcon_transitions(insyms, outsyms, contexts, q0="λ", dual=False):
    
    t = []
    
    for context in contexts:
        if not dual:
            context = context[:-1] # fixes an annoying bug w.r.t left vs. dual context transition generation
        for _in, _out in zip(insyms, outsyms):
            start = q0
            end = ""     
            ctype = "left"        
            
            for sym in context:                        
                end += sym # build the next state symbol by symbol 
                t.append(Edge(State(start), sym, sym, State(end), ctype=ctype))
                t.append(Edge(State(start), PH, PH, State(q0), ctype=ctype))
                 
                start = end # update start state
            
            t.append(Edge(State(start), _in, _out, State(q0), ctype=ctype, is_transduction=True)) 
            t.append(Edge(State(start), PH, PH, State(q0),  ctype=ctype))   
    return t


def Rcon_transitions(insyms, outsyms, contexts, q0="λ", Lcon=[],dual=False):
   
    t = []
    
    for context in contexts:
        for _in, _out in zip(insyms, outsyms):
        
            # transition generation depend on if its strictly right or dual context 
            if dual:
                leftcon = "".join(Lcon[0]) # join the left context to subtract it later in this func
                ctype = "dual"
                start = leftcon
                end = leftcon
            else:
                context = context[1:]
                ctype = "right"
                start = q0
                end = ""
            
            right_context = (_in,) + context # input symbol is always the first contextual transition. context is a tuple, so cast _in as a tuple and concat
            for sym in right_context[:-1]: # rightmost symbol is treated as the input for the transduction
                end += sym
                
                # all transitions moving to the right will output the empty string ("λ")
                seen_Lcon = get_lcon(start, leftcon) if dual else None
                t.append(Edge(State(start), sym, "λ", State(end), ctype=ctype, seen_Lcon=seen_Lcon))
                 
                output = start 
                if start == q0: # initial state gets a PH:PH transition
                    t.append(Edge(State(start), PH,PH, State(q0), ctype=ctype)) 
                      
                # if unknown symbol, need to output the state name along with PH symbol
                # for dual contexts, subtract the left context that has already been output
                output = subtract_lcon(start, leftcon) if dual else start if start != "λ" else ""
                    
                t.append(Edge(State(start), PH, output + PH, State(q0), ctype=ctype)) 
                start = end
                
            # reached the end of the context
            # transduction handling is a little different because its not part of the context
            
            # for dual contexts PH transitions, subtract the left context that has already been output
            output = subtract_lcon(start, leftcon) if dual else start 
        
            # transduction: output out symbol + state name   
            mapping = _out + "".join(context) 
        
            t.append(Edge(State(start), right_context[-1], mapping, State(q0), ctype=ctype, is_transduction=True, seen_Lcon=seen_Lcon)) 
            t.append(Edge(State(start), PH, output+PH, State(q0), ctype=ctype))      
                
    return t

def Dcon_transitions(insyms, outsyms, contexts,q0="λ"):

    t = []
 
    for context in contexts:
        hyphen = context.index("_")
        left_context = [context[:hyphen]]
        right_context = [context[hyphen+1:]]
        
        left_trans = [con for con in Lcon_transitions(insyms, outsyms, left_context, q0, dual=True) if not con.is_transduction] # filter out transduction transitions
        right_trans = Rcon_transitions(insyms, outsyms, right_context, Lcon=left_context, dual=True)
        dual_trans = left_trans + right_trans
       
        t.extend(dual_trans)  
    return t

def prefix_transitions(context_trans):
    
    Q, sigma, _ = get_Q_sigma_gamma(context_trans)
    Q.remove(State("λ")) # remove λ state 
    sigma = list(sigma)
    sigma.remove(PH) # remove PH symbol from sigma since it doesnt have prefix transitions
    transitions_to_add = []  

    for q in Q:
        q = q.label
        
        # exclude the first symbol because first symbol marks beginning of a "branch" of states (i.e. all states branching from state <a> begin with an "a")
        # this also lets us jump from one "branch" to another (i.e. <b> branch, <c> branch, etc..)
        pfxstate = q[1:]
        possible_prefix_trans = []
        
        # generate all possible prefix transitions for each state in Q by combining the prefix with all symbols in sigma
        for _ in range(len(pfxstate)+1):
            possible_prefix_trans.extend([Edge(State(q), PH, PH, State(pfxstate + s)) for s in sigma])
            pfxstate = pfxstate[1:]
               

        for ppt in possible_prefix_trans:
            if ppt.end in Q: # disregard states that dont exist
                
                # find all already existing transitions that have ppt.start as a start state  
                matched_trans = [ct for ct in context_trans if ct.start == ppt.start and ct.insym != PH]
                
                # get the last seen symbol to be used in the added prefix transition
                last_seen_symbol = str(ppt.end) if ppt.end[-1] == "]" else ppt.end[-1] # tag handling         
                
                # for each matched transition, find out if it already has a transition with the last seen symbol,
                symbol_seen = []
                for mt in matched_trans: 
                    if mt.insym == last_seen_symbol and not mt.is_transduction:
                        symbol_seen.append(mt)
                      
                find_mapping = [t for t in matched_trans if t.is_transduction] # finds the transduction transition
                
                # modify the last seen symbol depending on the matched transition's context type and append to transitions_to_add
                if not symbol_seen:
                    match = matched_trans[0]
                    ctype = match.ctype
                    lcon = match.seen_Lcon
                    output = last_seen_symbol
                    is_transduction = False
                
                    if ctype == "dual":
                        output = subtract_lcon(ppt.start, lcon) + last_seen_symbol
                        
                    elif ctype == "right":
                        
                        
                        
                        # self loops should only get last_seen_symbol. Otherwise, concatenate state name with last_seen_symbol
                        if ppt.start.label != ppt.end.label:
                            output = ppt.start.label + last_seen_symbol
                            
                            
                    
                    # need to replace the placeholder transduction mapping with one that goes to a prefix state (if applicable)
                    if match in find_mapping and match.insym == last_seen_symbol:
                        output = match.outsym
                        is_transduction = True # setting this lets the already existing PH transduction get overwritten in trans_to_dict()
                          
                     # if the prefix transduction has already been made, dont let any more possible prefix transductions into transitions_to_add
                    if ppt.is_transduction and not list(filter(lambda t: t.is_transduction, transitions_to_add)):
                        continue
                    
                    transitions_to_add.append(Edge(ppt.start, last_seen_symbol, output, ppt.end, is_transduction=is_transduction))
    
    # debugging code
    #             print(f"{last_seen_symbol = }")
    #             print(f"Proposed ppt: {ppt}")
    #             print(f"Matched trans: {matched_trans}\n")
    
    # print("Possible transitions being added:", *transitions_to_add, sep="\n")    
    # print("\n")   
             
    return transitions_to_add 

def get_Q_sigma_gamma(context_trans):
    
    Q = []
    for t in context_trans:
        if t.start not in Q:
            Q.append(t.start)
    
    sigma = set(t.insym for t in context_trans)
    gamma = set(t.outsym for t in context_trans) 
    return Q, sigma, gamma 

         
def get_final_mappings(trans):
    
    d = {}
    for t in trans:
        if t.start not in d and t.start.label != "λ":
            if t.ctype == "left":
                output = ""
            
            elif t.ctype == "right":
                output = t.start.label

            elif t.ctype == "dual":
                output = subtract_lcon(t.start.label, t.seen_Lcon)
            
            d[t.start] = intersperse(output)
    return d

def get_transitions(insyms, outsyms, contexts=[]):
    
    context_trans = [] # list of all context transitions 
    Lcons, Rcons, Dualcons= parse_contexts(contexts)
    
    if not contexts:
        context_trans += cf_transitions(insyms, outsyms)
    if Lcons:
        context_trans += Lcon_transitions(insyms, outsyms, Lcons)  
    if Rcons:
        context_trans += Rcon_transitions(insyms, outsyms, Rcons)  
    if Dualcons:
        context_trans += Dcon_transitions(insyms, outsyms, Dualcons)
        
    all_trans = context_trans + prefix_transitions(context_trans)
    
    return all_trans

    
def make_delta(trans):
    
    d = defaultdict(lambda: defaultdict(dict))
    for tran in trans:
        start, insym = tran.start, tran.insym
        end, outsym = tran.end, tran.outsym 
        
        # allows the PH transduction to be overwritten by the prefix one once
        if not d[start][insym] or tran.is_transduction and d[start][insym][1] == State("λ"): 
            d[start][insym] = [outsym, end] 
    return d

