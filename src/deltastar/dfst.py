
# Eric Sclafani
from collections import defaultdict
from dataclasses import dataclass
import pydot
from transitions import get_transitions, dfx, cfx, PH
from typing import List
from tabulate import tabulate 


@dataclass
class DFST:
                             
    delta: defaultdict
    rules:List[str]
    v0:str
    q0:str = "<λ>"
           
    def sigma(self):
        return set(sym for transitions in self.delta.values() for sym in transitions.keys())  
    
    def gamma(self):
        return set(sym[1] for transitions in self.delta.values() for sym in transitions.values()) 
    
    def Q(self):
        return list(self.delta.keys())
                    
    def displayparams(self):
        """ Prints rewrite rule, sigma, gamma, Q, q0, v0, F, delta""" 
        
        print(f"\n{'~'*7}Rewrite rules:{'~'*7}")
        for rule in self.rules:
            print(rule)
            
        print("~"*28,"\n")
        print(f"Σ: {self.sigma()}\nΓ: {self.gamma()}\nQ: {set(self.Q())}\nq0: {self.q0}\nv0: {None if not self.v0 else self.v0}\nF: None")
        
        # print(f"{'~'*7}Delta:{'~'*7}")
        
        transitions = []
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
               transitions.append([state, s, t[1], t[0]])
        
        print(tabulate(transitions, headers=["Start", "Insym", "Outsym", "End"]))
    
    def addtransition(self, prev_state:str, in_sym:str, next_state:str, out_sym:str):
        """manually adds a transition to delta

        Args:
            prev_state (str): state where transition begins
            in_sym (str): input string
            next_state (str): state where transition ends
            out_sym (str): output string
        """   
        self.delta[prev_state][in_sym] = [next_state, out_sym]
           
    def removetransition(self, prev_state:str, in_sym:str,):
        """manually removes a transition from delta. 
           Note: removing certain transitions can break the FST completely.

        Args:
            prev_state (str): state to delete a transition from
            in_sym (str): symbol transition to be deleted
        """
        try:
            del self.delta[prev_state][in_sym]
        except KeyError:
            raise KeyError(f"state '{prev_state}' with input symbol '{in_sym}' not found")
        
    def to_graph(self, file_name="my_machine.png", extra_edges=True):
         
        if not file_name.endswith(".png"):
            raise ValueError("only .png files can be exported")
        
        graph = pydot.Dot("finite_state_machine", graph_type="digraph", rankdir="LR", size="6!")
        graph.add_node(pydot.Node("initial", shape="point", color="white"))
        
        i = 0
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                
                if not extra_edges and in_sym == PH:
                    continue
                
                prev_state = state
                next_state = out_trans[0]
                
                if prev_state == self.q0 and i == 0: # i enforces that this edge only gets created once
                    graph.add_edge(pydot.Edge("initial", prev_state))
                
                #! broken
                # # if we have right context transitions, states need to output themselves
                # for final in self.finals:
                #     if cfx(prev_state) == final[0]: 
                #         prev_state = f"{prev_state}\,{final[1]}"
                        
                #     if cfx(next_state) == final[0]:
                #         next_state = f"{next_state}\,{final[1]}"
                          
                graph.add_node(pydot.Node(prev_state, shape="doublecircle"))
                graph.add_node(pydot.Node(next_state, shape="doublecircle"))
                graph.add_edge(pydot.Edge(prev_state, next_state, label=f"{in_sym}\:{out_trans[1]}"))
                i += 1
                
        graph.write_png(file_name)
    
    def rewrite(self, s):
        
        output = ""
        state = self.q0
        
        for char in s.split():  
            try: # attempt to find context transitions
                sym = self.delta[state][char][1] 
                output += sym + " " if sym != "λ" else "" # lambda here for right contexts i think?
                state = self.delta[state][char][0]
                
            except KeyError: # if not found, use the placeholder transition and replace placeholder with char
                sym = self.delta[state][PH][1]
                output += sym.replace(PH, char)
                state = self.delta[state][PH][0]
            
        return self.v0 + output
    

    
def transducer(pairs:List[tuple], contexts=[], v0="") ->  DFST:
    
    IN = [pair[0] for pair in pairs]
    OUT = [pair[1] if pair[1] else "Ø" for pair in pairs] # accounts for deletion rules
    rules = [] # store string representations of rewrite rules 
    
    if contexts: # context dependent rewrile rules
        for con in contexts:
            for _in, _out in zip(IN,OUT):
                rules.append(f"{_in} -> {_out} / {con}")
                     
    else: # context free rewrite rules  
        for _in, _out in zip(IN,OUT):
                rules.append(f"{_in} -> {_out} / _")
    
    delta = defaultdict(lambda: defaultdict(dict))
    transitions = get_transitions(IN, OUT, contexts)
    
    for trans in transitions:
        start, insym = str(trans.start), trans.insym
        end, outsym = str(trans.end), trans.outsym 
        delta[start][insym] = [end, outsym]
        
        
    return DFST(delta, rules, v0)
        

    
    
    
    
    


    
doubles = [
    ("[mod=imp]", "be"),
]    



t = transducer(doubles, ["x_", "y_"])

t.to_graph()


print(t.rewrite("x [mod=imp] y [mod=imp]"))



