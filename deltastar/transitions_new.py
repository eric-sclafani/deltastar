from dataclasses import dataclass
from utils.funcs import subslices
from more_itertools import windowed
from collections import namedtuple

@dataclass
class Rule:
    X:str
    Y:str
    context:str
    ctype:str
    target_context:str
    trigger_sym:str
    mtype:str

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

#! add a state output attribute (use dataclass?)
State = namedtuple("State", "label, ctype, seen_lcon")
Transition = namedtuple("Transition", "start, insym, outsym, end, is_mapping")
    
class Transitions:
    """This constructor holds all transitions and methods for accessing transition attributes"""
    
    def __init__(self, rule):
        self.rule = rule
        self.transitions = []
        
    def display_transitions(self):
        for trans in self.transitions:
            print(f"({trans.start.label} | {trans.insym} -> {trans.outsym} | {trans.end.label})")
    
    def get_maps(self):
        """Retrieves all mapping transitions"""       
        maps = list(filter(lambda x: x.is_mapping, self.transitions))
        return maps
    
    def get_states(self):
        """Retrieves all state labels"""
        return list(map(lambda x: x.start.label and x.end.label, self.transitions))
    
    def get_insyms(self):
        insyms = set(map(lambda x: x.insym, self.transitions))
        insyms.add(self.rule.trigger_sym)
        return insyms
        
    def search_transitions(self, start=None, insym=None, outsym=None, end=None):
        pass
    
    def add_transition(self, start, insym, outsym, end, is_mapping=False):
        self.transitions.append(Transition(start, insym, outsym, end, is_mapping))


def k_prefix_transitions(func):
    def wrapper(mapping, context=""):
        
        t = func(mapping, context)
        last_state = t.rule.get_statelabels()[-1]
        
        
                
                
        
        
        return t
    
    return wrapper
    
    
@k_prefix_transitions  
def generate_transitions(mapping, context):
    
    rule = Rule.rule(mapping, context)  
    t = Transitions(rule)
    for start_, end_ in windowed(rule.get_statelabels(), n=2, fillvalue=None):
        
        if rule.ctype == "cf": # cf is self loop on initial state mapping X to Y
            t.add_transition(start  = State(start_, ctype="cf", seen_lcon=""),
                             insym  = rule.X,
                             outsym = rule.Y,
                             end    = State(start_, ctype="cf", seen_lcon=""), 
                             is_mapping = True)
            
        elif rule.ctype == "left":
            t.add_transition(start  = State(start_, ctype="left", seen_lcon=""),
                             insym  = end_[-1],
                             outsym = end_[-1],
                             end    = State(end_, ctype="left", seen_lcon=""))
        
        
        
        elif rule.ctype == "right":
            pass
        
        elif rule.ctype == "dual":
            pass
        
    return t
    
    

test = generate_transitions(("a", "b"), "a c a b _")




    
    

    
    
    
    
    
    
