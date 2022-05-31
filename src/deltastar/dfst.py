# -*- coding: utf8 -*-

from collections import defaultdict
import PySimpleGUI as sg
import pydot


# Eric Sclafani

cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func
    
class DFST:
    
    def __init__(self, s1:str, s2:str, contexts=[], v0=""):
        
        self.q0 = "<λ>"                          
        self.v0 = v0
        self.s1 = s1
        self.s2 = s2  
        self.contexts = contexts                      
        self.delta = self.generate_delta(self.s1, self.s2, contexts)
        self.Q = list(self.delta.keys())        
        
        self.sigma = set(sym for transitions in self.delta.values() for sym in transitions.keys())            
        self.gamma = set(sym[1] for transitions in self.delta.values() for sym in transitions.values())           
    
    def display_params(self):
        """ Prints out sigma, gamma, q0, v0, Q, F, delta"""
        
        print(f"\nRewrite rule: {self.s1} -> {self.s2} / {'_' if not self.contexts else self.contexts}") #! needs to account for multiple mappings
        
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {self.Q}\nq0: {self.q0}\nv0: {self.v0}\nF: Not implemented yet")
        
        print(f"{'~'*7}Delta:{'~'*7}")
        
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
                print(f"{state} --({s} : {t[1]})--> {t[0]}")
        print("~"*20,"\n")
        
        
    def generate_transitions(self, s1, s2, contexts):
        
        
        IN, OUT = s1.split(), s2.split()
        if not IN or not OUT:
            raise NotImplementedError("Insertion and deletion rules not implemented yet. Stay tuned!")
        
        delta = []
        
        for con in contexts: 
            for _in, _out in zip(IN, OUT):
                CON = con.split("_") # splits the current context into a double. right side empty == left context rule, left side empty == right context rule
   
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ this block generates all left context transitions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if CON[0]: 
                    next_state = "" # rebuild state names symbol by symbol               
                    left_context = CON[0]
                    previous_state = self.q0 
                    
                    for sym in left_context:                           
                        next_state += sym 
                        
                        delta.append( (previous_state, sym, cfx(next_state), sym) )
                        delta.append( (previous_state, "?", self.q0, "?") ) # unspecified transitions. ? is a placeholder cf Chandlee 2014
                        
                        if len(next_state) == 1: # beginning of context can repeat arbitrary number of times
                            delta.append( (cfx(next_state), sym, cfx(next_state), sym) )
                        
                        previous_state = cfx(next_state) # update previous_state 
                        
                        if next_state == left_context: # reached the last state of context
                            delta.append( (previous_state, _in, self.q0, _out) )
                            delta.append( (previous_state, "?", self.q0, "?") )
                            
                        
                            
                        #     if cfx(_in) in delta and cfx(_in) != previous_state: # transition back to state corresponding to _in symbol
                        #         delta[previous_state][_in] = [cfx(_in), _out] 
                        #     else: 
                        #         delta[previous_state][_in] = [self.q0, _out]
                            
                        #     delta[previous_state]["?"] = [self.q0, "?"]
                    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ this block generates all right context transitions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if CON[1]:
                    next_state = ""       
                    right_context = _in + CON[1] # input symbol is always the first contextual transition. Also don't want to include the last symbol in context when generating states
                    previous_state = self.q0
                    
                    for sym in right_context[:-1]:
                        next_state += sym

                        delta.append( (previous_state, sym, cfx(next_state), "λ") ) # all transitions moving to the right will output the empty string
                        if previous_state == self.q0:
                            delta.append( (previous_state, "?", self.q0, "?") ) # initial state gets a ?:? transition
                        else:
                            delta.append( (previous_state, "?", self.q0, dfx(previous_state) + "?") ) # if unknown symbol, need to output the state name along with '?'
                        
                        if len(next_state) == 1: # beginning of context can repeat arbitrary number of times
                            delta.append( (cfx(next_state), sym, cfx(next_state), sym) )
                            
                        previous_state = cfx(next_state) # update previous_state
                        
                        if next_state == right_context[:-1]: # reached the last state of context
                            delta.append( (previous_state, right_context[-1] , self.q0, _out+CON[1]) )
                            delta.append( (previous_state, "?", self.q0, next_state + "?") )
                   
        # context free rules              
        if not contexts:
            for _in, _out in zip (IN, OUT): 
                delta.append((self.q0, _in, self.q0, _out))
                delta.append((self.q0, "?", self.q0, "?"))
                 
        return delta     
    
    def generate_delta(self, s1, s2, contexts):
        
        delta = defaultdict(lambda: defaultdict(dict))
        transitions = self.generate_transitions(s1, s2, contexts)
        
        for trans in transitions:
            prev_state, in_sym, next_state, out_sym = trans
            delta[prev_state][in_sym] = [next_state, out_sym]
            
        return delta
    
    
    def add_transition(self, trans:tuple):
        #! untested
        assert len(trans) == 4, "transition must be input as (prev_state, in_symbol, next_state, out_symbol)"
        prev_state, in_symbol, next_state, out_symbol = trans
        self.delta[prev_state][in_symbol] = [next_state, out_symbol]
           
    
    def remove_transition(self, trans:tuple):
        pass
    
    def to_graph(self, graph_name="my_machine.png", show=False):
        
        if not graph_name.endswith(".png"):
            raise ValueError("only .png files can be exported")
        
        graph = pydot.Dot("finite_state_machine", graph_type="digraph", rankdir="LR")
        graph.add_node(pydot.Node("initial", shape="point"))
        #! need to add final functions to output somehow 
        
        i = 0
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                graph.add_node(pydot.Node(dfx(state), shape="circle",))
                
                if state == self.q0 and i == 0: # the i here enforces that this edge only gets created once
                    graph.add_edge(pydot.Edge("initial", dfx(state)))
                
                graph.add_node(pydot.Node(dfx(out_trans[0]), shape="circle"))
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
                
        # final function
        #! no longer working
        for pair in self.state_names:
            if pair[1] == "RCON":
                if pair[0] == dfx(state): # if we land in a right context state, output that states name
                    output += pair[0]
                
        return output
 


test2 = DFST("a", "b", ["_c",])
test2.display_params()
test2.to_graph()