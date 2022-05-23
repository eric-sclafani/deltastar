# -*- coding: utf8 -*-

# Eric Sclafani
    
class DFST:
    """ 
    This class contains code for constructing deterministic finite-state string transducers
    
    -----------
    Attributes:
    -----------
        delta (set(tuples)): set containing all possible transitions in the machine
        
        F (tuple): final function (not implemented yet, code is outdated)
        
        q0 (str): starting state
        
        v0 (str): starting string
        
    --------
    Methods:
    --------
    
        transitions (delta): parses input transitions and stores them in a dict
        
        sigma: acquires all input symbols and puts them into a set
        
        gamma: acquires all output symbols and puts them into a set
        
        final (F): not implemented yet
        
        displayparams: prints the parameters of a DFST (sigma, gamma, q0, v0, F, Q, delta)
        
        T (s): given a string, performs transductions using delta's transitions
    
    """  
    
    def __init__(self, delta, F=(), q0="<>", v0=""):
        """ Constructs DFST parameters
        
        ----------
        Arguments:
        ----------
            delta (set(tuples)): set of transitions
            
            F (tuple): final function, (not implemented yet, code is outdated)
            
            q0 (str): starting state
            
            v0 (str): starting string
            
        ---------------------    
        Other instantiations:
        ---------------------
            Q (list): list of all states
            
            sigma (set): set of all input symbols
            
            gamma (set): set of all output symbols
        """
        
        self.q0 = q0                            
        self.v0 = v0                            
        self.delta = self.transitions(delta)    
        self.Q = list(self.delta.keys())        
        self.F = self.final(F)                  
        
        self.sigma = self.sigma()              
        self.gamma = self.gamma()              
   
    def transitions(self, delta):
        """ Takes a set of transitions and translates it into a dictionary:

                        input:  set(tuples) = { (PREVIOUS_STATE, SYMBOL, NEXT_STATE, NEXT_SYMBOL), ...}
                                        
                        output: dict = { PREVIOUS_STATE : {SYMBOL : [NEXT_STATE, NEXT_SYMBOL],...}, ...}
        ----------
        Arguments:
        ----------
            delta (set): set of transitions to turn into a dict
            
        --------    
        Returns:
        --------
            d (dict): dictionary of transitions
        """
        d = {}
        for entry in delta:
            
            previous_state = str(entry[0])      
            symbol = str(entry[1])                       
            next_state = entry[2]
            next_symbol = entry[3]
        
            if previous_state not in d: 
                d[previous_state] = {symbol : [next_state, next_symbol]}
            else:
                d[previous_state][symbol] = [next_state, next_symbol]
        return d
    
    def sigma(self):
        """ Acquires the set of all input symbols from delta
        
        --------
        Returns:
        --------
            set of all input symbols.
        """
        return set(sym for transitions in self.delta.values() for sym in transitions.keys())
    
    def gamma(self):
        """Acquires the set of all output symbols from delta
            
        --------
        Returns:
        --------
            set of all output symbols.
        """
        return set(sym[1] for transitions in self.delta.values() for sym in list(transitions.values()))
    
    def final(self, F):
        """Not implemented yet"""
        
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
        
        ----------
        Arguments:
        ----------
            s (str): string to undergo specified transformations
            
        --------
        Returns:
        --------
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
    
    delta = set()
    cfx = lambda string: f"<{string}>" 
    
    for CON in contexts:
        for _in, _out in zip(IN, OUT):
            con = ""             
            context = CON[:CON.find("_")]
            current_state = q  
            
            for sym in context:                                
                con += sym                                              
                delta.add((current_state, sym, cfx(con), sym))           
                delta.add((current_state, "?", q, "?"))                
                current_state = cfx(con)        
                
                if len(con) == 1: # if first symbol in the context, add self loop  (i.e. first symbol in a context can be repeated arbitrary times)
                    delta.add((current_state, sym, current_state, sym)) 
                
                
                # # generate prefix transitions
                # prefix = ""
                # for char in con:
                #     prefix += char
                #     for trans in delta:
                        
                #         # character level transition creation
                #         if current_state == trans[0] and trans[1] != char: # check if outgoing transition already exists with input char from current state
                           
                        
                #         # if prefix != con: # prevent inadvertent self loops 
                           
                        
                      
                        
                        
                                        
            # in change state 
            delta.add((current_state, _in, q, _out)) #! needs to be replaced with new transition functionality             
            delta.add((current_state, "?", q, "?"))    
            
            
    if not contexts:
        current_state = "<>"
        for _in, _out in zip (IN, OUT):  
            delta.add((current_state, _in, current_state, _out))
            delta.add((current_state, "?", current_state, "?"))
                       
    
    return delta

def rewrite (s1:str, s2:str, context="", v0="", displayparams=False) -> DFST:
    """ Given an input, output, and context, this function generates transitions and instantiates a DFST object. Only no or left contexts currently work
    
    ----------
    Arguments:
    ----------
        s1 (str): input symbols to be changed
        
        s2 (str): the ouput symbols to be change into
        
        context (str): context for the change to occur. Empty by default
        
        v0 (str): optional string to prepend the output with (NOTE: may have unexpected consequences regarding context. old code.)
        
        displayparams (bool): when true, displays a DFST's parameters
        
    --------
    Returns:
    --------
        DFST.T (lambda function): calls DFST.T to enact the transductions generated by rewrite
    
    """
    
    #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  ~~~insert context format handling code here~~~
    #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      
   
    contexts = [f"{CON}_" for entry in context.split("_") for CON in entry.split()]
    IN, OUT = s1.split(), s2.split()
    
    if not OUT: # deletion rules
        OUT = ("λ " *len(IN)).strip().split()
    
    delta = (generate_transitions("<>", contexts, IN, OUT))
      
    fst = DFST(delta, v0=v0, F=())
    
    if displayparams:
        fst.display_params()
        
    return lambda string : fst.T(string)


test = rewrite("a", "b", "acab_", displayparams=True)
# print(test("bcaaaa"))

# test2 = rewrite("a", "b", "c_")
# print(test2("cccca"))

