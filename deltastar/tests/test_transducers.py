import pytest
import sys

# technically not needed, but this lets me run the files through cmd if needed
sys.path.append("/home/eric/python/projects/deltastar/") 
sys.path.append("/home/eric/python/projects/deltastar/deltastar")

from deltastar.transducers import assimilation, deletion, insertion

# the goal of these tests is to locate the inevitable edge cases that arise from certain combinations of contexts and mappings
# (i.e., the mapping contains symbols also found in the context and vice versa, multiple contexts share the same get_syms, etc...)
# that is why these most of these tests are filled with seemingly random and non-sensical combinations 

# the following rewrite rules match most (or all) of the ones seen in test_transitions


def get_syms(fst, in_out_pairs):
    """Takes (input, output) pairs and performs element-wise string comparison for each symbol for both strings
    
    Args:
        fst (deltastar.DFST): transducer to check the rewrite method of
        in_out_pairs (List[tuple]): (input, output) pairs to check

    Yields:
        sym1, sym2 (tuple[str]): symbols that fail the comparison
    """
    for input_string, expected_string in in_out_pairs:
        rewrite = fst.rewrite(input_string).split()
        expected_string = expected_string.split()
        
        report =  f"Input string: {input_string}\n\nRewrite string:  {' '.join(rewrite)}\nExpected string: {' '.join(expected_string)}"
        for sym1, sym2 in zip(rewrite, expected_string):
            
            # this block enforces that the strings are of equal length
            if len(rewrite) != len(expected_string):
                print(f"Strings of unequal length\n{report}")
                yield True, False
            
            elif sym1 != sym2:
                print(report)
                yield sym1, sym2

