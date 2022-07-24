
# Eric Sclafani
from collections import defaultdict
from dataclasses import dataclass
import pydot
from transitions import get_transitions, PH
from typing import List
from tabulate import tabulate 

cfx = lambda string: f"<{string}>"

@dataclass
class DFST:
                             
    delta: defaultdict
    Q:List[str]
    sigma:set
    gamma:set
    rules:List[str]
    v0:str = ""
    q0:str = "<λ>"
    
    @property                    
    def displayparams(self):
        """ Prints rewrite rule, sigma, gamma, Q, q0, v0, F, delta""" 
        
        print(f"\n{'~'*7}Rewrite rules:{'~'*7}")
        print(*self.rules, sep="\n")
        
        print("~"*28,"\n")
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {set(cfx(q) for q in self.Q)}\nq0: {self.q0}\nv0: {None if not self.v0 else self.v0}\nF: Not Implemented Yet")
        
        print(f"Delta:")
        
        transitions = []
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
               transitions.append([cfx(state), s, t[0], cfx(t[1])])
        
        print(tabulate(transitions, headers=["Start", "Insym", "Outsym", "End"], tablefmt="fancy_outline"))
    
    
    
    #! ~~~~~~~~~~~~~~~~~~~~~~~~~~~ BROKEN: NEEDS TO BE UPDATED ~~~~~~~~~~~~~~~~~~~~~~~~
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
                    graph.add_edge(pydot.Edge("initial", str(prev_state)))
                
                #! broken
                # # if we have right context transitions, states need to output themselves
                # for final in self.finals:
                #     if cfx(prev_state) == final[0]: 
                #         prev_state = f"{prev_state}\,{final[1]}"
                        
                #     if cfx(next_state) == final[0]:
                #         next_state = f"{next_state}\,{final[1]}"
                          
                graph.add_node(pydot.Node(str(prev_state), shape="doublecircle"))
                graph.add_node(pydot.Node(str(next_state), shape="doublecircle"))
                graph.add_edge(pydot.Edge(str(prev_state), str(next_state), label=f"{in_sym}\:{out_trans[1]}"))
                i += 1
                
        graph.write_png(file_name)
    
    def rewrite(self, s):
        
        output = ""
        state = self.q0
        
        for char in s.split():  
            try: # attempt to find context transitions
                sym = self.delta[state][char][1] 
                output += sym + " " if sym != "λ" else "" # lambda here for right contexts
                state = self.delta[state][char][0]
                
            except KeyError: # if not found, use the placeholder transition and replace placeholder with char
                sym = self.delta[state][PH][1]
                output += sym.replace(PH, char)
                state = self.delta[state][PH][0]
            
        return self.v0 + output
    
def transducer(pairs:List[tuple], contexts=[], v0="") ->  DFST:
    
    IN = [pair[0] for pair in pairs]
    OUT = [pair[1] if pair[1] else "Ø" for pair in pairs] # accounts for deletion rules
    
    # this condition block acquires the string representations of rewrite rules for displaying
    rules = [] 
    if contexts: # context dependent 
        for con in contexts:
            for _in, _out in zip(IN,OUT):
                rules.append(f"{_in} -> {_out} / {con}")
                     
    else: # context free 
        for _in, _out in zip(IN,OUT):
                rules.append(f"{_in} -> {_out} / _")
    
    
    delta, Q, sigma, gamma = get_transitions(IN, OUT, contexts)
    
    return DFST(delta, Q, sigma, gamma, rules, v0)
        

    

    


    
doubles = [
    ("a", "b"),
]    

# t = transducer(doubles, ["[tns=pst] _ [mod=imp]"])
# t.displayparams

# x = transducer(doubles, ["a c a b _", "c c _"])
# x.displayparams

z = transducer(doubles, ["x y _ m n",])
z.displayparams













    #     for pfxstate in pfx_states:
    #         if delta.get(pfxstate): # if the possible prefix state exists in delta
    #             if pfxstate[-1] == "]": # tag handling
    #                 last_seen_symbol = pfxstate
    #             else:
    #                 last_seen_symbol = pfxstate[-1]  
     
                # if the current state does not already have an outgoing arc with last seen symbol              
    #             if not delta[state].get(last_seen_symbol): 
    #                 delta[state][last_seen_symbol] = [last_seen_symbol, pfxstate]