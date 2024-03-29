    # -*- coding: utf8 -*-

# Eric Sclafani
from collections import defaultdict
from dataclasses import dataclass
import pydot
import transitions as tr
from utils.funcs import *
from typing import List
from tabulate import tabulate 

RESERVED = ["$", "λ", "Ø", "?"]

@dataclass
class DFST:
                             
    delta: defaultdict
    Q:List[str]
    sigma:set
    gamma:set
    finals: dict
    rules:List[str]
    rule_type:str
    v0:str = ""
    q0:str = tr.State("λ")
    
    @property                    
    def displayparams(self):
        """ Prints rewrites rule, sigma, gamma, Q, q0, v0, F, delta""" 
        finals = {f"<{k}>":v for k,v in self.finals.items()}
        
        print(f"{'~'*7}Rewrite rules:{'~'*7}")
        print(*self.rules, sep="\n")
        print("~"*28,"\n")
        
        # these next two loops remove the extra symbols from sigma and gamma
        sigma = set()
        for sym in self.sigma:
            if sym not in RESERVED:
                sigma.add(sym)     
                
        gamma = set()
        for sym in self.gamma:
            for char in sym:
                if char not in RESERVED:
                    gamma.add(char)
                    
                    
        print(f"Σ: {sigma}\nΓ: {gamma}\nQ: {set(cfx(q) for q in self.Q) if self.Q else set(['<λ>'])}\nq0: {cfx(self.q0.label)}\nv0: {None if not self.v0 else self.v0}\nFinals: {finals}")
        
        
        print(f"Delta:")
        transitions = []
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
               transitions.append([cfx(state), s, t[0], cfx(t[1])])
        
        print(tabulate(transitions, headers=["Start", "Insym", "Outsym", "End"], tablefmt="fancy_outline"))
    
    
    
    def to_graph(self, file_name="my_machine.png", show_PH=False):
        """Creates a .png file of you machine via Graphviz and saves to local directory
        
        Args:
            file_name (str): name of the file. Defaults to 'my_machine.png'
            show_PH (bool): option to show the ?:? transitions. Set to False by default to avoid clutter"""
         
        if not file_name.endswith(".png"):
            raise ValueError("only .png files can be exported")
        
        graph = pydot.Dot("finite_state_machine", graph_type="digraph", rankdir="LR", size="10!")
        graph.add_node(pydot.Node("initial", shape="point", color="white"))
        
        i = 0
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                
                if not show_PH and in_sym == PH:
                    continue
                
                start = state
                end = out_trans[1]
                
                if start == self.q0 and i == 0: # i enforces that this edge only gets created once
                    graph.add_edge(pydot.Edge("initial", str(start)))
                
                if self.finals[start]:
                    start = f"{start}\\,{self.finals[start]}"
                        
                if self.finals[end]:
                    end = f"{end}\\,{self.finals[end]}"
                          
                graph.add_node(pydot.Node(str(start), shape="doublecircle"))
                graph.add_node(pydot.Node(str(end), shape="doublecircle"))
                graph.add_edge(pydot.Edge(str(start), str(end), label=f"{in_sym}\\:{out_trans[0]}"))
                i += 1
                
        graph.write_png(file_name)
    
    
    #! add a better debug mode
    def rewrite(self, s:str, show_path=False) -> str:
        """Rewrite a user's target string by iterating through delta and producing an output tape
        
        Args:
            s (str): string to undergo transduction
            show_path (bool): debug option to see the output tape and path the string takes through the machine (can get messy with large machines)
            
        Returns:
            str: new string
        """
        
        path = []
        out_tape = []
        output = ""
        state = self.q0 # begin at the initial state
        
        if self.rule_type == "insertion":
            s = list("$"+ "Ø" + intersperse(s.split(), "Ø") + "Ø" + "$")
        else:
            s = ("$ " + s + " $").split()
            
        for sym in s: 
            try: # attempt to find transitions
                outsym = self.delta[state][sym][0] 
                output += outsym 
                state = self.delta[state][sym][1]
                path.append(state.label)
                
            except KeyError: # if not found, use the placeholder transition and replace placeholder with sym
                outsym = self.delta[state][PH][0]
                output += outsym.replace(PH, sym)
                state = self.delta[state][PH][1]
                path.append(state.label)
            out_tape.append(output)
            
        output += self.finals[state]
        out_tape.append(output)
        
        for sym in RESERVED:
            output = output.replace(sym, "").strip()
            
        if show_path:
            print(f"\nInput string: {' '.join(s)}")
            print(f"String path: {' --> '.join(path)}\nOutput tape: {' --> '.join(out_tape)}")
        
        self.v0 = self.v0 + " " if self.v0 else ""
        return intersperse(self.v0 + output)
    
    
    
    @classmethod
    def from_rules(cls, insyms, outsyms, contexts=[], v0="", rule_type=""):
        assert len(insyms) == len(outsyms)

        # this condition block acquires the string representations of rewrite rules for displaying, 
        # and transduction environments to be used when generating prefix transitions
        rules = []  
        transduction_envs = {}
        if contexts: # context dependent 
            for con in contexts:
                for _in, _out in zip(insyms, outsyms):
                    rules.append(f"{_in} -> {_out} / {con}") 
                    
                    _con = con.replace("_", _in).strip()
                    transduction_envs[_con] = _out
                    
        else: # context free 
            for _in, _out in zip(insyms, outsyms):
                rules.append(f"{_in} -> {_out} / _")

        transitions = tr.get_transitions(insyms, outsyms, contexts, transduction_envs)
        delta = tr.get_delta(transitions)
        Q, sigma, gamma = tr.get_Q_sigma_gamma(transitions)
        finals = tr.get_final_mappings(transitions)
            
        return cls(delta, Q, sigma, gamma, finals, rules, v0=v0, rule_type=rule_type)

    
    
