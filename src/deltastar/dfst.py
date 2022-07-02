
# Eric Sclafani
from collections import defaultdict
import pydot
from transitions import get_transitions, dfx, cfx, PH
  
class DFST:

    def __init__(self, pairs:list[str], contexts=[], v0=""):
        
        #! change this architecture to be compatible with dataclass?
        self.q0 = "<λ>"                          
        self.v0 = v0
        self.pairs = pairs
        self.contexts = contexts                      
        self.delta = self._generate_delta(self.pairs, self.contexts)
        self.Q = list(self.delta.keys())         
        
    def __repr__(self):
        
        if self.contexts:
        
            rules = f"{x} -> {y} / {}"
            
    
    def _generate_delta(self, pairs,contexts):
        
        delta = defaultdict(lambda: defaultdict(dict))
        transitions = get_transitions(pairs, contexts)
        
        for trans in transitions:
            start, insym = trans.start.label, trans.insym
            end, outsym = trans.end, trans.outsym 
            delta[start][insym] = [end, outsym]
                
    @property
    def sigma(self):
        return set(sym for transitions in self.delta.values() for sym in transitions.keys())  
    @property
    def gamma(self):
        return set(sym[1] for transitions in self.delta.values() for sym in transitions.values()) 
    
    @property                  
    def displayparams(self):
        """ Prints rewrite rule, sigma, gamma, Q, q0, v0, F, delta""" 
        
        print(f"\nRewrite rule: {self.s1} -> {self.s2 if self.s2 else 'Ø'} / {self.contexts if self.contexts else '_'}")
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {set(self.Q)}\nq0: {self.q0}\nv0: {None if not self.v0 else self.v0}\nF:{self.finals}")
        
        print(f"{'~'*7}Delta:{'~'*7}")
        
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
                print(f"{state} --( {s} : { t[1]} )--> {t[0]}")
        print("~"*20,"\n")
    
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
        
    def to_graph(self, file_name="my_machine.png",window=False, extra_edges=True):
         
        if not file_name.endswith(".png"):
            raise ValueError("only .png files can be exported")
        
        graph = pydot.Dot("finite_state_machine", graph_type="digraph", rankdir="LR", size="6!")
        graph.add_node(pydot.Node("initial", shape="point", color="white"))
        
        i = 0
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                
                if not extra_edges and in_sym == PH:
                    continue
                
                prev_state = dfx(state)
                next_state = dfx(out_trans[0])
                
                if cfx(prev_state) == self.q0 and i == 0: # i enforces that this edge only gets created once
                    graph.add_edge(pydot.Edge("initial", prev_state))
                
                # if we have right context transitions, states need to output themselves
                for final in self.finals:
                    if cfx(prev_state) == final[0]: 
                        prev_state = f"{prev_state}\,{final[1]}"
                        
                    if cfx(next_state) == final[0]:
                        next_state = f"{next_state}\,{final[1]}"
                          
                graph.add_node(pydot.Node(prev_state, shape="doublecircle"))
                graph.add_node(pydot.Node(next_state, shape="doublecircle"))
                graph.add_edge(pydot.Edge(prev_state, next_state, label=f"{in_sym}\:{out_trans[1]}"))
                i += 1
                
        graph.write_png(file_name)
    
    def rewrite(self, s):
        """ Given string s, perform transductions on it according to self.delta
        
        Args:
            s (str): string to undergo specified transformations
            
        Returns:
            output (str): transformed string
        """
        output = ""
        state = self.q0
        
        for char in s:  
            try: # attempt to find context transitions
                sym = self.delta[state][char][1] 
                output += sym if sym != "λ" else ""
                state = self.delta[state][char][0]
                
            except KeyError: # if not found, use the placeholder transition and replace placeholder with char
                sym = self.delta[state][PH][1]
                output += sym.replace(PH, char)
                state = self.delta[state][PH][0]
        
        # for final in list(filter(lambda x: x[0] == state, self.finals)):# final string concatenation 
        #     if state == final[0]:
        #         output += final[1]
        
        #! no longer working
        # if not self.s2:   
        #     output = output.replace("Ø", "") # deletion rules  
            
        return self.v0 + output
    
    
    
    
    
#! write a function that will parse the useres specified rules and return a DFST object
    
doubles = [
    ("a", "b"),
    ("x", "y")
]    
    
d = DFST(doubles, ["r_"])

d.displayparams





