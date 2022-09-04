from dataclasses import dataclass
from utils.funcs import subslices


@dataclass
class Rule:
    
    insym:str
    outsym:str
    context:list
    ctype:str # context type
    mtype:str # map type
    mindex:int # map index
    
    def __repr__(self):
        return f"{self.insym} -> {self.outsym} / {' '.join(self.context)}"
    
    @property
    def statelabels(self):
        
        if self.ctype == "left":
            context = self.context[:-1]
            
        return subslices(context) # exclude the underscore
    
    @classmethod
    def rule(cls, mapping:tuple[str], context):
        
        insym, outsym = mapping
        context = context.split()
        index = context.index("_")
        
        ctype = "left" if index == len(context)-1 else "right" if index == 0 else "dual"           
        mtype = "delete"if not outsym else "insert" if not insym else "rewrite"  
        
        return cls(insym, outsym, context, ctype, mtype, index)
    
    
rule = Rule.rule(("b", "d"), "a c a b _")
print(rule.statelabels)



    

 
    
    

    
    
    
    
    
    
