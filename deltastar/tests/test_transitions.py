import pytest
import sys
sys.path.append("/home/eric/python/projects/deltastar/") # change this dir if needed

from deltastar.transitions import State, Edge
from deltastar.transitions import get_transitions


# TEST CASES: [input, output] pairs
mappings = {"single":{
                      "t1" : [("a", "b")],
                      "t2" : [("[tns=pst]", "ed")],
                      "t3" : [("abc", "xyz")],
                     },
                         
            "multiple":{
                        "t1" : [("a", "A"), ("b", "B"), ("c", "C")],
                        "t2" : [("[mod=imp]", "be"), ("[pol=neg]", "ne"), ("[caus=yes]", "de")],
                        }
            }

         
contexts = {
            "left":{"single":{"t1" : ["a c a b _"],
                              "t2" : ["b b b _"],
                              "t3" : ["[STEM] _ "],
                             },
                     
                    "multiple":{"t1" : ["a c a b _", "c c _", "b _"],
                                "t2" : ["b a b a _", " a b _", "c _"],
                               }
                    },
            "right":{"single":{"t1" : [],
                               "t2" : [],
                               "t3" : [],
                              },
                    "multiple":{"t1" : [],
                                "t2" : [],
                                "t3" : [],
                               }
                    },
            
            "dual":{"single":{"t1" : [],
                              "t2" : [],
                              "t3" : [],
                             },
                     
                    "multiple":{"t1":(),
                                "t2":(),
                                "t3":(),
                               },
                    }
            }
            
            
class TestContextFree:

    def test_single_mapping(self):
        
        insyms_t1, outsyms_t1 = mappings["single"]["t1"][0]
        transitions_t1 = [
                          Edge(State("λ"), "a", "b", State("λ"),ctype="cf"), 
                          Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                         ]
         
        insyms_t2, outsyms_t2 = mappings["single"]["t2"][0]
        transitions_t2 = [
                          Edge(State("λ"), "[tns=pst]", "ed", State("λ"),ctype="cf"), 
                          Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                         ]

        insyms_t3, outsyms_t3 = mappings["single"]["t3"][0]
        transitions_t3 = [
                          Edge(State("λ"), "abc", "xyz", State("λ"),ctype="cf"), 
                          Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                         ]

        assert get_transitions(insyms_t1, outsyms_t1) == transitions_t1
        assert get_transitions(insyms_t2, outsyms_t2) == transitions_t2
        assert get_transitions(insyms_t3, outsyms_t3) == transitions_t3
        
        
        
    def test_multiple_mappings(self):
        
        insyms_t1, outsyms_t1 = mappings["multiple"]["t1"]
        transitions_t1 = [
                          Edge(State("λ"), "a", "x", State("λ"),ctype="cf"),
                          Edge(State("λ"), "b", "y", State("λ"),ctype="cf"),
                          Edge(State("λ"), "c", "z", State("λ"),ctype="cf"),
                          Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                         ]
        
        insyms_t2, outsyms_t2 = mappings["multiple"]["t2"]
        transitions_t2 = [
                          Edge(State("λ"), "[mod=imp]", "be", State("λ"),ctype="cf"),
                          Edge(State("λ"), "[pol=neg]", "ne", State("λ"),ctype="cf"),
                          Edge(State("λ"), "[caus=yes]", "de", State("λ"),ctype="cf"), 
                          Edge(State("λ"), "?", "?", State("λ"),ctype="cf")
                         ]
        
        assert get_transitions(insyms_t1, outsyms_t1) == transitions_t1
        assert get_transitions(insyms_t2, outsyms_t2) == transitions_t2
    
class TestLeftContext:
    
    def test_single_mapping_single_context(self):
        
        insyms_t1, outsyms_t1 = mappings["single"]["t1"]
        context_t1 = contexts["left"]["single"]["t1"]
        transitions_t1 = [
                          Edge(State("λ"), "a", "a", State("a"), ctype="left"),
                          Edge(State("λ"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("a"), "c", "c", State("ac"), ctype="left"),
                          Edge(State("a"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("a"), "a", "a", State("a"), ctype="left"),
                          Edge(State("ac"), "a", "a", State("aca"), ctype="left"),
                          Edge(State("ac"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("aca"), "b", "b", State("acab"), ctype="left"),
                          Edge(State("aca"), "?", "?", State("λ"), ctype="left"),
                          Edge(State("aca"), "c", "c", State("ac"), ctype="left"),
                          Edge(State("aca"), "a", "a", State("a"), ctype="left"),
                          Edge(State("acab"), "a", "b", State("a"), ctype="left", is_transduction=True),
                          Edge(State("acab"), "?", "?", State("λ"), ctype="left"),
                         ]
        # assert tr.Lcon_transitions(insyms_t1, outsyms_t1, context_t1) == transitions_t1
        
        
        
        
        insyms_t2, outsyms_t2 = mappings["single"]["t2"]
        
        
        
        
        insyms_t3, outsyms_t3 = mappings["single"]["t3"]
    
    
    def test_single_mapping_multiple_context(self):
        pass


    def test_mutiple_mapping_single_context(self):
        pass
    
    
    def test_multiple_mapping_multiple_context(self):
        pass
    
    

class TestRightContext:
    
        
    def test_single_mapping_single_context(self):
        pass
    
    
    def test_single_mapping_multiple_context(self):
        pass


    def test_mutiple_mapping_single_context(self):
        pass
    
    
    def test_multiple_mapping_multiple_context(self):
        pass
    



class TestDualContext:
    
        
    def test_single_mapping_single_context(self):
        pass
    
    
    def test_single_mapping_multiple_context(self):
        pass


    def test_mutiple_mapping_single_context(self):
        pass
    
    
    def test_multiple_mapping_multiple_context(self):
        pass
    

class TestMixedContexts:
    
    
    def test_single_mapping_multiple_context(self):
        pass

    
    def test_multiple_mapping_multiple_context(self):
        pass
    





