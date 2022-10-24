from dataclasses import dataclass, field
from utils.funcs import despace, remove_duplicate_states, subtract_lcon
from pipe import select, where
from more_itertools import windowed

lam = "λ" # so I dont have to constantly track down this symbol
PH = "?" # placeholder

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

@dataclass
class Transitions:
    """This constructor holds all transitions and methods for accessing transition properties"""
    states:list[State]
    X:str
    Y:str
    context:str
    mtype:str
    transitions:list = field(default_factory=list)
        
    def rule(self):
        context = "_" if not self.context else self.context
        return f"{self.X} -> {self.Y} / {context}"
         
    def get_sigma(self):
        insyms = set(self.transitions | select(lambda x: x.insym))
        insyms.add(self.X)
        return insyms
    
    def state_exists_with_insym(self, state_label, insym):
        # if this list gets populated, then state already has an outgoing arc with insym
        find_match = list(self.transitions | where(lambda x: x.start.label == state_label and x.insym == insym))
        return True if find_match else False
    
    def add_edge(self, start, insym, outsym, end, is_mapping=False):
        self.transitions.append(Edge(start, insym, outsym, end, is_mapping))
        
    def to_dict(self):
        pass
        
    def display_transitions(self):
        print(*self.transitions, sep="\n")
              
def parse_rule(mapping, context=""):
    
    #! validation will happen here
    X, Y = mapping
    ctype = "cf"
    if context: 
        context_list = context.split()
        index = context_list.index("_")
        ctype = "left" if index == len(context_list)-1 else "right" if index == 0 else "dual"
            
    mtype = "delete" if not Y else "insert" if not X else "rewrite" 
    return X, Y, context, ctype, mtype
    
def extract_states(context:str, ctype:str, X:str) -> list[State]:
        
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
    

def make_context_trans(t, states):
    
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

def modify_state_outputs(t, states, ctype):
    """If rule is a dual context, right states need have the left context subtracted from their output"""
    if ctype == "dual":
        last_left_state = list(states | where(lambda x: x.ctype == "left"))[-1]# grab last transition with left state
        for trans in t.transitions:
            end = trans.end
            if end.ctype == "right":
                end.output = subtract_lcon(end.label, last_left_state.label)
    return t

def make_prefix_trans(t, states):
    
    state_labels = list(states | select(lambda x: x.label))
    state_labels.remove((lam,))
    
    for i, label in enumerate(state_labels):
        state = label[1:] 
        pfxstate = None
        while True:
            for s in t.get_sigma():
                temp = state + (s,)
                if temp in state_labels and len(temp) <= len(label) and not t.state_exists_with_insym(label, s):
                    if not pfxstate: # prevents overriding
                        pfxstate = temp
                    
                    #! next step: need to handle mapping

            
            
            state = state[1:]
            if not state and len(temp) == 1:
                break
            
        print(f"Current state: {label} Pfxstate: {pfxstate}\n")
    return t


def make_PH_trans(t):
    return t
    

def generate_transitions(mapping, context=""):
    
    X, Y, context, ctype, mtype = parse_rule(mapping, context)
    states = extract_states(context, ctype, X)
    t = Transitions(states, X, Y, context, mtype)
    
    t = make_context_trans(t, states)
    t = modify_state_outputs(t, states, ctype)
    t = make_prefix_trans(t, states)
    #t = make_PH_trans(t)
    return t

t1 = generate_transitions(("x", "b"), "a c a b _")

#t2 = generate_transitions(("m", "n"), "a b c _ x y z")
# for tran in t2.transitions:
#     print(tran.end.ctype)
#     print("Transition: ", tran)
#     print(f"{tran.start=}, {tran.start.output=}\n{tran.end=}, {tran.end.output=}\n\n")


