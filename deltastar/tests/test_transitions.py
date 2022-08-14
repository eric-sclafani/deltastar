import pytest
import sys
sys.path.append("/home/eric/python/projects/deltastar/deltastar") # change this dir to where deltastar is installed

from deltastar.transitions import State, Edge
from deltastar.transitions import get_transitions
from deltastar.transitions import make_delta

# the goal of these tests is to locate the inevitable edge cases that arise from certain combinations of contexts and mappings
# (i.e., the mapping contains symbols also found in the context and vice versa, multiple contexts share the same symbols, etc...)
# that is why these most of these tests are filled with seemingly random and non-sensical combinations 

# For these tests, insyms, outsyms takes the format of what happens AFTER the user's rewrite rules have been received,
# i.e. insyms and outsyms have a 1 to 1 correspondence
                   
                   
                   
#! ADD DELETION AND INSERTION TESTS FOR ALL
class TestContextFree:

    def test_cf_1(self):
        
        insyms, outsyms = (["a", "b", "c"], ["A", "B", "C"])
        transitions = [
                       Edge(State("λ"), "a", "A", State("λ"),ctype="cf"),
                       Edge(State("λ"), "b", "B", State("λ"),ctype="cf"),
                       Edge(State("λ"), "c", "C", State("λ"),ctype="cf"),
                       Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                      ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms))
         
        
    def test_cf_2(self):
        
        insyms, outsyms = (["[mod=imp]", "[pol=neg]", "[caus=yes]"], ["be", "ne", "de"])
        transitions = [
                       Edge(State("λ"), "[mod=imp]", "be", State("λ"),ctype="cf"),
                       Edge(State("λ"), "[pol=neg]", "ne", State("λ"),ctype="cf"),
                       Edge(State("λ"), "[caus=yes]", "de", State("λ"),ctype="cf"), 
                       Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                      ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms))
        
    
