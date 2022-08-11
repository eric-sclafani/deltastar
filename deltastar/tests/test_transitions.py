import pytest
import sys
sys.path.append("/home/eric/python/projects/deltastar/") # change this dir if needed

from deltastar.transitions import State, Edge
from deltastar.transitions import get_transitions
from deltastar.transitions import make_delta


# ~~~ TEST CASES ~~~
# format matches the user's input AFTER they specify the mappings/contexts
# the goal of these tests is to locate the inevitable edge cases that arise from certain combinations of contexts and mappings
# (i.e., the mapping contains symbols also found in the context and vice versa, multiple contexts share the same symbols, etc...)
# that is why these most of these tests are filled with seemingly random and non-sensical combinations 


mappings = {
            "t1" : ((["a"], ["b"])),
            "t2" : ((["b"], ["p"])),
            "t3" : ((["[STEM]"], ["verb"])),
            "t4" : ((["a", "b", "c"], ["A", "B", "C"])),
            "t5" : ((["[mod=imp]", "[pol=neg]", "[caus=yes]"], ["be", "ne", "de"])),
            "t6" : ((["g"], ["G"]))
            }
            

contexts = {
            "left":{"t1" : ["x y x y _", "x x _"],
                    "t2" : ["b b b _"],
                    "t3" : ["a c a b _", "c c _", "b _", ],
                    "t4" : []
                   },
                    
            "right":{"t1" : ["_ a b a b"],
                     "t2" : ["_ g g f f", "_ z z"],
                     "t3" : [],     
                     "t4" : []  
                    },
                    
            "dual":{"t1" : [],
                    "t2" : [],
                    "t3" : [],
                    "t4" : [],
                   },
            }
            
                   
class TestContextFree:

    def test_cf_1(self):
        
        insyms, outsyms = mappings["t4"]
        transitions = [
                       Edge(State("λ"), "a", "A", State("λ"),ctype="cf"),
                       Edge(State("λ"), "b", "B", State("λ"),ctype="cf"),
                       Edge(State("λ"), "c", "C", State("λ"),ctype="cf"),
                       Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                      ]
        assert transitions == get_transitions(insyms, outsyms) 
         
        
    def test_cf_2(self):
        
        insyms, outsyms = mappings["t5"]
        transitions = [
                       Edge(State("λ"), "[mod=imp]", "be", State("λ"),ctype="cf"),
                       Edge(State("λ"), "[pol=neg]", "ne", State("λ"),ctype="cf"),
                       Edge(State("λ"), "[caus=yes]", "de", State("λ"),ctype="cf"), 
                       Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                      ]
        assert transitions == get_transitions(insyms, outsyms)
        
    
