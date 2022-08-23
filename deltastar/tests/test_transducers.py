import pytest
import sys

# technically not needed, but this lets me run the files through cmd 
sys.path.append("/home/eric/python/projects/deltastar/") 
sys.path.append("/home/eric/python/projects/deltastar/deltastar")

from deltastar.transducers import assimilation, deletion, insertion

# the goal of these tests is to locate the inevitable edge cases that arise from certain combinations of contexts and mappings
# (i.e., the mapping contains symbols also found in the context and vice versa, multiple contexts share the same syms, etc...)
# that is why these most of these tests are filled with seemingly random and non-sensical combinations 

def get_syms(fst, in_out_pairs):
    """Takes (input, output) pairs and performs element-wise string comparison for each symbol for both strings
    
    Args:
        fst (deltastar.DFST): transducer to check the rewrite method of
        in_out_pairs (List[tuple]): (input, output) pairs to check

    Yields:
        sym1, sym2 (tuple[str]): symbols that fail the comparison
        len(rewrite), len(expected_string) (tuple[int]): ensures that both strings are of equal length
    """
    for input_string, expected_string in in_out_pairs:
        rewrite = fst.rewrite(input_string).split()
        expected_string = expected_string.split()
        
        report =  f"Input string: {input_string}\n\nRewrite string:  {' '.join(rewrite)}\nExpected string: {' '.join(expected_string)}"
        for sym1, sym2 in zip(rewrite, expected_string):
            
            # this block enforces that the strings are of equal length
            if len(rewrite) != len(expected_string):
                print(f"Strings of unequal length\n{report}")
                yield len(rewrite), len(expected_string)
            
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
    
    
    def test_Rcon_rewrite_3(self):
        
        fst = assimilation([("a", "b"), ("x", "y")], ["_ x y z", "_ b b", " _ a"])
        in_out_pairs = [
            ("x x x x x y z a x y z x b b a a a a a a a x y z x b b x a",
             "x x x y x y z b x y z y b b b b b b b b b x y z y b b y a"),
            
            ("a a a f a x y x y z x x y z a a x a", 
             "b b a f a x y x y z y x y z b a y a"),  
            
            ("x x x a a a a b b x x x b b x a",
             "x x y b b b b b b x x y b b y a"),
            
            ("x a x a x x y z x x y z a x a a",
             "y a y a y x y z y x y z a y b a"),
            
            ("a b b b b x x b x x x a x y z",
             "b b b b b x x b x x y b x y z"),
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
         
         
    def test_Dcon_rewrite_2(self):
        
        fst = assimilation([("a", "X"), ("b", "Y")], ["a c _ c b"])
        
        in_out_pairs = [
            ("a c a c b a a a a a c b c b a a a a c a c a c a c b b a c a c b c b",
             "a c X c b a a a a a c Y c b a a a a c a c a c X c b b a c X c Y c b"),
            
            ("a c a c a c b b b b a c b c b c b a c a c b",
             "a c a c X c b b b b a c Y c b c b a c X c b"),
            
            ("a c b c b a c a c b a c b c a c b c b",
             "a c Y c b a c X c b a c b c a c Y c b"),
            
            ("a a a c c c b b b c c c b b b [mod=imp] a c a c b",
             "a a a c c c b b b c c c b b b [mod=imp] a c X c b"),
            
            ("[this] [is] [a] [test] a c a c a c b [for] [tag] c b c b a c b c b [handling]",
             "[this] [is] [a] [test] a c a c X c b [for] [tag] c b c b a c Y c b [handling]"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym 
      
            
    def test_Dcon_rewrite_3(self):
        
        fst = assimilation([("g", "G"), ("f", "F")], ["$ f g _ f y", "$ w _ p p", "b _ b"])
        
        in_out_pairs = [
            ("f g g f y f g g f y f g f g w f p p b b b g b g b g b f b f b",
             "f g G f y f g g f y f g f g w f p p b b b G b G b G b F b F b"),
            
            ("b b b f b g f b b f g g f y [test]",
             "b b b F b g f b b f g g f y [test]"),
            
            ("w g p p g g f f f f f w f p p g f f f g f f y",
             "w G p p g g f f f f f w f p p g f f f g f f y"),
            
            ("w w w w g p p b b b b f b f f f b g b g g b b",
             "w w w w g p p b b b b F b f f f b G b g g b b"),
            
            ("f g g f y f y f g f f y",
             "f g G f y f y f g f f y"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym 
    
   
class TestDeletion:
    
    def test_Lcon_rewrite_1(self):
        
        fst = deletion([("a", ""), ("x", ""), ("[TEST]", ""), ("c", "")], ["b _", "p p p _", "x y z _", "g g a _"])
        in_out_pairs = [
            ("b a b a p p p p p a x y x y x y z x b b p p b b a p p p x",
             "b b p p p p p x y x y x y z b b p p b b p p p"),
            
            ("b b b [TEST] p b p b p p p x b x y z x y z a",
             "b b b p b p b p p p b y z y z"),
            
            ("b p b p x y z x y z [TEST] p p p a b [TEST] p p p [TEST] x y z x y z a",
             "b p b p x y z y z p p p b p p p x y z y z"),
            
            ("x x x y z b a g g g g a x y z g g a x y z [TEST] p p p p x x y z x",
             "x x x y z b g g g g a y z g g a y z p p p p x y z"),
            
            ("c a c a b c a g g g a c [TEST] b [TEST] x y z x y z g g a c x y z c",
             "c a c a b a g g g a [TEST] b x y z y z g g a x y z"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    
    def test_Lcon_rewrite_2(self):
        
        fst = deletion([("g", ""), ("t", ""), ("p", "")], ["a b c _", "g t p _", "t h e _", "p o w _"])
        in_out_pairs = [
            ("g t p g t p a a a a b c p t t h h e e t h e g t g g g t p p t t g t p g",
             "g t p t p a a a a b c t t h h e e t h e t g g g t p t t g t p"),
            
            ("a b a b a b c t t t h e g t p a b c t g t p o w t",
             "a b a b a b c t t h e t p a b c g t p o w"),
            
            ("p p o w g t p p g t p g t p t a a b c g t p t h e p o w g",
             "p p o w t p g t p t p a a b c t p h e o w"),
            
            ("g g g t p g g g t a b c t h h e p o w w p t h e g t a b a b c c g a b c t",
             "g g g t p g g t a b c h h e p o w w p t h e t a b a b c c g a b c"),
            
            ("t t t h e p o w p o w a a b c g t p p",
             "t t t h e o w o w a a b c t p"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
            
                  
    def test_Lcon_rewrite_3(self):
        
        fst = deletion([("[HELLO]", ""), ("s", ""), ("[TAG]", "")], ["$ d u d e _", "t o a s t _", "s s s _", "y x y _"])
        in_out_pairs = [
            ("s s [HELLO] s [TAG] t t s s t o a s t s s s s s s [TAG] t o o t o a s t [HELLO]",
             "s s [HELLO] s [TAG] t t s s t o a s t s s t o o t o a s t"),
            
            ("d u d e [TAG] d u d e [HELLO] a a a t t o a s t t o a s t s",
             "d u d e d u d e [HELLO] a a a t t o a s t t o a s t"),
            
            ("s t o a s t [HELLO] [TAG] s s s s s s s s [TAG] d u d u d e t o a s t s",
             "s t o a s t [TAG] s s s d u d u d e t o a s t"),
            
            ("y y x y [HELLO] [HELLO] s d u d e s t o a t o a s t s a s t [TAG] s s s y x y x x y x y s",
             "y y x y [HELLO] s d u d e s t o a t o a s t a s t [TAG] s s s y x y x x y x y"),
            
            ("d d u d e s s s [TAG] s [HELLO] y y y y x y [TAG]",
             "d d u d e s s s s [HELLO] y y y y x y"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
            
            
    def test_Rcon_rewrite_1(self):
        
        fst = deletion([("[JEFF]", ""), ("[SCOTT]", ""), ("w", ""), ("a", "")], ["_ c c c", "_ w y z", "_ p p"])
        in_out_pairs = [
            ("[JEFF] c c w y y y w w [SCOTT] p p w w y w w y z [JEFF] c c c",
             "[JEFF] c c w y y y w w p p w w y w y z c c c"),
            
            ("w w w w w p p a p [JEFF] c c a p [SCOTT] [SCOTT] c c c c c c w w y c c c a p p",
             "w w w w p p a p [JEFF] c c a p [SCOTT] c c c c c c w w y c c c p p"),
            
            ("w w w c c c w w y z [SCOTT] p a c c c w y z",
             "w w c c c w y z [SCOTT] p c c c w y z"),
            
            ("[JEFF] c c c [SCOTT] p p w w w y z p p a p p",
             "c c c p p w w y z p p p p"),
            
            ("c c c c w w y w y z w c c c [SCOTT] [JEFF] p p w w y w c c c",
             "c c c c w w y w y z c c c [SCOTT] p p w w y c c c"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    
    def test_Rcon_rewrite_2(self):
        
        fst = deletion([("x", ""), ("y", ""), ("z", "")], ["_ y a y $", "_ x y z", "_ x x x y"])
        in_out_pairs = [
            ("x y a y x x x y x y z z x x y x x x y x y z z y a y",
             "x y a x x x x y z z x x x x x x y z y a y"),
            
            ("z z z x y z x x x y y y y a y x y z x x x x y z y a y",
             "z z x y  x x x y y y y a x y z x x y y a y"),
            
            ("x x y y z z x x y z z y a y x y z x y z x x x y",
             "x x y y z z x y z z y a x y x y x x x y"),
            
            ("x x x x x x y x y z y a y",
             "x x x x x x y y a y"),
            
            ("y z y z x z y x y z x x x y x y x y z",
             "y z y z x z x y x x x y x x y z"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
            
        
    def test_Rcon_rewrite_3(self):
        
        fst = deletion([("f", ""), ("c", "")], ["_ c c c $", "_ p f a $", "_ o f", "_ o o p"])
        in_out_pairs = [
            ("c c c c c c c f f f o f c o f p f a c p f a",
             "c c c c c c c f f o f o f p f a p f a"),
            
            ("p f p f c o f o f c c c c c c",
             "p f p f o o f c c c c c"),
            
            ("o o o f o o p c c c c f o f o c o o p f o f c c c c",
             "o o o o o p c c c c o f o o o p o f c c c"),
            
            ("o f o p c c p f a o f o o o p c p f a",
             "o f o p c c p f a o f o o o p p f a"),
            
            ("p f p f o f c p c a o f c o f o o p c c c c",
             "p f p o f c p c a o f o o o p c c c"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    
    def test_Dcon_rewrite_1(self):
        
        fst = deletion([("u", ""), ("t", ""), ("e", "")], ["d _ d", "d _ t", "u _ e"])
        in_out_pairs = [
            ("d d d t t u u e d u d u t u t e u e e",
             "d d d t u e d d t u e u e"),
            
            ("u d t u t e e d e d t t u d e d d e t t",
             "u d t u e e d d t u d d d t t"),
            
            ("u u u u u t e u t u t d e d e t u d u d e",
             "u u u u u e u t u t d d t u d d e"),
            
            ("d e d e t e u u e u u u t e",
             "d d t e u e u u u e"),
            
            ("e e u e e t e t e d e d e t u u t d u t",
             "e e u e t e t e d d t u u t d t"),
        ]
        for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
            assert rewrite_sym == expected_sym
    
    
    def test_Dcon_rewrite_2(self):
        
        fst = deletion([("[WOW]", ""), ("p", ""), ("i", "")], ["i i _ i i"])
        in_out_pairs = [
            ("i i i i i i i",
             "i i i i"),
            
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
        
        fst = deletion([()], [])
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
    
    
    #! template code
    # @pytest.mark.skip(reason="Not Implemened Yet")
    # def test_(self):
        
    #     fst = ([()], [])
    #     in_out_pairs = [
    #         ("",
    #          ""),
            
    #         ("",
    #          ""),
            
    #         ("",
    #          ""),
            
    #         ("",
    #          ""),
            
    #         ("",
    #          ""),
    #     ]
    #     for rewrite_sym, expected_sym in get_syms(fst, in_out_pairs):
    #         assert rewrite_sym == expected_sym
    

