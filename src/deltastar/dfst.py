# -*- coding: utf8 -*-

# Eric Sclafani

cfx = lambda string: f"<{string}>"                # circumfix func
dfx = lambda string: string.strip("<").strip(">") # de-circumfix func
    
class DFST:
    
    def __init__(self, s1:str, s2:str, contexts=[], v0=""):
        
        self.q0 = "<>"                          
        self.v0 = v0
        self.s1 = s1
        self.s2 = s2  
        self.contexts = contexts                      
        self.delta, self.state_names = self.generate_delta(self.s1, self.s2, self.contexts)
        self.Q = list(self.delta.keys())        
        
        self.sigma = set(sym for transitions in self.delta.values() for sym in transitions.keys())            
        self.gamma = set(sym[1] for transitions in self.delta.values() for sym in transitions.values())           
    
    def display_params(self):
        """ Prints out sigma, gamma, q0, v0, Q, F, delta"""
        
        print(f"\nRewrite rule: {self.s1} -> {self.s2} / {'_' if not self.contexts else self.contexts}") #! needs to account for multiple mappings
        
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {self.Q}\nq0: {self.q0}\nv0: {self.v0}\nF: Not implemented yet")
        
        print(f"{'~'*7}Delta:{'~'*7}")
        
        for state, trans in sorted(self.delta.items()):
            for s, t in trans.items():
                print(f"{state} --({s} : {t[1]})--> {t[0]}")
        print("~"*20,"\n")
        
        
    def generate_delta(self, s1, s2, contexts):
        
        
        IN, OUT = s1.split(), s2.split()
        if not IN or not OUT:
            raise NotImplementedError("Insertion and deletion rules not implemented yet. Stay tuned!")
            
        delta = {}
        state_names = set()
        
        
        for con in contexts: 
            for _in, _out in zip(IN, OUT):
                
                CON = con.split("_") # splits the current context into a double. right side empty == left context rule, left side empty == right context rule
                
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ this block generates all left context transitions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if CON[0]: 
                    next_state = ""                 
                    left_context = CON[0]
                    previous_state = self.q0 
                    
                    for sym in left_context:                           
                        next_state += sym 
                        state_names.add((next_state, "LCON"))
                        
                        if previous_state not in delta:
                            delta[previous_state] = {sym : [cfx(next_state), sym]}
                        else:
                            delta[previous_state][sym] = [cfx(next_state), sym]
                        delta[previous_state]["?"] = [self.q0, "?"] # unspecified transitions. ? is a placeholder cf Chandlee 2014
                           
                        if len(next_state) == 1: # first symbol in a context can be repeated arbitrary times
                            delta[cfx(next_state)] = { sym: [cfx(next_state), sym]}
                        
                        previous_state = cfx(next_state)
                          
                    #! CURRENT BUG: transduction transition is being overwritten when mutiple mappings are specified.          
                    # in change state (state that has a transduction transition)
                    if cfx(_in) in delta and cfx(_in) != previous_state: # transition back to state corresponding to _in symbol
                        #delta[previous_state] = {_in : [cfx(_in), _out]}
                        delta[previous_state][_in] = [cfx(_in), _out]
                        
                    else: 
                        delta[previous_state][_in] = [self.q0, _out]
                     
                    delta[previous_state]["?"] = [self.q0, "?"]

                    print(delta)   
                    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ this block generates all right context transitions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if CON[1]:
                    
                    next_state = "" # rebuild state names symbol by symbol       
                    right_context = _in + CON[1] # input symbol is always the first contextual transition. Also don't want to include the last symbol in context when generating states
                    previous_state = self.q0
                    
                    for sym in right_context[:-1]:
                        
                        next_state += sym
                        state_names.add((next_state,"RCON"))
                        
                        if previous_state not in delta:
                            delta[previous_state] = {sym : [cfx(next_state),"λ"]} # all transitions moving to the right will output the empty string 
                        else:
                            delta[previous_state][sym] = [cfx(next_state),"λ"]
                            
                        if previous_state == self.q0: 
                            delta[previous_state]["?"] = [self.q0, "?"] # puts ?:? self loop on initial state
                        else:
                            delta[previous_state]["?"] = [self.q0, dfx(previous_state) +"?"] 
                            
                        
                        if len(next_state) == 1: # first symbol in a context can be repeated arbitrary times
                            delta[cfx(next_state)] = { sym: [cfx(next_state), sym]}
                            
                        previous_state = cfx(next_state)
                    
                    # in change state
                    delta[previous_state] = {right_context[-1] : [self.q0, _out+CON[1]]}
                    delta[previous_state]["?"] = [self.q0, next_state+"?"]
                
                
                #! I needed to separate context and prefix transitions in order to account for multiple contexts specified at once
                #! i.e. it is possible to transition from one rewrite rule state to a different rewrite rule state (totally not confusing :P)
                # this loop generates all extra transitions 
                
                
                # for state in state_names: # for every state, find all possible prefix transitions
                #     prefix= ""
                #     for char in state:
                #         prefix += char
                        
                #         # this block attempts to find prefix level transitions
                #         if cfx(prefix) in delta and prefix != state: # check if <prefix> state exists and disallow inadvertent self loops
                #             try:
                #                 delta[cfx(state)][prefix[-1]]
                #             except KeyError:
                #                 # very important check: if the last symbol of the state + current char == the prefix. Without this check, false transitions can be created
                #                 if state[-1] + char == prefix:
                #                     delta[cfx(state)][prefix[-1]] = [cfx(prefix), prefix[-1]]
                                
                #         # this block attempts to find character level transitions 
                #         # (needed because the above prefix handling stops on the last character aka when prefix == state. The last character can hold a transition)
                #         try:
                #             delta[cfx(state)][char] # check if outgoing transition already exists with input char from state
                #         except KeyError:
                #             if cfx(char) in delta:
                #                 delta[cfx(state)][char] = [cfx(char), char]
        
        # context free rules              
        if not contexts:
            for _in, _out in zip (IN, OUT):  
                delta[self.q0] = {_in : [self.q0, _out]}
                delta[self.q0]["?"] = [self.q0, "?"]            
        return delta, state_names         
    
    
    def add_transition(self, trans:tuple):
        #! untested
        prev_state, next_state = trans[0], trans[2]
        in_symbol, out_symbol = trans[1], trans[3]
        
        try:
            self.delta[prev_state][in_symbol] = [next_state, out_symbol]
        except KeyError:
            self.delta[prev_state] = {in_symbol: [next_state, out_symbol]}    
    
    def remove_transition(self, trans:tuple):
        pass
        
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
        for pair in self.state_names:
            if pair[1] == "RCON":
                if pair[0] == dfx(state):
                    output += pair[0]
                
        return output
 


test2 = DFST("a", "b", ["_c",])
test2.display_params()
print(test2.rewrite("aaaaac"))


