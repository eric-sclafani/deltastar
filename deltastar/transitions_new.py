from dataclasses import dataclass
from utils.funcs import subslices
from more_itertools import windowed

@dataclass
class Rule:
    
    X:str
    Y:str
    context:str
    ctype:str # context type
    mtype:str # map type
    
    def __repr__(self):
        context = "_" if not self.context else self.context
        return f"{self.insym} -> {self.outsym} / {context}"
    
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
            context = lcon + " " + (self.insym + " " + rcon[:-1])
            
        context = context.split()  
        return ("λ",) + subslices(context) 
    
    def target_context(self):
        return self.context.replace("_", self.X)
    
    @classmethod
    def rule(cls, mapping:tuple[str], context=""):
        X, Y = mapping
        context_list = context.split()
        
        if context: 
            index = context_list.index("_")
            ctype =  "left" if index == len(context_list)-1 else "right" if index == 0 else "dual"  
        else:
            ctype = "cf"  
                 
        mtype = "delete" if not Y else "insert" if not X else "rewrite"  
        return cls(X, Y, context, ctype, mtype)
    
@dataclass
class State:
    label:str
    ctype:str
    seen_lcon:str = ""
    
    def __repr__(self):
        return self.label

@dataclass 
class Transition:
    start:State
    insym:str
    outsym:str
    end:State
    is_mapping:bool = False
    
    def __repr__(self):
        return f"({self.start} | {self.insym} -> {self.outsym} | {self.end})"   


@dataclass
class Delta:
    
    transitions:list
    
    def get_mappings(self):
        
        maps = []
        for t in self.transitions:
            if t.is_mapping:
                maps.append(t)
        return maps
    
    def search_trans(self, start=None, insym=None, outsym=None, end=None):
        pass
    
    @classmethod
    def generate_context_transitions(cls, mapping, context=""):
        
        t = []
        rule = Rule.rule(mapping, context)
        for start_label ,end_label in windowed(rule.get_statelabels(), n=2, fillvalue=None):
            
            if rule.ctype == "cf":
                t.append(Transition(start = State(start_label, ctype="cf"),
                                    insym = rule.X,
                                    outsym = rule.Y,
                                    end = State(start_label, ctype="cf"),
                                    is_mapping=True))
                
            elif rule.ctype == "left":
                pass
            
            elif rule.ctype == "right":
                pass
            
            elif rule.ctype == "dual":
                pass
            
        return cls(t)
    
    
    
    
    
f = Delta.generate_context_transitions(("a", "b"), )


    
    

    
    
    
    
    
    