class TestLeftContext:
    
    def test_Lcon_1(self): # "[STEM]", "verb",
        
        insyms, outsyms = mappings["t3"]
        context = contexts["left"]["t1"]
        transitions = [
                          Edge(State("λ"), "x", "x", State("x"), ctype="left"),
                          Edge(State("λ"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("x"), "y", "y", State("xy"), ctype="left"),
                          Edge(State("x"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("x"), "x", "x", State("xx"), ctype="left"),
                          Edge(State("xy"), "x", "x", State("xyx"), ctype="left"),
                          Edge(State("xy"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("xyx"), "y", "y", State("xyxy"), ctype="left"),
                          Edge(State("xyx"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("xyx"), "x", "x", State("xx"), ctype="left"),
                          Edge(State("xyxy"), "[STEM]", "verb", State("λ"), ctype="left", is_transduction=True),
                          Edge(State("xyxy"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("xyxy"), "x", "x", State("xyx"), ctype="left"),
                          Edge(State("xx"), "[STEM]", "verb", State("λ"), ctype="left", is_transduction=True),
                          Edge(State("xx"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("xx"), "y", "y", State("xy"), ctype="left"),
                          Edge(State("xx"), "x", "x", State("xx"), ctype="left"),
                         ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
        
    def test_Lcon_2(self):
        
       
        insyms, outsyms = mappings["t2"]
        context = contexts["left"]["t2"]
        transitions = [
                          Edge(State("λ"), "b", "b", State("b"), ctype="left"),
                          Edge(State("λ"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("b"), "b", "b", State("bb"), ctype="left"),
                          Edge(State("b"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("bb"), "b", "b", State("bbb"), ctype="left"),
                          Edge(State("bb"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("bbb"), "b", "p", State("bbb"), ctype="left", is_transduction=True),
                          Edge(State("bbb"), "?", "?", State("λ"), ctype="left"),
                         ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
        
    
    def test_Lcon_3(self):
        
        insyms, outsyms = mappings["t1"]
        context = contexts["left"]["t3"]
        transitions = [
                       Edge(State("λ"), "a", "a", State("a"), ctype="left"),
                       Edge(State("λ"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("λ"), "c", "c", State("c"), ctype="left"),
                       Edge(State("λ"), "b", "b", State("b"), ctype="left"),
                       Edge(State("a"), "c", "c", State("ac"), ctype="left"),
                       Edge(State("a"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("a"), "a", "a", State("a"), ctype="left"),
                       Edge(State("a"), "b", "b", State("b"), ctype="left"),
                       Edge(State("ac"), "a", "a", State("aca"), ctype="left"),
                       Edge(State("ac"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("ac"), "c", "c", State("cc"), ctype="left"),
                       Edge(State("ac"), "b", "b", State("b"), ctype="left"),
                       Edge(State("aca"), "b", "b", State("acab"), ctype="left"),
                       Edge(State("aca"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("aca"), "c", "c", State("ac"), ctype="left"),
                       Edge(State("aca"), "a", "a", State("a"), ctype="left"),
                       Edge(State("acab"), "a", "b", State("a"), ctype="left", is_transduction=True),
                       Edge(State("acab"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("acab"), "c", "c", State("c"), ctype="left"),
                       Edge(State("acab"), "b", "b", State("b"), ctype="left"),
                       Edge(State("c"), "c", "c", State("cc"), ctype="left"),
                       Edge(State("c"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("c"), "a", "a", State("a"), ctype="left"),
                       Edge(State("c"), "b", "b", State("b"), ctype="left"),
                       Edge(State("cc"), "a", "b", State("a"), ctype="left", is_transduction=True),
                       Edge(State("cc"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("cc"), "c", "c", State("cc"), ctype="left"),
                       Edge(State("cc"), "b", "b", State("b"), ctype="left"),
                       Edge(State("b"), "a", "b", State("a"), ctype="left", is_transduction=True),
                       Edge(State("b"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("b"), "c", "c", State("c"), ctype="left"),
                       Edge(State("b"), "b", "b", State("b"), ctype="left"),
                      ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
        

# class TestRightContext:
    
        
#     #! contains wrong prefix transitions
    
#     def test_Rcon_1(self):
        
        
#         insyms, outsyms = mappings["t1"]
#         context = contexts["right"]["t1"]
#         transitions = [
#                        Edge(State("λ"), "a", "λ", State("a"), ctype="right"),
#                        Edge(State("λ"), "?", "?", State("λ"), ctype="right"),
#                        Edge(State("a"), "a", "λ", State("aa"), ctype="right"),
#                        Edge(State("a"), "?", "a?", State("λ"), ctype="right"),
#                        Edge(State("aa"), "b", "λ", State("aab"), ctype="right"),
#                        Edge(State("aa"), "?", "aa?", State("λ"), ctype="right"),
#                        Edge(State("aa"), "a", "a", State("aa"), ctype="right"),
#                        Edge(State("aab"), "a", "λ", State("aaba"), ctype="right"),
#                        Edge(State("aab"), "?", "aab?", State("λ"), ctype="right"),
#                        Edge(State("aaba"), "b", "babab", State("λ"), ctype="right", is_transduction=True),
#                        Edge(State("aaba"), "?", "aaba?", State("λ"), ctype="right"),
#                        Edge(State("aaba"), "a", "aabaa", State("aa"), ctype="right"),
#                       ]
#         assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
    
#     def test_Rcon_2(self):
        
        
#         insyms, outsyms = mappings["t6"]
#         context = contexts["right"]["t2"]
#         transitions = [
#                        Edge(State("λ"), "g", "λ", State("g"), ctype="right"),
#                        Edge(State("λ"), "?", "?", State("λ"), ctype="right"),
#                        Edge(State("g"), "g", "λ", State("gg"), ctype="right"),
#                        Edge(State("g"), "?", "g?", State("λ"), ctype="right"),
#                        Edge(State("g"), "z", "λ", State("gz"), ctype="right"),
#                        Edge(State("gg"), "g", "λ", State("ggg"), ctype="right"),
#                        Edge(State("gg"), "?", "gg?", State("λ"), ctype="right"),
#                        Edge(State("gg"), "z", "ggz", State("gz"), ctype="right"),
#                        Edge(State("ggg"), "f", "λ", State("gggf"), ctype="right"),
#                        Edge(State("ggg"), "?", "ggg?", State("λ"), ctype="right"),
#                        Edge(State("ggg"), "g", "g", State("ggg"), ctype="right"),
#                        Edge(State("ggg"), "z", "gggz", State("gz"), ctype="right"),
#                        Edge(State("gggf"), "f", "Gggff", State("λ"), ctype="right", is_transduction=True),
#                        Edge(State("gggf"), "?", "gggf?", State("λ"), ctype="right"),
#                        Edge(State("gggf"), "g", "gggfg", State("g"), ctype="right"),
#                        Edge(State("gz"), "z", "Gzz", State("λ"), ctype="right", is_transduction=True),
#                        Edge(State("gz"), "?", "gz?", State("λ"), ctype="right"),
#                        Edge(State("gz"), "g", "gzg", State("g"), ctype="right")
#                       ]
#         assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
    
    
#     def test_Rcon_3(self):
#         pass
  

# class TestDualContext:
    
        
#     def test_Dcon_1(self):
#         pass
    
    
    
#     def test_Dcon_2(self):
#         pass
    
    
#     def test_Dcon_3(self):
#         pass
    

# class TestMixedContexts:
    
    
#     def test_single_mapping_multiple_context(self):
#         pass

    
#     def test_multiple_mapping_multiple_context(self):
#         pass
    





