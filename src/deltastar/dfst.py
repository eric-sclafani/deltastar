# -*- coding: utf8 -*-

# Eric Sclafani
    
class DFST:
 
    
    def __init__(self, s1:str, s2:str, contexts=[], v0=""):
        
        self.q0 = "<>"                          
        self.v0 = v0
                                   
        self.delta = self.generate_delta(s1, s2, contexts)
        self.Q = list(self.delta.keys())        
        # self.F = F           
        
        self.sigma = set(sym for transitions in self.delta.values() for sym in transitions.keys())            
        self.gamma = set(sym[1] for transitions in self.delta.values() for sym in list(transitions.values()))           
    
     
    def display_params(self):
        """ Prints out sigma, gamma, q0, v0, Q, F, delta"""
        
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {self.Q}\nq0: {self.q0}\nv0: {self.v0}\nF: Not implemented yet")
        print(f"{'~'*7}Delta:{'~'*7}")
        
        for state, trans in sorted(self.delta.items()):
            for s, t in trans.items():
                print(f"{state} --({s} : {t[1]})--> {t[0]}")
        print("~"*20)
        
        
    def generate_delta(self, s1, s2, contexts):
    
        IN, OUT = s1.split(), s2.split()
    
        if not OUT: # deletion rules
            OUT = ("λ " *len(IN)).strip().split()
    
        delta = {}
        state_names = []
        cfx = lambda string: f"<{string}>" 
        
        
        for CON in contexts: 
            for _in, _out in zip(IN, OUT):
                
                
                
                current_state = ""             
                left_context = CON[:CON.find("_")]
                previous_state = self.q0
                
            
                # this loop generates all context transitions
                for sym in left_context:                           
                    current_state += sym 
                    state_names.append(current_state)
                    
                    if previous_state not in delta:
                        delta[previous_state] = {sym : [cfx(current_state), sym]}
                    else:
                        delta[previous_state][sym] = [cfx(current_state), sym]
                    delta[previous_state]["?"] = [self.q0, "?"] # unspecified transitions. ? is a placeholder cf Chandlee 2014
                            
                    if len(current_state) == 1: # first symbol in a context can be repeated arbitrary times
                        delta[cfx(current_state)] = { sym: [cfx(current_state), sym]}
                        
                    previous_state = cfx(current_state)
                    
                # in change state (state that has a transduction transition)
                if cfx(_in) in delta and cfx(_in) != previous_state: # transition back to state corresponding to _in symbol, or initial state
                    delta[previous_state] = {_in : [cfx(_in), _out]}
                else:
                    delta[previous_state] = {_in : [self.q0, _out]}
                delta[previous_state]["?"] = [self.q0, "?"]
                
                
                #! I needed to separate context and prefix transitions in order to account for multiple contexts specified at once
                #! i.e. it is possible to transition from one rewrite rule state to a different rewrite rule state (totally not confusing :P)
                
                # this loop generates all extra transitions
                for state in state_names: # for every state, find all possible prefix transitions
                    prefix= ""
                    for char in state:
                        prefix += char
                        
                        # this block attempts to find prefix level transitions
                        if cfx(prefix) in delta and prefix != state: # check if <prefix> state exists and disallow inadvertent self loops
                            try:
                                delta[cfx(state)][prefix[-1]]
                            except KeyError:
                                # very important check: if the last symbol of the state + current char == the prefix
                                # without this check, false transitions can be created
                                if state[-1] + char == prefix:
                                    delta[cfx(state)][prefix[-1]] = [cfx(prefix), prefix[-1]]
                                
                        # this block attempts to find character level transitions 
                        # (needed because the above prefix handling stops on the last character aka when prefix == state. The last character can hold a transition)
                        try:
                            delta[cfx(state)][char] # check if outgoing transition already exists with input char from state
                        except KeyError:
                            if cfx(char) in delta:
                                delta[cfx(state)][char] = [cfx(char), char]
                                
        # context free rules              
        if not contexts:
            for _in, _out in zip (IN, OUT):  
                delta[self.q0] = {_in : [self.q0, _out]}
                delta[self.q0]["?"] = [self.q0, "?"]
                        
        return delta    
        
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
                output += self.delta[state][char][1] 
                state = self.delta[state][char][0]
            except: # if not found, use the placeholder transition
                state = self.delta[state]["?"][0]
                output += char
            
        output = output.replace("λ", "") # lambda replacing for deletion rules (see rewrite function for more details)
        
        return output
 


test2 = DFST("a", "b", ["c_", "x_"])
test2.display_params()
print(test2.rewrite("caxa"))


