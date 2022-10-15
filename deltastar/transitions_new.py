from dataclasses import dataclass
from utils.funcs import despace, remove_duplicate_states
from pipe import select, where
from more_itertools import windowed

lam = "λ" # so I dont have to constantly track down this symbol

@dataclass
class State:
    label:tuple
    ctype:str = ""
    seen_lcon:str = ""
    output:str = ""
    is_initial:bool = False
    
    def __repr__(self):
        return despace(self.label)
 
@dataclass
class Transition:
    start:State
    insym:str
    outsym:str
    end:State
    is_mapping:bool=False
    
    def __repr__(self):
        return f"({self.start} | {self.insym} -> {self.outsym} | {self.end})"

@dataclass
class Rule:
    X:str
    Y:str
    context:str
    ctype:str
    mtype:str # unused

    def __repr__(self):
        context = "_" if not self.context else self.context
        return f"{self.X} -> {self.Y} / {context}"
    
    def get_trigger_state(self):
        """Gets the state in which the transduction occurs"""
        return self.get_statelabels()[-1]
    
    def get_trigger_sym(self):
        """Gets the symbol that triggers the mapping to occur"""
        return self.X if self.ctype in ["left", "cf"] else self.context.split()[-1][-1]
    
    def get_states(self):
        
        lstates, rstates = [], [] # need this declaration since they may be empty (strictly left or right context)
        get_labels = lambda x: [tuple(x[0:j]) for j in range(1, len(x)+1)]
        context = self.context.split("_")
        
        if self.ctype in ["left", "dual"]:
            lcon = context[0].strip() if context[0] else ""
            lstates = [State(label, ctype="left") for label in get_labels(lcon.split())]
            
        if self.ctype in ["right", "dual"]:
            rcon = (self.X + " " + context[1][:-1].strip()) if context[1] else ""
            rcon = (lcon + " " + rcon) if self.ctype == "dual" else rcon # combines lcon+rcon for dual context state labels
            rstates = [State(label, ctype="right", output=label) for label in get_labels(rcon.split())] 
            
        q_0 = [State((lam,), is_initial=True)]
        # due to combining lcon+rcon above, states with duplicate labels are made. Need to remove them.
        return remove_duplicate_states(q_0 + lstates + rstates) 
        
    @classmethod
    def rule(cls, mapping, context=""):
        X, Y = mapping
        ctype = "cf"
        if context: 
            context_list = context.split()
            index = context_list.index("_")
            ctype = "left" if index == len(context_list)-1 else "right" if index == 0 else "dual"
              
        mtype = "delete" if not Y else "insert" if not X else "rewrite"  
        return cls(X, Y, context, ctype, mtype)

class Delta:
    """This constructor holds all transitions and methods for accessing transition attributes"""
    
    def __init__(self, rule):
        self.rule = rule
        self.transitions = []
        
    def get_mappings(self):
        """Retrieves all mapping transitions""" 
        maps = list(self.transitions | where(lambda x: x.is_mapping))
        return maps
         
    def get_sigma(self):
        insyms = set(self.transitions | select(lambda x: x.insym))
        insyms.add(self.rule.get_trigger_sym())
        return insyms
    
    def state_exists_with_insym(self, state_label, pfxsym):
        # if this list is ever populated, then state already has an outgoing arc with pfxsym
        match_found = list(self.transitions | where(lambda x: x.start.label == state_label and x.insym == pfxsym))
        return True if match_found else False
    
    def add_transition(self, start, insym, outsym, end, is_mapping=False):
        self.transitions.append(Transition(start, insym, outsym, end, is_mapping))
        
    def display_transitions(self):
        print(*self.transitions, sep="\n")

def make_context_trans(d):
    
    states = d.rule.get_states()
    if len(states) == 1: # cf has no context trans
        return d
    
    for start, end in windowed(states, n=2):
        insym = end.label[-1]
        outsym = end.label[-1] if end.ctype == "left" else lam
        d.add_transition(start = start,
                         insym = insym,
                         outsym = outsym,
                         end = end)
    return d

def modify_state_outputs(d):
    
    delta_ctype = d.rule.ctype
    for transition in d.transitions:
        
        if delta_ctype == "right":
            pass
        
        elif delta_ctype == "dual":
            pass 
    return d

    
def make_prefix_trans(d):


    #! handle transductions here
    # for q in t.get_statelabels():
    #     pfxstate = q[1:]
        
    #     while True:
    #         # concats each sym in sigma with pfxstate and keeps it if it exists in Q
    #         pfxstates = [pfxstate + [s] for s in t.get_sigma() if pfxstate + [s] in t.get_statelabels()]
    #         for state in pfxstates:
    #             pfxsym = state[-1]
                
    #             if not t.state_exists_with_insym(q, pfxsym):
    #                 if t.rule.ctype == "left": 
    #                     t.add_transition(start  = State(q, ctype="left", seen_lcon=""),
    #                                      insym  = pfxsym,
    #                                      outsym = pfxsym,
    #                                      end    = State(state, ctype="left", seen_lcon=""))
                        
                    
    #         if not pfxstate:
    #             break 
    #         pfxstate = pfxstate[1:]   

    return d


def make_PH_trans(d):
    return d
    

def generate_transitions(mapping, context=""):
    
    rule = Rule.rule(mapping, context)  
    d = Delta(rule)
    
    d = make_context_trans(d)
    #d = modify_state_outputs(d)
    #d = make_prefix_trans(d)
    #d = make_PH_trans(d)
    return d

#t1 = generate_transitions(("x", "b"), "a a a c a b _")
#t1.display_transitions()

t2 = generate_transitions(("m", "n"), "a b c _ x y z")
t2.display_transitions()



 

    
    
    
    

# future composition code 👀
# class Test(str):
    
#     def __matmul__(self, B):
#         A = self
#         return Test(A + B)
# A = Test("hello")
# B = Test("hi")
# print(A @ B)