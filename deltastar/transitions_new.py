from dataclasses import dataclass
from utils.funcs import despace

@dataclass
class State:
    label:tuple
    ctype:str
    seen_lcon:str = ""
    output:str = None
    
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
    
    def get_state_labels(self):
        
        lstates, rstates = [], []
        getlabels = lambda x: [tuple(x[0:j]) for j in range(1, len(x)+1)]
        context = self.context.split("_")
        if self.ctype in ["left", "dual"]:
            lcon = context[0].strip() if context[0] else ""
            lstates = getlabels(lcon.split())
            
        if self.ctype in ["right", "dual"]:
            rcon = self.X + " " + context[1][:-1].strip() if context[1] else ""
            
            if self.ctype == "dual":
                rcon = lcon + " " + rcon
            
            # filter out the left states 
            rstates = [s for s in getlabels(rcon.split()) if s not in lstates]

        return lstates, rstates
        
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
        
    def get_maps(self):
        """Retrieves all mapping transitions""" 
        maps = list(filter(lambda x: x.is_mapping, self.transitions))
        return maps
        
    def get_sigma(self):
        insyms = set(map(lambda x: x.insym, self.transitions))
        insyms.add(self.rule.get_trigger_sym())
        return insyms
        
    def get_trans_with_state(self, state_label):
        return list(filter(lambda x: x.start.label == state_label, self.transitions))
    
    def state_exists_with_insym(self, state_label, pfxsym):
        # if this list is ever populated, then state already has an outgoing arc with pfxsym
        return True if list(filter(lambda x: x.start.label == state_label and x.insym == pfxsym, self.transitions)) else False
    
    def add_transition(self, start, insym, outsym, end, is_mapping=False, prepend=False):
        self.transitions.append(Transition(start, insym, outsym, end, is_mapping))
        
    def display_transitions(self):
        print(*self.transitions, sep="\n")
        
def make_context_trans(t):
    
    lstates, rstates = t.rule.get_state_labels()

    for i in range(len(lstates)-1): # this block generates left context transitions
        start, end = lstates[i], lstates[i+1]
        t.add_transition(start  = State(start, ctype="left"),
                         insym  = end[-1],
                         outsym = end[-1],
                         end    = State(end, ctype="left"))
    
    try: # Dual context: this block adds transition connecting the last left state w/ the first right state 
        start = t.transitions[-1].end
        end = rstates[0]
        t.add_transition(start  = start,
                         insym  = end[-1],
                         outsym = "λ",
                         end    = State(end, ctype="right"))
    except IndexError: pass
    
    for i in range(len(rstates)-1): # this block generates right context transitions
        start, end = rstates[i], rstates[i+1]  
        t.add_transition(start  = State(start, ctype="right"),
                         insym  = end[-1],
                         outsym = "λ",
                         end    = State(end, ctype="right"))
        
    try: # this block adds initial state to context state transition (if applicable)
        trans1 = t.transitions[0]
        q_0 = Transition(start  = State("λ", ctype=trans1.start.ctype),
                         insym  = str(trans1.start)[0],
                         outsym = str(trans1.start)[0] if trans1.start.ctype == "left" else "λ",
                         end    = trans1.start)
        t.transitions.insert(0, q_0) # prepend to transitions
    except IndexError: pass
    
    return t

def make_mapping(t):
    return t
    
def make_prefix_trans(t):

    #! deprecated for now
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

    return t


def make_PH_trans(t):
    return t
    

def generate_transitions(mapping, context=""):
    
    rule = Rule.rule(mapping, context)  
    t = Delta(rule)
    
    t = make_context_trans(t)
    #t = make_mapping(t)
    #t = make_prefix_trans(t)
    #t = make_PH_trans(t)
    return t

#t1 = generate_transitions(("x", "b"), "a a a c a b _")
#t1.display_transitions()

t2 = generate_transitions(("x", "y"), "a b _ c d")
t2.display_transitions()


 

    
    
    
    

# future composition code 👀
# class Test(str):
    
#     def __matmul__(self, B):
#         A = self
#         return Test(A + B)
# A = Test("hello")
# B = Test("hi")
# print(A @ B)