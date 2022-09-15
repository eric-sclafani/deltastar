from dataclasses import dataclass
from utils.funcs import subslices, despace
from more_itertools import windowed

@dataclass
class Rule:
    X:str
    Y:str
    context:str
    ctype:str
    target_context:str # unused
    trigger_sym:str # unused
    mtype:str # unused

    def __repr__(self):
        context = "_" if not self.context else self.context
        return f"{self.X} -> {self.Y} / {context}"
    
    def get_statelabels(self):
        
        if self.ctype == "cf":
            context  = ""
        
        elif self.ctype == "left": # exclude underscore
            context = self.context[:-1]
        
        elif self.ctype == "right": # include insym as first symbol and exclude underscore and last context symbol
            context = self.insym + self.context[1:-1]
        
        elif self.ctype == "dual":
            lcon = self.context.split("_")[0].strip()
            rcon = self.context.split("_")[1].strip()
            context = lcon + " " + (self.X + " " + rcon[:-1])
            
        context = context.split()  
        return ("λ",) + subslices(context) 
        
    @classmethod
    def rule(cls, mapping, context=""):
        X, Y = mapping
        context_list = context.split()
        if context: 
            index = context_list.index("_")
            ctype =  "left" if index == len(context_list)-1 else "right" if index == 0 else "dual"  
        else:
            ctype = "cf"  
            
        target_context = context.replace("_", X) if context else None 
        trigger_sym = X if ctype in ["left", "cf"] else target_context[-1]
        mtype = "delete" if not Y else "insert" if not X else "rewrite"  
        
        return cls(X, Y, context, ctype, target_context, trigger_sym, mtype)

@dataclass
class State:
    label:list
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

class Transitions:
    """This constructor holds all transitions and methods for accessing transition attributes"""
    
    def __init__(self, rule):
        self.rule = rule
        self.transitions = []
        
    def get_maps(self):
        """Retrieves all mapping transitions""" 
        maps = list(filter(lambda x: x.is_mapping, self.transitions))
        return maps
    
    def get_statelabels(self):
        """Retrieves all state labels"""
        return list(map(lambda x: x.start.label and x.end.label, self.transitions))
        
    def get_sigma(self):
        insyms = set(map(lambda x: x.insym, self.transitions))
        insyms.add(self.rule.trigger_sym)
        return insyms
        
    def get_trans_with_state(self, state_label):
        return list(filter(lambda x: x.start.label == state_label, self.transitions))
    
    def state_exists_with_insym(self, state_label, pfxsym):
        # if this list is ever populated, then state already has an outgoing arc with pfxsym
        return True if list(filter(lambda x: x.start.label == state_label and x.insym == pfxsym, self.transitions)) else False
    
    def add_transition(self, start, insym, outsym, end, is_mapping=False):
        self.transitions.append(Transition(start, insym, outsym, end, is_mapping))
        
    def display_transitions(self):
        print(*self.transitions, sep="\n")

def add_prefix_transitions(func):
    def wrapper(mapping, context=""):
        
        t = func(mapping, context)
        for q in t.get_statelabels():
            pfxstate = q[1:]
            
            print(f"{q = }")
            while True:
                # concats each sym in sigma with pfxstate and keeps it if it exists in Q
                pfxstates = [pfxstate + [s] for s in t.get_sigma() if pfxstate + [s] in t.get_statelabels()]
                print(f"{pfxstates = }")
                
                #! next check if q already has an outgoing transition with pfxstate[-1]
                for state in pfxstates:
                    pfxsym = state[-1]
                    
                    if t.state_exists_with_insym(q, pfxsym):
                        print(f"\t\tCurrent state: {q} already exists with outsym: {pfxsym}")
                    
                      
                if not pfxstate:
                    break 
                pfxstate = pfxstate[1:]   
            print("\n")
        
                
                
        
        
        return t
    
    return wrapper
    
    
@add_prefix_transitions  
def generate_transitions(mapping, context) -> Transitions:
    
    rule = Rule.rule(mapping, context)  
    t = Transitions(rule)
    
    for start, end in windowed(rule.get_statelabels(), n=2, fillvalue=None):
        if rule.ctype == "cf": # cf is self loop on initial state mapping X to Y
            end = start
            t.add_transition(start  = State(start, ctype="cf", seen_lcon=""),
                             insym  = rule.X,
                             outsym = rule.Y,
                             end    = State(end, ctype="cf", seen_lcon=""), 
                             is_mapping = True)
            
        elif rule.ctype == "left":
            t.add_transition(start  = State(start, ctype="left", seen_lcon=""),
                             insym  = end[-1],
                             outsym = end[-1],
                             end    = State(end, ctype="left", seen_lcon=""))
        
        
        
        elif rule.ctype == "right":
            pass
        
        elif rule.ctype == "dual":
            pass # possibly get rid of "dual" type and treat as left + right??
        
    return t
    
    

test = generate_transitions(("a", "b"), "a a a c a b [mod=imp] _")
#test.display_transitions()


    
    

    
    
    
    
    
    

# future composition code 👀
# class Test(str):
    
#     def __matmul__(self, B):
#         A = self
#         return Test(A + B)
# A = Test("hello")
# B = Test("hi")
# print(A @ B)