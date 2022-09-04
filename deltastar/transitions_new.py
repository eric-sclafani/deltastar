from dataclasses import dataclass
from utils.funcs import subslices


@dataclass
class Rule:
    
    insym:str
    outsym:str
    context:str
    ctype:str # context type
    mtype:str # map type
    
    def __repr__(self):
        context = "_" if not self.context else self.context
        return f"{self.insym} -> {self.outsym} / {context}"
    
    @property
    def statelabels(self):
        
        if self.ctype == "cf":
            context  = ""
        
        elif self.ctype == "left": # exclude underscore
            context = self.context[:-1]
            
        elif self.ctype == "right": # include insym as first symbol and exclude underscore and last context symbol
            context = self.insym + self.context[1:-1]
            
        elif self.ctype == "dual":
            leftcon = self.context.split("_")[0].strip()
            rightcon = self.context.split("_")[1].strip()
            
            context = leftcon + " " + (self.insym + " " + rightcon[:-1])
            
        context = context.split()  
        return (["λ"],) + subslices(context) 
    
    @classmethod
    def rule(cls, mapping:tuple[str], context=""):
        insym, outsym = mapping
        context_list = context.split()
        
        if context: 
            index = context_list.index("_")
            ctype =  "left" if index == len(context_list)-1 else "right" if index == 0 else "dual"  
        else:
            ctype = "cf"       
        
        mtype = "delete" if not outsym else "insert" if not insym else "rewrite"  
        return cls(insym, outsym, context, ctype, mtype)
    
    
rule = Rule.rule(("x", "y"), "_ b a b")
print(rule)
print(rule.ctype)
print(rule.statelabels)






    

 
    
    

    
    
    
    
    
    