class TestAssimilation:
    
    def test_Lcon_rewrite_1(self):
        fst = assimilation([("a", "b"), ("x", "y")], ["a c a b _", "x y z _"])
        
        in_out_pairs = [
            
            ("a c a b a", 
             "a c a b b"),
            
            ("a a a c a b a a", 
             "a a a c a b b a"),
            
            ("h e l l o a c a b x", 
             "h e l l o a c a b y"),
            
            ("a c a b a c a b x a c a b x", 
             "a c a b b c a b y a c a b y"),
            
            ("a c a c a c a b a c a a b a", 
             "a c a c a c a b b c a a b a"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
     

    def test_Lcon_rewrite_2(self):
        fst = assimilation([("b", "p"), ("d", "t")], ["b a b a _", "$ f o o _", "b b b _"])
        
        in_out_pairs = [
            ("x y f o o b b b d",
             "x y f o o b b b t"),
            
            ("f o o d e r i c b a b a b b a b a b a d",
             "f o o t e r i c b a b a p b a b a p a t"),
            
            ("b a b a f o o b a b a d",
             "b a b a f o o b a b a t"),
            
            ("b b b b b b b a a b a b a d",
             "b b b p p p p a a b a b a t"),
            
            ("b b b d d d f o o o b f o o d",
             "b b b t d d f o o o b f o o d"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
   
    def test_Lcon_rewrite_3(self):
        fst = assimilation([("a", "b")], ["a c a b _", "c c _", "b _", ])
    
        in_out_pairs = [
            ("c c a c a b a",
             "c c b c a b b"),
            
            ("a c a c a b a c c c a",
             "a c a c a b b c c c b"),
            
            ("b b b a b a c a b a c c b a",
             "b b b b b b c a b b c c b b"),
            
            ("t h i s i s a t e s t s t r i n g a c a b a c c a",
             "t h i s i s a t e s t s t r i n g a c a b b c c b"),
            
            ("c c b a c a c c a c a b a b b b a c c c b c c a",
             "c c b b c a c c b c a b b b b b b c c c b c c b"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
   
    def test_Rcon_rewrite_1(self):
        
        fst = assimilation([("a", "b")], ["_ a b a b"])
        in_out_pairs = [
            ("a a b a b b b a a b a a b a b",
             "b a b a b b b a a b b a b a b"),
            
            ("b b b a a b a b a a a a b a b a a b a a b",
             "b b b b a b a b a a b a b a b a a b a a b "),
            
            ("a a a a b a b e r i c a b b a a b a b a b a b b c",
             "a a b a b a b e r i c a b b b a b a b a b a b b c"),
            
            ("a b b a a b b a a a b a b a",
             "a b b a a b b a b a b a b a"),
            
            ("b a b a a a a b a a b a b",
             "b a b a a a a b b a b a b"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    def test_Rcon_rewrite_2(self):
        
        fst = assimilation([("g", "G")], ["_ g g f f", "_ z z"])
        
        in_out_pairs = [
            ("g g g g g g f f g z z g g z g z z",
             "g g g G g g f f G z z g g z G z z"),
            
            ("g z g z g g g f g g g f f g z g z z",
             "g z g z g g g f G g g f f g z G z z"),
            
            ("z z z z g g g f f f g g f f g",
             "z z z z G g g f f f g g f f g"),
            
            ("g g g f f g g g f f g z z g z z",
             "G g g f f G g g f f G z z G z z"),
            
            ("g f g f g g g f f z z g z g z z g g g f f",
             "g f g f G g g f f z z g z G z z G g g f f"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    #@pytest.mark.skip(reason="Contains an annoying edge case, so disabling for now") 
    def test_Rcon_rewrite_3(self):
        
        fst = assimilation([("a", "b"), ("x", "y")], ["_ x y z", "_ b b", " _ a"])
        in_out_pairs = [
            ("x x x x x y z a x y z x b b a a a a a a a x y z x b b x a",
             "x x x y x y z b x y z y b b b b b b b b b x y z y b b y a"),
            
            ("a a a f a x y x y z x x y z a a x a", 
             "b b a f a x y x y z y x y z b a y a"),  
            
            ("",
             ""),
            
            ("",
             ""),
            
            ("",
             ""),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
            
    def test_Dcon_rewrite_1(self):
        
        fst = assimilation([("a", "A"), ("h", "H")], ["x y z _ z y x"])
        in_out_pairs = [
            ("x x x x y z a z y x y z h z y x",
             "x x x x y z A z y x y z H z y x"),
            
            ("x y z x y z a z y q y z h h z y x x x x y z a z y x",
             "x y z x y z a z y q y z h h z y x x x x y z A z y x"),
            
            ("z y x x y z a a z y x y z h z y x",
             "z y x x y z a a z y x y z H z y x"),
            
            ("x y z x y z x y z a z y x y z z y x y z h z y x",
             "x y z x y z x y z A z y x y z z y x y z H z y x"),
            
            ("x y x y x y x y z a x y z a z y x y y x z z x y z h h z y x x y z h",
             "x y x y x y x y z a x y z A z y x y y x z z x y z h h z y x x y z h"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym      
        
    @pytest.mark.skip(reason="Contains an annoying edge case, so disabling for now") 
    def test_Dcon_rewrite_2(self):
        
        #! contains an issue where the right context prefix transition is sending too many symbols to output tape
        
        fst = assimilation([("a", "X"), ("b", "Y")], ["a c _ c b"])
        
        in_out_pairs = [
            ("a c a c b",
             "a c X c b"),
            
            ("",
             ""),
            
            ("",
             ""),
            
            ("",
             ""),
            
            ("",
             ""),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym 
      
            
    @pytest.mark.skip(reason="Not Implemened Yet") 
    def test_Dcon_rewrite_3(self):
        
        fst = assimilation([()], [])
        
        in_out_pairs = [
            ("",
             ""),
            
            ("",
             ""),
            
            ("",
             ""),
            
            ("",
             ""),
            
            ("",
             ""),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym 
    
        
    @pytest.mark.skip(reason="Not Implemened Yet") 
    def test_Mixedcon_rewrite_1(self):
        
        fst = assimilation([()], [])
        in_out_pairs = [
            ("",""),
            
            ("",""),
            
            ("",""),
            
            ("",""),
            
            ("",""),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
       
        
    @pytest.mark.skip(reason="Not Implemened Yet") 
    def test_Mixedcon_rewrite_2(self):
        
        fst = assimilation([()], [])
        in_out_pairs = [
            ("",""),
            
            ("",""),
            
            ("",""),
            
            ("",""),
            
            ("",""),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
       
    
@pytest.mark.skip(reason="Not Implemened Yet")     
class TestDeletion:
    
    def test_Lcon_rewrite_1(self):
        
        fst = deletion([()], [])
        in_out_pairs = [
            ("",""),
            
            ("",""),
            
            ("",""),
            
            ("",""),
            
            ("",""),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    def test_Lcon_rewrite_2(self):
        pass
    
    def test_Rcon_rewrite_1(self):
        pass
    
    def test_Rcon_rewrite_2(self):
        pass
    
    def test_Dcon_rewrite_1(self):
        pass
    
    def test_Dcon_rewrite_2(self):
        pass
    
    def test_Mixedcon_rewrite_1(self):
        pass
    
    def test_Mixedcon_rewrite_2(self):
        pass

@pytest.mark.skip(reason="Not Implemened Yet") 
class TestInsertion:
    
    def test_Lcon_rewrite_1(self):
        pass
    
    def test_Lcon_rewrite_2(self):
        pass
    
    def test_Rcon_rewrite_1(self):
        pass
    
    def test_Rcon_rewrite_2(self):
        pass
    
    def test_Dcon_rewrite_1(self):
        pass
    
    def test_Dcon_rewrite_2(self):
        pass
    
    def test_Mixedcon_rewrite_1(self):
        pass
    
    def test_Mixedcon_rewrite_2(self):
        pass
    

