from dataclasses import dataclass
from utils.funcs import subslices


@dataclass
class Rule:
    
    insym:str
    outsym:str
    context:list
    ctype:str
    k:int
    
    @property
    def statelabels(self):
        return subslices(self.context)
    
    @classmethod
    def rule(cls, mapping:tuple[str], context):
        
        insym, outsym = mapping[0], mapping[1]
        context = context.split()
        
        index = context.index("_")
        ctype = "left" if index == len(context)-1 else "right" if index == 0 else "dual"
        
        k = len(context)
        
        return cls(insym, outsym, context, ctype, k)
    
    
rule = Rule.rule(("a", "b"), "a c a b _")



    

 
    
    

    
    
    
    
    
    