class TestLeftContext:
    
    
    def test_Lcon_1(self): 
        
        insyms, outsyms = [("a","x"), ("b", "y")]
        context = ["a c a b _", "x y z _"]
        transitions = [
                       Edge(State("λ"), "a", "a", State("a"), ctype="left"),
                       Edge(State("λ"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("λ"), "x", "x", State("x"), ctype="left"),
                       Edge(State("a"), "c", "c", State("ac"), ctype="left"),
                       Edge(State("a"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("a"), "x", "x", State("x"), ctype="left"),
                       Edge(State("a"), "a", "a", State("a"), ctype="left"),
                       Edge(State("ac"), "a", "a", State("aca"), ctype="left"),
                       Edge(State("ac"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("ac"), "x", "x", State("x"), ctype="left"),
                       Edge(State("aca"), "b", "b", State("acab"), ctype="left"),
                       Edge(State("aca"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("aca"), "c", "c", State("ac"), ctype="left"),
                       Edge(State("aca"), "x", "x", State("x"), ctype="left"),
                       Edge(State("aca"), "a", "a", State("a"), ctype="left"),
                       Edge(State("acab"), "a", "b", State("a"), ctype="left", is_transduction=True),
                       Edge(State("acab"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("acab"), "x", "y", State("x"), ctype="left", is_transduction=True),
                       Edge(State("x"), "y", "y", State("xy"), ctype="left"),
                       Edge(State("x"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("x"), "x", "x", State("x"), ctype="left"),
                       Edge(State("x"), "a", "a", State("a"), ctype="left"),
                       Edge(State("xy"), "z", "z", State("xyz"), ctype="left"),
                       Edge(State("xy"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("xy"), "x", "x", State("x"), ctype="left"),
                       Edge(State("xy"), "a", "a", State("a"), ctype="left"),
                       Edge(State("xyz"), "a", "b", State("a"), ctype="left", is_transduction=True),
                       Edge(State("xyz"), "?", "?", State("λ"), ctype="left"),
                       Edge(State("xyz"), "x", "y", State("x"), ctype="left", is_transduction=True),
                      ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
        
    def test_Lcon_2(self):
    
        insyms, outsyms = [("b"), ("p")]
        context = ["b b b _"]
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
        
        insyms, outsyms = [("a"), ("b")] 
        context = ["a c a b _", "c c _", "b _", ]
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
        

class TestRightContext:
    
    def test_Rcon_1(self):
        
        insyms, outsyms = [("a"), ("b")]
        context = ["_ a b a b"]
        transitions = [
                       Edge(State("λ"), "a", "λ", State("a"), ctype="right"),
                       Edge(State("λ"), "?", "?", State("λ"), ctype="right"),
                       Edge(State("a"), "a", "λ", State("aa"), ctype="right"),
                       Edge(State("a"), "?", "a?", State("λ"), ctype="right"),
                       Edge(State("aa"), "b", "λ", State("aab"), ctype="right"),
                       Edge(State("aa"), "?", "aa?", State("λ"), ctype="right"),
                       Edge(State("aa"), "a", "a", State("aa"), ctype="right"),
                       Edge(State("aab"), "a", "λ", State("aaba"), ctype="right"),
                       Edge(State("aab"), "?", "aab?", State("λ"), ctype="right"),
                       Edge(State("aaba"), "b", "babab", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("aaba"), "?", "aaba?", State("λ"), ctype="right"),
                       Edge(State("aaba"), "a", "aabλ", State("aa"), ctype="right"),
                      ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
    
    def test_Rcon_2(self):
        
        insyms, outsyms = [("g"), ("G")]
        context = ["_ g g f f", "_ z z"]
        transitions = [
                       Edge(State("λ"), "g", "λ", State("g") , ctype="right"),
                       Edge(State("λ"), "?", "?", State("λ"), ctype="right"),
                       Edge(State("g"), "g", "λ", State("gg"), ctype="right"),
                       Edge(State("g"), "?", "g?", State("λ"), ctype="right"),
                       Edge(State("g"), "z", "λ", State("gz"), ctype="right"),
                       Edge(State("gg"), "g", "λ", State("ggg"), ctype="right"),
                       Edge(State("gg"), "?", "gg?", State("λ"), ctype="right"),
                       Edge(State("gg"), "z", "gλ", State("gz"), ctype="right"),
                       Edge(State("ggg"), "f", "λ", State("gggf"), ctype="right"),
                       Edge(State("ggg"), "?", "ggg?", State("λ"), ctype="right"),
                       Edge(State("ggg"), "g", "g", State("ggg"), ctype="right"),
                       Edge(State("ggg"), "z", "ggλ", State("gz"), ctype="right"),
                       Edge(State("gggf"), "f", "Gggff", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("gggf"), "?", "gggf?", State("λ"), ctype="right"),
                       Edge(State("gggf"), "g", "gggfλ", State("g"), ctype="right"),
                       Edge(State("gz"), "z", "Gzz", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("gz"), "?", "gz?", State("λ"), ctype="right"),
                       Edge(State("gz"), "g", "gzλ", State("g"), ctype="right")
                       ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))
    
    
    def test_Rcon_3(self):
        
        insyms, outsyms = [("a","x"), ("b", "y")]
        context = ["_ x y z", "_ b b", " _ a"]
        transitions = [
                       Edge(State("λ"), "a", "λ", State("a"), ctype="right"),
                       Edge(State("λ"), "?", "?", State("λ"), ctype="right"),
                       Edge(State("λ"), "x", "λ", State("x"), ctype="right"),
                       Edge(State("a"), "x", "λ", State("ax"), ctype="right"),
                       Edge(State("a"), "?", "a?", State("λ"), ctype="right"),
                       Edge(State("a"), "b", "λ", State("ab"), ctype="right"),
                       Edge(State("a"), "a", "b", State("a"), ctype="right", is_transduction=True),
                       Edge(State("ax"), "y", "λ", State("axy"), ctype="right"),
                       Edge(State("ax"), "?", "ax?", State("λ"), ctype="right"),
                       Edge(State("ax"), "b", "aλ", State("xb"), ctype="right"),
                       Edge(State("ax"), "x", "aλ", State("xx"), ctype="right"),
                       Edge(State("ax"), "a", "axλ", State("a"), ctype="right"),
                       Edge(State("axy"), "z", "bxyz", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("axy"), "?", "axy?", State("λ"), ctype="right"),
                       Edge(State("axy"), "a", "axyλ", State("a"), ctype="right"),
                       Edge(State("axy"), "x", "axyλ", State("x"), ctype="right"),
                       Edge(State("x"), "x", "λ", State("xx"), ctype="right"),
                       Edge(State("x"), "?", "x?", State("λ"), ctype="right"),
                       Edge(State("x"), "b", "λ", State("xb"), ctype="right"),
                       Edge(State("x"), "a", "y", State("a"), ctype="right", is_transduction=True),
                       Edge(State("xx"), "y", "λ", State("xxy"), ctype="right"),
                       Edge(State("xx"), "?", "xx?", State("λ"), ctype="right"),
                       Edge(State("xx"), "b", "xλ", State("xb"), ctype="right"),
                       Edge(State("xx"), "x", "x", State("xx"), ctype="right"),
                       Edge(State("xx"), "a", "xxλ", State("a"), ctype="right"),
                       Edge(State("xxy"), "z", "yxyz", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("xxy"), "?", "xxy?", State("λ"), ctype="right"),
                       Edge(State("xxy"), "a", "xxyλ", State("a"), ctype="right"),
                       Edge(State("xxy"), "x", "xxyλ", State("x"), ctype="right"),
                       Edge(State("ab"), "b", "bbb", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("ab"), "?", "ab?", State("λ"), ctype="right"),
                       Edge(State("ab"), "a", "abλ", State("a"), ctype="right"),
                       Edge(State("ab"), "x", "abλ", State("x"), ctype="right"),
                       Edge(State("xb"), "b", "ybb", State("λ"), ctype="right", is_transduction=True),
                       Edge(State("xb"), "?", "xb?", State("λ"), ctype="right"),
                       Edge(State("xb"), "a", "xbλ", State("a"), ctype="right"),
                       Edge(State("xb"), "x", "xbλ", State("x"), ctype="right"),
                      ]
        assert make_delta(transitions) == make_delta(get_transitions(insyms, outsyms, context))

# class TestDualContext:
    
        
#     def test_Dcon_1(self):
#         pass
    
    
    
#     def test_Dcon_2(self):
#         pass
    
    
#     def test_Dcon_3(self):
#         pass
    

# class TestMixedContexts:
    
    
#     def test_mixedcon_1(self):
#         pass
    
    
    
#     def test_mixedcon_2(self):
#         pass





