# DeltaStar

`DeltaStar` is a library for constructing finite-state string transducers.

**[Finite-state automata](https://en.wikipedia.org/wiki/Finite-state_machine)** are valued by linguists and computer scientists alike because of their **powerful text manipulation capabilities**. Linguists in particular make heavy use of [finite-state transducers](https://en.wikipedia.org/wiki/Finite-state_transducer) to model *phonological* and *morphological* string rewrite rules, which it turns out, transducers hold a nearly 1-to-1 correspondence to.

There is a sparse amount of python libraries for constructing FSTs. The only library I know that approaches the same subject is [Pynini](https://pypi.org/project/pynini/), an excellent python library that is a wrapper for [OpenFST](https://www.openfst.org/twiki/bin/view/FST/WebHome), a c++ library that hosts powerful finite-state machines. Since Pynini's functionality is c++ based however, all operations in it are done in the background and it is not intuitive to see the actual transductions occur. 

With this in mind, I wanted to make a python-based approach that explicitly showed every transition. Finite-state machines can be rather jarring when approaching them for the first time, so I think it's a good idea to value explicitness and show everything that's occurring inside the machine. Alongside this, `DeltaStar` was written with linguistic rewrite rules specifically in mind and the syntax reflects this. 

I hope this project is useful and comes in handy for those who deem it so. If you use this software for research or projects, kindly throw a link back to this repository :)

## Files

- `transducers.py` - main file containing the DFST code (Note: in the documentation below, I prefix all dfst examples with 'ds'. This is for when it is eventually released to the public. If you want to test the code yourself with custom machines, do so in this file and just use the `rewrite` function)
- `examples/malarky.py` - file containing test rewrite rules for the wonderful language of Malarky 

## Installation

### Not working yet

```bash
pip install deltastar
```
or
```bash
pip3 install deltastar
```

## Disclaimer
first project

## Note
A large portion of the README will eventually be migrated to a separate documentation file, complete with more detailed explanations and examples.

## Usage and current implementations

All transducers must be created using the same pattern:

```python
import deltastar as ds

rule = ds.rewrite(INPUT_SYMBOL(S), OUTPUT_SYMBOL(S), CONTEXT)
```
where:

   - **INPUT_SYMBOL(S)** = the input symbols to be changed. 
   - **OUTPUT_SYMBOL(S)** = the output symbols that get changed into. 
   - **CONTEXT** = the environment in which the transduction takes place. 

`Notes`: 
- Each mapping between INPUT and OUTPUT *must* be **space delimited**.
- **INPUT** and **OUTPUT** must have a 1 to 1 correspondence 
- **Context** can be left empty for context free mappings.
- Beware: When it comes to **multiple mappings**, it's possible to have them override each other.

### Possible types of transductions:

- **Context free rewrite rules** -
```python

# a -> b / _ "Every 'a' turns into a 'b' regardless of context"
a_to_b_cf = ds.rewrite("a", "b")

# apply your newly created transducer to strings!

print(a_to_b_cf("aaabbbcccddd")
>>> "bbbbbbcccddd"

# multiple mappings at once!
# a -> x / _ ,   b -> y / _ ,   c -> z / _
multiple_mappings_cf = ds.rewrite("a b c", "x y z")

print(multiple_mappings_cf("abcabcabc a b c c b a"))
>>> "xyzxyzxyz x y z z y x"

# a small example showing that each output can be of arbitrary length
test = rewrite("a b c", "XXX YYY ZZZ")
print(test("abc"))
>>> "XXXYYYZZZ"
```


- **Left context dependent rewrite rules** -
```python
# a -> b  / c _ "Every 'a' turns into a 'b' when it follows a 'c' "
a_to_b_after_c = ds.rewrite("a", "b", "c_")

print(a_to_b_after_c("caacaa"))
>>> "cbacba"

print(a_to_b_after_c("caaa"))
>>> "cbaa"


# multiple left contexts!

# a -> b / x _,  a -> b / y _,  a -> b / z _
multiple_contexts = ds.rewrite("a", "b", "x y z _")
print(multiple_contexts("xa ya za xxxa yyya zzza")) # space delimited for easier reading!
>>> "xb yb zb xxxb yyyb zzzb"


# multiple mappings AND multiple left contexts!
multiple_mappings_and_contexts = ds.rewrite("a b c d", "e f g h", "x y z _")
print(multiple_mappings_and_contexts("xa xb xc xd ya yb yc yd za zb zc zd")) # space delimited for easier reading!
>>> "xe xf xg xh ye yf yg yh ze zf zg zh"

```
- **Deletion rewrite rules** - (Note: deletion is freshly implemented and does contains bugs)
```python

# a -> ∅ / a _ "Every 'a' alternates with ∅ (deletes) after it follows an another 'a' "
delete_a = ds.rewrite("a", "", "a_",)
print(delete_a("aa"))
>> "a"

# a -> ∅ / _,   b -> ∅ / _,   c -> ∅ / _
delete_a_b_c = ds.rewrite("a b c", "")
print(delete_a_b_c("abcxyzabc"))
>> "xyz"

```


## Detailed explanations

When you call `deltastar.rewrite` and provide the function with a mapping, it automatically generates transitions from state to state. The initial state always starts at "<>". The machine then iterates over the (left) context and creates a new state consisting of the longest prefix seen. For example:
```
a -> b / cccc _

STATES: <> -> <c> -> <cc> -> <ccc> -> <cccc>
```
This is the full set of transitions generated for the above rewrite rule (from my code):
```
~~~~~~~Delta:~~~~~~~
<> --(c : c)--> <c>        From state <>, given 'c', I output a 'c' and move to state <c>
<> --(? : ?)--> <>
<c> --(c : c)--> <cc>      From state <c>, given 'c', I output a 'c' and move to state <cc>
<c> --(? : ?)--> <>
<cc> --(? : ?)--> <>
<cc> --(c : c)--> <ccc>    From state <cc>, given 'c', I output a 'c' and move to state <ccc>
<ccc> --(? : ?)--> <>
<ccc> --(c : c)--> <cccc>  From state <ccc>, given 'c', I output a 'c' and move to state <cccc>
<cccc> --(a : b)--> <>     From state <cccc>, given 'a', I output a 'b' and move to state <>
<cccc> --(c : c)--> <cccc> From state <cccc>, given 'c', I output a 'c' and move to state <cccc>
<cccc> --(? : ?)--> <>
~~~~~~~~~~~~~~~~~~~~
```
In the text above, the mappings are shown as (INPUT : OUTPUT). The question marks indicate symbols received that are not a part of the context. Thus, they all map back to the initial state. When the program encounters a symbol not in the context, it just moves to the initial state and outputs the received symbol. 

All transitions are stored in a dictionary. The above (minus the explanation text) is what is printed when you set the `displayparams` argument in `deltastar.rewrite` to True.

When it comes time to operate over a string, the user-created DFST lambda function just does a simple lookup to find transitions for each input symbol.

Additionally, when it comes to multiple contexts, they get internally parsed as follows:
```python
("a", "b", "x y z _") -> ("x_", "y_", "z_")
```
So you can think of the above rewrite rule as a compilation of the following rules:
```python
("a", "b","x_")
("a", "b","y_")
("a", "b","z_")
```
I think this syntax is efficient since often times, especially in linguistics, you're going to have a **grouping of symbols** that need to experience a change.

## Future plans

### Currently working on:

- implementing right contexts
- implementing dual sided contexts

### Definite additions (no order):
- right context handling
- composition / intersection
- word initial / final detection rules
- handle insertion and deletion rules (INCLUDE EOW / BOW)
- have an OSL / ISL mode switch
- dot file drawing capability (similar to Pynini)
- make user able to manually add / delete transitions
- make a model pickle function?


### Possible additions:

- non deterministic transducers
- 2-way transducers
- weighted FSTS
- monoidzz

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
