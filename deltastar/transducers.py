
# Eric Sclafani
from collections import defaultdict
from dataclasses import dataclass
import pydot
import transitions as tr
from transitions import PH, cfx
from typing import List
from tabulate import tabulate 

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
        print(f"Σ: {self.sigma}\nΓ: {self.gamma}\nQ: {set(cfx(q) for q in self.Q) if self.Q else set(['<λ>'])}\nq0: {self.q0}\nv0: {None if not self.v0 else self.v0}\nFinals: {finals}")
        
        print(f"Delta:")
        
        transitions = []
        for state, trans in sorted(self.delta.items(), key=lambda x: x =="<λ>"): # key makes sure initial state transitions are first
            for s, t in trans.items():
               transitions.append([cfx(state), s, t[0], cfx(t[1])])
        
        print(tabulate(transitions, headers=["Start", "Insym", "Outsym", "End"], tablefmt="fancy_outline"))
    
    #! ~~~~~~~~~~~~~~~~~~~~~~~~~~~ BROKEN: NEEDS TO BE UPDATED ~~~~~~~~~~~~~~~~~~~~~~~~
    def to_graph(self, file_name="my_machine.png", disable_PH=True):
         
        if not file_name.endswith(".png"):
            raise ValueError("only .png files can be exported")
        
        graph = pydot.Dot("finite_state_machine", graph_type="digraph", rankdir="LR", size="6!")
        graph.add_node(pydot.Node("initial", shape="point", color="white"))
        
        i = 0
        for state, transitions in self.delta.items():
            for in_sym, out_trans in transitions.items():
                
                if disable_PH and in_sym == PH:
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
                graph.add_edge(pydot.Edge(str(prev_state), str(next_state), label=f"{in_sym} : {out_trans[1]}"))
                i += 1
                
        graph.write_png(file_name)
    
    # users need to input strings space delimited. This accounts for symbols having multiple characters (i.e. "[tns=past] v e r b [mod=imp] ")
    def rewrite(self, s:str) -> str:
        
        output = ""
        state = self.q0 # begin at the initial state
        
        if self.rule_type == "insertion":
            s = list("Ø" + tr.intersperse("Ø", s.split()) + "Ø")
        else:
            s = s.split()
            
        for char in s:  
            try: # attempt to find transitions
                outsym = self.delta[state][char][0] 
                output += outsym 
                state = self.delta[state][char][1]
                
            except KeyError: # if not found, use the placeholder transition and replace placeholder with char
                outsym = self.delta[state][PH][0]
                output += outsym.replace(PH, char) 
                state = self.delta[state][PH][1]
        
        output = ((tr.intersperse(" ", output) + self.finals[state]).replace("λ", "").replace("Ø", "")).split()
        
       
        return self.v0 + "".join(output)
    
    @classmethod
    def from_rules(cls, insyms, outsyms, contexts=[], v0="", rule_type=""):
        assert len(insyms) == len(outsyms)

        # this condition block acquires the string representations of rewrite rules for displaying
        rules = []  
        if contexts: # context dependent 
            for con in contexts:
                for _in, _out in zip(insyms, outsyms):
                    rules.append(f"{_in} -> {_out} / {con}")   
        else: # context free 
            for _in, _out in zip(insyms, outsyms):
                rules.append(f"{_in} -> {_out} / _")


        transitions = tr.get_transitions(insyms, outsyms, contexts)
        delta = tr.get_delta(transitions)
        Q, sigma, gamma = tr.get_Q_sigma_gamma(transitions)
        finals = tr.get_final_mappings(transitions)
            
        return cls(delta, Q, sigma, gamma, finals, rules, v0=v0, rule_type=rule_type)

    
def assimilation(pairs:List[tuple], contexts=[], v0="") -> DFST:
    
    insyms, outsyms = [], []
    for insym, outsym in pairs:
        if not insym or not outsym:
            raise tr.RuleError(f"Invalid pair {insym, outsym}")

        insyms.append(insym)
        outsyms.append(outsym)
        
    return DFST.from_rules(insyms, outsyms, contexts, v0=v0, rule_type="assimilation")
    
def deletion(pairs:List[tuple], contexts=[], v0="") -> DFST:
    
    insyms, outsyms = [], []
    for insym, outsym in pairs:
        if not insym or outsym:
            raise tr.RuleError(f"Invalid pair {insym, outsym}")

        insyms.append(insym)
        outsyms.append("Ø")
        
    return DFST.from_rules(insyms, outsyms, contexts, v0=v0, rule_type="deletion")
    
    
def insertion(pairs:List[tuple], contexts=[], v0="") -> DFST:
    
    insyms, outsyms = [], []
    for insym, outsym in pairs:
        if insym or not outsym:
            raise tr.RuleError(f"Invalid pair {insym, outsym}")

        insyms.append("Ø")
        outsyms.append(outsym)
        
    contexts_insertion = []
    
    for context in contexts:
        hyphen = context.index("_")
        
        if hyphen == len(context)-1: # left context rule
            context = context[:hyphen]
            new_context = list("Ø" + tr.intersperse("Ø", context.split()))
            contexts_insertion.append(" ".join(new_context) + " _")

        elif hyphen == 0: # right context rule
            pass

        else: # dual context
            pass
            
    
    print(contexts_insertion)
    return DFST.from_rules(insyms, outsyms, contexts_insertion, v0=v0, rule_type="insertion")
        
        
        
        
rule = insertion([("", "[mod=imp]")], ["a c a b _"])
rule.displayparams
print(rule.rewrite("a c a b a c a b"))




# test = transducer([("a", "A"), ("h", "H")], ["x y z _ z y x"])
# test.displayparams
# print(test.rewrite("x y z h z y x", to_list=True,))

#! was giving some issues
# test = transducer([("a", "X"), ("b", "Y")], ["a c _ c b"])
# test.displayparams
# print(test.rewrite("a c a c b", to_list=True))

# test = transducer([("c", "C")], ["c _ d a c"])
# test.displayparams
# print(test.rewrite("x y z h z y x", to_list=True))



    