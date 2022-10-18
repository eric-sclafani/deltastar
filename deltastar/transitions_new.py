from dataclasses import dataclass
from utils.funcs import despace, remove_duplicate_states, subtract_lcon
from pipe import select, where
from more_itertools import windowed

lam = "λ" # so I dont have to constantly track down this symbol
PH = "?"

@dataclass
class State:
    label:tuple
    ctype:str = ""
    output:str = ""
    is_initial:bool = False
    
    def __repr__(self):
        return despace(self.label)
 
@dataclass
class Edge:
    start:State
    insym:str
    outsym:str
    end:State
    is_mapping:bool=False
    
    def __repr__(self):
        return f"({self.start} | {self.insym} -> {self.outsym} | {self.end})"

class Transitions:
    """This constructor holds all transitions and methods for accessing transition properties"""
    
    def __init__(self, rule):
        self.rule = rule
        self.X = X
        self.Y = Y
        self.context = context
        self.ctype = ctype
        self.mtype = mtype # mapping type (rewrite, insertion, or deletion)
        self.transitions = []
        
    def rule(self):
        context = "_" if not self.context else self.context
        return f"{self.X} -> {self.Y} / {context}"
         
    def get_sigma(self):
        insyms = set(self.transitions | select(lambda x: x.insym))
        insyms.add(self.X)
        return insyms
    
    def state_exists_with_insym(self, state_label, pfxsym):
        # if this list is ever populated, then state already has an outgoing arc with pfxsym
        match_found = list(self.transitions | where(lambda x: x.start.label == state_label and x.insym == pfxsym))
        return True if match_found else False
    
    def add_edge(self, start, insym, outsym, end, is_mapping=False):
        self.transitions.append(Edge(start, insym, outsym, end, is_mapping))
        
    def display_transitions(self):
        print(*self.transitions, sep="\n")
              
def parse_rule(mapping, context=""):
    X, Y = mapping
    ctype = "cf"
    if context: 
        context_list = context.split()
        index = context_list.index("_")
        ctype = "left" if index == len(context_list)-1 else "right" if index == 0 else "dual"
            
    mtype = "delete" if not Y else "insert" if not X else "rewrite" 
    return X, Y, ctype, mtype
    
def extract_states(context:str, ctype:str, X:str):
        
        lstates, rstates = [], [] # need this declaration since they may be empty (strictly left or right context)
        get_labels = lambda x: [tuple(x[0:j]) for j in range(1, len(x)+1)] 
        context = context.split("_")
        
        if ctype in ["left", "dual"]:
            lcon = context[0].strip() if context[0] else ""
            lstates = [State(label, ctype="left") for label in get_labels(lcon.split())]
            
        if ctype in ["right", "dual"]:
            rcon = (X + " " + context[1][:-1].strip()) if context[1] else ""
            rcon = (lcon + " " + rcon) if ctype == "dual" else rcon # combines lcon+rcon for dual context state labels
            rstates = [State(label, ctype="right", output=label) for label in get_labels(rcon.split())] 
        
        q_0 = [State((lam,), is_initial=True)]
        # due to combining lcon+rcon above, states with duplicate labels are made. Need to remove them.
        return remove_duplicate_states(q_0 + lstates + rstates)
    

def make_context_trans(t):
    
    states = t.rule.get_states()
    if len(states) == 1: # cf has no context trans
        return t
    
    for start, end in windowed(states, n=2):
        insym = end.label[-1]
        outsym = end.label[-1] if end.ctype == "left" else lam
        t.add_edge(start = start,
                   insym = insym,
                   outsym = outsym,
                   end = end)
    return t

def modify_state_outputs(t):
    """If rule is a dual context, right states need have the left context subtracted from their output"""
    
    if t.rule.ctype == "dual":
        # grab last transition with left state
        last_left_state = list(d.transitions | where(lambda x: x.start.ctype == "left"))[-1]
        seen_lcon = last_left_state.start.label
        
        for trans in t.transitions:
            end = trans.end
            if end.ctype == "right":
                end.output = subtract_lcon(end.label, seen_lcon)
    return t

    
def make_prefix_trans(t, states):
    
    state_labels = list(states | select(lambda x: x.label))
    
    for label in state_labels:
        pfxstate = label[1:]
        while True:
            
            pfxstates = [pfxstate + (s,) for s in t.get_sigma() if pfxstate + (s,) in state_labels]
            for state in pfxstates:
                pfxsym = state[-1]
        
        
            if not pfxstate:
                break
            
            print(f"Current state: {label}")
            print(f"Pfxstates: {pfxstates}\n")
            pfxstate = pfxstate[1:]
    return t


def make_PH_trans(t):
    return t
    

def generate_transitions(mapping, context=""):
    
    rule = Rule.rule(mapping, context)  
    t = Transitions(rule)
    
    t = make_context_trans(t)
    t = modify_state_outputs(t)
    #t = make_prefix_trans(t)
    #t = make_PH_trans(t)
    return t

t1 = generate_transitions(("x", "b"), "a c a b _")


#t2 = generate_transitions(("m", "n"), "a b c _ x y zsl")

#! state output testing code
# for tran in t2.transitions:
#     print(tran.end.ctype)
#     print("Transition: ", tran)
#     print(f"{tran.start=}, {tran.start.output=}\n{tran.end=}, {tran.end.output=}\n\n")


