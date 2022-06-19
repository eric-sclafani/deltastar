
# Eric Sclafani
from collections import defaultdict
from more_itertools import collapse
import pydot
from transitions import get_transitions, dfx, cfx
  
class DFST:

    def __init__(self, s1:str, s2:str, contexts=[], v0=""):
        
        if not isinstance(s1, str) or not isinstance(s2,str):
            raise TypeError("s1 and s2 must be of type 'str'")
        if not isinstance(contexts,list):
            raise TypeError("contexts must be of type 'list'")
        
        if "λ" in s1 or "λ" in s2 or "λ" in "".join(contexts):
            raise ValueError("'λ' is a reserved symbol and cannot be used in rewrite rules")
        if "ψ" in s1 or "ψ" in s2 or "ψ" in "".join(contexts):
            raise ValueError("'ψ' is a reserved symbol and cannot be used in rewrite rules")
        if "Ø" in s1 or "Ø" in s2 or "Ø" in "".join(contexts):
            raise ValueError("'Ø' is a reserved symbol and cannot be used in rewrite rules")

        
        self.q0 = "<λ>"                          
        self.v0 = v0
        self.s1 = s1
        self.s2 = s2  
        self.contexts = contexts                      
        self.delta = self._generate_delta(self.s1, self.s2, self.contexts)
        self.finals = self._finals()
        self.Q = list(self.delta.keys())         
    
    def _generate_delta(self, s1, s2, contexts):
        
        states = set()
        delta = defaultdict(lambda: defaultdict(dict))
        transitions = get_transitions(s1, s2, contexts)
        
        for trans in transitions:
            prev_state, in_sym, next_state, out_sym = trans
            states.add(dfx(prev_state))
            delta[prev_state][in_sym] = [next_state, out_sym]
            
        #! ~~HIGHLY WIP~~~: some prefix transitions are still incorrect / not generated. Prefix transitions will be overhauled in a future update
        # prefix transitions: need to do them here instead of transitions.py bc I need access to the delta dict
        for state in states:
            
            prefix = ""
            for sym in state:
                prefix += sym # rebuild preix state name symbol by symbol
                
                # prefix level transitions
                if prefix != state: # disallow self looping transitions (aka stops before it reaches last symbol of state
                    if not delta[cfx(state)].get(prefix[-1]): # check to see if current state does not already have an outgoing transition with last symbol of prefix
                        if state[-1] + sym == prefix: # very important check: if the last symbol of the state + current symbol == the prefix. Without this check, false transitions can be created
                            delta[cfx(state)][prefix[-1]] = [cfx(prefix), prefix[-1]]
                        
                # character level transitions (need these too since the prefix level doesn't capture all possible transitions)
                if not delta[cfx(state)].get(sym) and state != "λ": # check if outgoing transition already exists with input char from state and disallow q0 self loop                       
                    if sym != state and cfx(sym) in delta: 
                        delta[cfx(state)][sym] = [cfx(sym), sym]
        return delta
    
    def _finals(self):
        states = []
        right = False
        
        # checks to see if the machine is strictly right context:
        # after collapsing, if second entry == lambda, then we know for sure it's a right context and not a dual one
        # need to do this because dual contexts have different rules for state outputs than strictly right
        check_right = list(collapse([val for state, transition in self.delta.items() for val in transition.values()]))
        if check_right[1] == "λ":
            right = True
        
        for state, transitions in self.delta.items():
            seen_left_context = ""
            for in_sym, out_trans in transitions.items():
                
                if right:
                    if out_trans[1] == "λ":
                        state_output = dfx(out_trans[0])
                        states.append((out_trans[0], state_output))   
                         
                else: # is a dual context
                    # this condition block keeps track of left contexts and subtracts them from right context state names when processing a dual context
                    if out_trans[1] != "λ" and in_sym not in seen_left_context and in_sym != "ψ" and in_sym == out_trans[1]:
                        seen_left_context += in_sym
                        
                    elif out_trans[1] == "λ": 
                        if dfx(out_trans[0]).startswith(seen_left_context) and seen_left_context != dfx(out_trans[0]): 
                            
                            state_output = dfx(out_trans[0]).replace(seen_left_context,"",1)
                        else:
                            state_output = dfx(out_trans[0]) 
                        states.append((out_trans[0], state_output))
        return states
                
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
        """manually removes a transition from delta. Note: removing certain transitions can break the FST.

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
                
                if not extra_edges and in_sym == "ψ":
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
                sym = self.delta[state]["ψ"][1]
                output += sym.replace("ψ", char)
                state = self.delta[state]["ψ"][0]
        
        for final in list(filter(lambda x: x[0] == state, self.finals)):# final string concatenation 
            if state == final[0]:
                output += final[1]
        
        if not self.s2:   
            output = output.replace("Ø", "") # deletion rules  
            
        return self.v0 + output





