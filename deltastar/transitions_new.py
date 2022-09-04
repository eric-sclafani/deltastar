from dataclasses import dataclass
from typing import Tuple

class State:
    
    label:str

    def __len__(self):
        return len(self.label)

    def __repr__(self):
        return self.label
    
    def __getitem__(self, idx):
        string = self.label
        if isinstance(idx, slice): # idx is a slice object in this case
            start,stop,step = idx.indices(len(string))
            return "".join([string[i] for i in range(start,stop,step)])
        else:
            return string[idx]

@dataclass
class Rule:
    
    mapping:Tuple[str]
    context:str
    ctype:str
    k:int
    
    @property
    def statelabels(self):
        pass
    
    
    @classmethod
    def rule(cls, ):
        pass
    
    
    
    
    
    
