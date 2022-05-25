# -*- coding: utf8 -*-

# Eric Sclafani
    
class DFST:
    """ 
    This class contains code for constructing deterministic finite-state string to string transducers
    
    Attributes:
    
        delta (dict): dict containing all possible transitions in the machine
        
        F (tuple): final function (not implemented yet, code is outdated)
        
        q0 (str): starting state
        
        v0 (str): starting string
        
    Methods:
        
        sigma: acquires all input symbols and puts them into a set
        
        gamma: acquires all output symbols and puts them into a set
        
        final (F): not implemented yet
        
        displayparams: prints the parameters of a DFST (sigma, gamma, q0, v0, F, Q, delta)
        
        T (s): given a string, performs transductions using delta's transitions
    
    """  
    
    def __init__(self, delta, F=(), q0="<>", v0=""):
        """ Constructs DFST parameters
        
        Arguments:
        
            delta (dict): dict of transitions
            
            F (tuple): final function, (not implemented yet, code is outdated)
            
            q0 (str): starting state
            
            v0 (str): starting string
             
        Other instantiations:
        
            Q (list): list of all states
            
            sigma (set): set of all input symbols
            
            gamma (set): set of all output symbols
        """
        self.q0 = q0                            
        self.v0 = v0                            
        self.delta = delta
        self.Q = list(self.delta.keys())        
        self.F = self.final(F)                  
        
        self.sigma = self.sigma()              
        self.gamma = self.gamma()              
    
    def sigma(self):
        """ Acquires the set of all input symbols from delta

        Returns:
            set of all input symbols.
        """
        return set(sym for transitions in self.delta.values() for sym in transitions.keys())
    
    def gamma(self):
        """Acquires the set of all output symbols from delta
            
        Returns:
            set of all output symbols.
        """
        return set(sym[1] for transitions in self.delta.values() for sym in list(transitions.values()))
    
    def final(self, F):
        """Not implemented yet. Will be returned to when right sided contexts are implemented"""
        
        # outdated code
        # ~~~ HIGHLY WIP ~~~
        
        # if not isinstance(F, tuple):
        #     raise TypeError(f"{F} must be of type 'tuple'")
        # if len(F) == 1 or len(F) >2:
        #     raise Exception(f"{F} must be empty or of format (STATE, STRING)") 
           
        # return { str(F[0]) : F[1] } if F else ()
        return ""
    
         
    def display_params(self):
        """ Prints out sigma, gamma, q0, v0, Q, F, delta"""
        
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {self.Q}\nq0: {self.q0}\nv0: {self.v0}\nF: {self.F}")
        print(f"{'~'*7}Delta:{'~'*7}")
        
        for state, trans in sorted(self.delta.items()):
            for s, t in trans.items():
                print(f"{state} --({s} : {t[1]})--> {t[0]}")
        print("~"*20)
    
    def T(self, s):
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
                
        # appends final string if current state in F else empty string (outdated)
        output += self.F[state] if state in self.F else ""
        output = output.replace("λ", "") # lambda replacing for deletion rules (see rewrite function for more details)
        
        return output
 
def generate_transitions(q, contexts, IN, OUT):
    
    
    delta = {}
    state_names = []
    cfx = lambda string: f"<{string}>" 
    
    # context sensitive rules
    for CON in contexts: 
        for _in, _out in zip(IN, OUT):
            current_state = ""             
            context = CON[:CON.find("_")]
            previous_state = q  
            
            #! I needed to separate context and prefix transitions in order to account for multiple contexts specified at once
            #! i.e. it is possible to transition from one rewrite rule state to a different rewrite rule state (totally not confusing :P)
            
            # this loop generates all context transitions
            for sym in context:                           
                current_state += sym 
                state_names.append(current_state)
                
                if previous_state not in delta:
                    delta[previous_state] = {sym : [cfx(current_state), sym]}
                else:
                    delta[previous_state][sym] = [cfx(current_state), sym]
                delta[previous_state]["?"] = [q, "?"] # unspecified transitions. ? is a placeholder cf Chandlee 2014
                         
                if len(current_state) == 1: # first symbol in a context can be repeated arbitrary times
                    delta[cfx(current_state)] = { sym: [cfx(current_state), sym]}
                    
                previous_state = cfx(current_state)
                
            # in change state (state that has a transduction transition)
            if cfx(_in) in delta and cfx(_in) != previous_state: # transition back to state corresponding to _in symbol, or initial state
                delta[previous_state] = {_in : [cfx(_in), _out]}
            else:
                delta[previous_state] = {_in : [q, _out]}
            delta[previous_state]["?"] = [q, "?"]
            
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
        current_state = "<>"
        for _in, _out in zip (IN, OUT):  
            delta[current_state] = {_in : [current_state, _out]}
            delta[current_state]["?"] = [current_state, "?"]
                       
    return delta

def rewrite (s1:str, s2:str, contexts=[], v0="", displayparams=False) -> DFST:
    """ Given an input, output, and context, this function generates transitions and instantiates a DFST object. Only no or left contexts currently work

    Arguments:
        s1 (str): input symbols to be changed
        
        s2 (str): the ouput symbols to be change into
        
        context (str): context for the change to occur. Empty by default
        
        v0 (str): optional string to prepend the output with (NOTE: may have unexpected consequences regarding context. old code.)
        
        displayparams (bool): when true, displays a DFST's parameters
    
    Returns:
        DFST.T (lambda function): calls DFST.T to enact the transductions generated by rewrite
    
    """
    
    #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  ~~~insert context format handling code here~~~
    #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      
    
    
    IN, OUT = s1.split(), s2.split()
    
    if not OUT: # deletion rules
        OUT = ("λ " *len(IN)).strip().split()
    
    delta = (generate_transitions("<>", contexts, IN, OUT))
      
    fst = DFST(delta, v0=v0, F=())
    
    if displayparams:
        fst.display_params()
        
    return lambda string : fst.T(string)


test1 = rewrite("a", "b", ["a_"], displayparams=True)

test2 = rewrite("a", "b", ["acab_"], displayparams=True)