def assimilation(pairs:List[tuple], contexts=[], v0="") -> DFST:
    """Handles assimilation rewrite rules such that existing symbols are mapped to new ones
    
    Args:
        pairs (List[tuple]): list of (INPUT, OUTPUT) pairs. 
        contexts (list): list of contexts for mapping to transpire
        v0(str): optional string to prepend to output tape (is not involved in transduction)
        
    Returns:
        DFST object: DFST instantiated through rewrite rules
    """
    if contexts:
        validate_context(contexts)
    
    insyms, outsyms = [], []
    for insym, outsym in pairs:
        if not insym or not outsym:
            raise RuleError(f"Invalid pair {insym, outsym}")

        insyms.append(insym)
        outsyms.append(outsym)
        
    return DFST.from_rules(insyms, outsyms, contexts, v0=v0, rule_type="assimilation")
    
    
    
def deletion(pairs:List[tuple], contexts=[], v0="") -> DFST:
    """Handles deletion rewrite rules such that existing symbols are mapped to the empty string.
    
    Args:
        pairs (List[tuple]): list of (INPUT, "") pairs 
        contexts (list): list of contexts for mapping to transpire
        v0(str): optional string to prepend to output tape (is not involved in transduction)
        
    Returns:
        DFST object: DFST instantiated through rewrite rules
    """
    
    if contexts:
        validate_context(contexts)
    
    insyms, outsyms = [], []
    for insym, outsym in pairs:
        if not insym or outsym:
            raise RuleError(f"Invalid pair {insym, outsym}")

        insyms.append(insym)
        outsyms.append("Ø")
        
    return DFST.from_rules(insyms, outsyms, contexts, v0=v0, rule_type="deletion")
    
    
    
def insertion(pairs:List[tuple], contexts=[], v0="") -> DFST:
    """Handles insertion rewrite rules such that the empty string is mapped to a new symbol.
    
    Args:
        pair (List[tuple]): list containing a ("", OUTPUT) pair (Note: insertion can only handle one mapping at a time)
        contexts (list): list of contexts for mapping to transpire
        v0(str): optional string to prepend to output tape (is not involved in transduction)
        
    Returns:
        DFST object: DFST instantiated through rewrite rules
    """
    
    if contexts:
        validate_context(contexts)
    
    if len(pairs) != 1:
        raise ValueError("Insertion rules can only take one mapping at a time")
        
    insyms, outsyms = [], []
    for insym, outsym in pairs:
        if insym or not outsym:
            raise RuleError(f"Invalid pair {insym, outsym}")

        insyms.append("Ø")
        outsyms.append(outsym)
        
    contexts_insertion = []
    apply_intersperse = lambda string : intersperse(string.split(), "Ø")
    for context in contexts:
        underscore = context.index("_")
        
        if underscore == len(context)-1: # left context
            context = context[:underscore]
            new_context = list("Ø" + apply_intersperse(context))
            new_context = validate_insertion_context(" ".join(new_context) + " _")
            contexts_insertion.append(new_context)

        elif underscore == 0: # right context
            context = context[underscore+1:]
            new_context = list(apply_intersperse(context))
            new_context = validate_insertion_context("_ " + " ".join(new_context))
            contexts_insertion.append(new_context)

        else: # dual context
            left, right = context.split("_")
            left = list( "Ø" + apply_intersperse(left))
            right = list(apply_intersperse(right) + "Ø")
            
            dual = " ".join(left) + " _ " + " ".join(right)
            dual = validate_insertion_context(dual)
            contexts_insertion.append(dual)
            
    return DFST.from_rules(insyms, outsyms, contexts_insertion, v0=v0, rule_type="insertion")





# mappings1 = [("e","i"),("i","i")]
# environment1 = ["_ #"]
# final_e_raising = assimilation(mappings1, environment1)
# final_e_raising.displayparams
