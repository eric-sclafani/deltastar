# -*- coding: utf8 -*-

# Eric Sclafani
from collections import defaultdict
import PySimpleGUI as sg
import pydot
from transitions import get_transitions, dfx, cfx

    
class DFST:

    def __init__(self, s1:str, s2:str, contexts=[], v0=""):
        
        self.q0 = "<λ>"                          
        self.v0 = v0
        self.s1 = s1
        self.s2 = s2  
        self.contexts = contexts                      
        self.delta = self._generatedelta(self.s1, self.s2, self.contexts)
        self.finals = self._finals()
        self.Q = set(self.delta.keys())        
    
    def _generatedelta(self, s1, s2, contexts):
        
        delta = defaultdict(lambda: defaultdict(dict))
        transitions = get_transitions(s1, s2, contexts)
        
        for trans in transitions:
            prev_state, in_sym, next_state, out_sym = trans
            delta[prev_state][in_sym] = [next_state, out_sym]
            
        return delta
    
    def _finals(self):
        
        states = []
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                if out_trans[1] == "λ": # if output symbol== lambda, then its a right context transition. Thus, the next_state needs its own output
                    states.append(dfx(out_trans[0]))
        return states
                
    @property
    def sigma(self):
        return set(sym for transitions in self.delta.values() for sym in transitions.keys())  
    @property
    def gamma(self):
        return set(sym[1] for transitions in self.delta.values() for sym in transitions.values()) 
                           
    def displayparams(self):
        """ Prints sigma, gamma, q0, v0, Q, F, delta"""
        
        print(f"\nRewrite rule: {self.s1} -> {self.s2} / {'_' if not self.contexts else self.contexts}")
        
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {self.Q}\nq0: {self.q0}\nv0: {self.v0}\nF: Not implemented yet")
        
        print(f"{'~'*7}Delta:{'~'*7}")
        
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
                print(f"{state} --({s} : {t[1]})--> {t[0]}")
        print("~"*20,"\n")
        
    def addtransition(self, trans:tuple):
        """manually adds a transition to delta

        Args:
            trans (tuple): transition to be added to delta

        Raises:
            TypeError: crashes if user uses anything other than a tuple
            ValueError: crashes if tuple format is invalid
        Returns:
            None - updates delta by reference
            
        Example:

        """
        if not isinstance(trans, tuple):
            raise TypeError("transition must be of type 'tuple'")
        elif len(trans) != 4:
            raise ValueError("transition must be input as (prev_state, in_symbol, next_state, out_symbol)")
        
        prev_state, in_symbol, next_state, out_symbol = trans
        self.delta[prev_state][in_symbol] = [next_state, out_symbol]
           
    
    def removetransition(self, trans:tuple):
        pass
    
    def to_graph(self, graph_name="my_machine.png", show=False):
         
        
        if not graph_name.endswith(".png"):
            raise ValueError("only .png files can be exported")
        
        graph = pydot.Dot("finite_state_machine", graph_type="digraph", rankdir="LR", size="6!")
        graph.add_node(pydot.Node("initial", shape="point", color="white"))
        #! need to add final functions to output somehow 
        
        i = 0
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                graph.add_node(pydot.Node(dfx(state), shape="doublecircle",))
                
                if state == self.q0 and i == 0: # the i here enforces that this edge only gets created once
                    graph.add_edge(pydot.Edge("initial", dfx(state)))
                
                graph.add_node(pydot.Node(dfx(out_trans[0]), shape="doublecircle"))
                graph.add_edge(pydot.Edge(dfx(state),dfx(out_trans[0]),label=f"{in_sym}\:{out_trans[1]}"))
                i += 1
                
        graph.write_png(graph_name)
        
        if show:
            sg.theme("DarkAmber")
            layout = [[sg.Image(graph_name)], [sg.Quit(key="Quit",)]]
            window = sg.Window(graph_name.replace(".png", ""), layout=layout, element_justification="c")
          
            while True: # main event loop
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == "Quit":
                    break
            window.close()
 
    def rewrite(self, s):
        """ Given string s, perform transductions on it according to self.delta
        
        Arguments:
            s (str): string to undergo specified transformations
            
        Returns:
            output (str): new string that has undergone transformations
        """
        output = self.v0
        state = self.q0
        
        for char in s:  
            try: # attempt to find context transitions
                sym = self.delta[state][char][1] 
                output += sym if sym != "λ" else ""
                state = self.delta[state][char][0]
                
            except: # if not found, use the placeholder transition and replace placeholder with char
                sym = self.delta[state]["?"][1]
                output += sym.replace("?", char)
                state = self.delta[state]["?"][0]
                
        # final string concatenation 
        if dfx(state) in self._finals(): # if we land in a right context state, output that states name
            output += dfx(state)
                
        return output
 


test2 = DFST("a", "b", ["c_c"])
test2.displayparams()
# test2.to_graph(show=True)
print(test2.rewrite("aa")) #! crashing