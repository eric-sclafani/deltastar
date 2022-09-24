# Overview
In its current state, `Deltastar` is a program that compiles rewrite rules into deterministic **finite-state string transducers** (FSTs). 
This type of machine is designed to edit (transduce) a string according to a defined set of mappings.

Linguists value FSTs because of their correspondance with rewrite rules, for which both *phonology* and *morphology* in particular 
have an abundance of. One can encode these linguistic mappings though finite-state string transducers.

# Note

The code base is undergoing very heavy reconstruction. Refer to `refactoring.md` for more details.

Check out the `dev` branch for the most recent updates!

# Inspiration

This project is directly inspired by [Pynini](https://pypi.org/project/pynini/), a python wrapper for the C++ library [OpenFST](https://www.openfst.org/twiki/bin/view/FST/WebHome) that hosts a powerful API for constructing FSTs. 
Through projects and experimentation, I have grown quite fond of Pynini and it seems (to me at least) that the bounds for 
the types of machines you want to make are seemingly endless. 

However, in my opinion, Pynini's API is not straight forward. As a linguist, when I began my Pynini journey, I had no formal language theory background.
Thus, it took a good chunk of time to understand the API and what was happening behind the scenes.

You may say, of course, that one should only use these machines provided they have prior knowledge of them. I disagree with this notion, for I became infatuated with finite-state technology long before I was exposed to the formalisms.  

This leads me to discuss the reason for Deltastar: I wish to make a fully-fledged DFST library with an API that is both approachable to people new to formal language theory, and scalable for those who already have a background. 

One more point is that OpenFST computes **`non-deterministic`** FSTs from the ground up. Without going into great detail (yet), these types of machines are indeed powerful and expressive but lack certain qualities that deterministic machines have that I and other computational linguists value. I seek to write a formula for creating FSTs that is **`deterministic by construction`**. That is, there will only ever exist one path that a string can traverse.




# Usage

If you wish to experiment with the code, feel free to do so by forking the repo. However, the API will most likely see a dramatic change. 


Currently, there are three factory functions to construct a DFST inside of `transducers.py`: **assimilation**, **deletion**, and **insertion** 
(appropriately named for what types of rules they're used for, of course). 

Finally, below are examples on how to use the API. For more intricate examples, see the `deltastar/examples/` directory.

## Context specification

Multiple contexts can be specified for a single machine. One inputs a **list of contexts during instantiation**. The context strings must take the following format:
```python
- Left:  X Y Z _
- Right: _ X Y Z
- Dual:  X Y Z _ A B C
```
where the underscore ( _ ) indicates where the transduction should occur.

For `context-free machines`, do not specify contexts at all. Everthing becomes a self loop on the initial state then.

**For a single machine, the contexts must be homogenous**; you cannot mix left context with right context, left context with dual context, right context with dual context:

```python
VALID CONTEXTS: ["a b _", "c c c _"], 
                ["_ y", "_ x y z", "_ l m a o"], 
                ["b c _ c b", "h h _ h h"]  

INVALID CONTEXT: ["g g _", "p _ p", "_ o o o"]
```



## Mapping specification

Mappings must be specified as a list of ( INPUT, OUTPUT ) pairs:

```python
>>> [("a", "b"), ("x", "y"), ("[tns=pst]", "ed")]
```

## String input

Each function expects symbols to be space delimited. This allows for symbols to have multiple characters:
```
"t h i s i s a s t r i n g"

"[tns=pst] [mod=imp] v e r b [pol=neg] [trns=yes]"
```

## Assimilation

**Assimilation** rules map input symbols to new symbols. The snippet below shows one mapping and one context:

```python
>>> fst = assimilation([("a", "b")], ["a c a b _"])
```
Input your string into the `.rewrite()` and behold the magic:
```python
>>> print(fst.rewrite("a c a b a"))
"a c a b b"
```

You can use the **.displayparams** method to get a summary of the parameters of your machine:
```python
>>> fst.displayparams

~~~~~~~Rewrite rules:~~~~~~~
a -> b / a c a b _
~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

Σ: {'a', 'c', 'b'}
Γ: {'a', 'c', 'b'}
Q: {'<aca>', '<ac>', '<acab>', '<λ>', '<a>'}
q0: <λ>
v0: None
Finals: {'<λ>': '', '<a>': '', '<ac>': '', '<aca>': '', '<acab>': ''}
Delta:
╒═════════╤═════════╤══════════╤════════╕
│ Start   │ Insym   │ Outsym   │ End    │
╞═════════╪═════════╪══════════╪════════╡
│ <λ>     │ a       │ a        │ <a>    │
│ <λ>     │ ?       │ ?        │ <λ>    │
│ <a>     │ c       │ c        │ <ac>   │
│ <a>     │ ?       │ ?        │ <λ>    │
│ <a>     │ a       │ a        │ <a>    │
│ <ac>    │ a       │ a        │ <aca>  │
│ <ac>    │ ?       │ ?        │ <λ>    │
│ <aca>   │ b       │ b        │ <acab> │
│ <aca>   │ ?       │ ?        │ <λ>    │
│ <aca>   │ c       │ c        │ <ac>   │
│ <aca>   │ a       │ a        │ <a>    │
│ <acab>  │ a       │ b        │ <a>    │
│ <acab>  │ ?       │ ?        │ <λ>    │
╘═════════╧═════════╧══════════╧════════╛
```

Starting from the top, each entry in `Delta` can be read as:
        
    Given a start state and input symbol, what do I output and which state do I travel to?

The `<λ>` state indicates the initial state of the machine, or the **empty state**. Each state label represents 
all symbols seen leading up to that state.

The `?` is a placeholder representing symbols that have no transition. For example, if you're in state `<aca>` 
and receive a `x` insym, no transition exists for it and you go back to the empty state and output the `x`.


## Deletion

**Deletion** rules map input symbols to the empty string. How is the empty string treated in this case?
Symbols are mapped to null "Ø" and then removed before the output is returned to the user:
```python

>>> fst = deletion([("a", "")], ["b _ b",])
>>> print(fst.rewrite("a a b a b a b b b a b"))
'a a b b b b b b'

>>> fst.displayparams

~~~~~~~Rewrite rules:~~~~~~~
a -> Ø / b _ b
~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

Σ: {'b', 'a'}
Γ: {'b', 'a'}
Q: {'<λ>', '<b>', '<ba>'}
q0: <λ>
v0: None
Finals: {'<λ>': '', '<b>': '', '<ba>': 'a'}
Delta:
╒═════════╤═════════╤══════════╤═══════╕
│ Start   │ Insym   │ Outsym   │ End   │
╞═════════╪═════════╪══════════╪═══════╡
│ <λ>     │ b       │ b        │ <b>   │
│ <λ>     │ ?       │ ?        │ <λ>   │
│ <b>     │ ?       │ ?        │ <λ>   │
│ <b>     │ a       │ λ        │ <ba>  │
│ <b>     │ b       │ b        │ <b>   │
│ <ba>    │ b       │ Øbλ      │ <b>   │
│ <ba>    │ ?       │ a?       │ <λ>   │
╘═════════╧═════════╧══════════╧═══════╛

``` 
**Delta** here looks a little different from the **assimilation** example, with lambdas and symbols combined with the place holder **?** in the outsym (**a?**).
This is because of how right and dual contexts are treated in my algorithm.

So what do the lambdas mean? A transition will send **λ** to the output tape if and only if it
travels into a state associated with a right or dual context. **λ** gets removed before the output is returned to the user. 

In other words, **λ** ( in the outsym column) means:
    
    I have seen an input symbol, but have not sent a corresponding symbol to the output tape.

This formalism adds no functionality. It is merely a visual indication of the above occurence. In some situations, you may see symbols combined with lambda, so maybe **xyzλ**. This occurs during right and dual context transitions and basically means:

    Hey, I'm going into a state where I have not sent anything to the output tape, 
    but I'm holding onto symbols from a right or dual context I've seen already, so I must output them now.
    
Don't worry if that doesn't make sense. It's only important to know if you want to modify the messy transition code (good luck lol). 

## Insertion

**Insertion** rules require more steps. Because we need to detect the empty string, which is not a character in itself, **`we need to make it a character`**. This is done by interspersing the context and user's input with "Ø" symbols:

( **`Disclaimer`**: because of this wacky handling of **insertion** rules, the transitions are highly volatile. For simple machines (i.e. one or two small contexts), the code will *most likely* work. But for anything more, don't be surprised if it doesn't. )

```python

>>> fst = insertion([("", "x"), ], ["_ m", "_ l o l"])
>>> print(fst.rewrite("m m m l l o l"))
'x m x m x m l x l o l'

>>> fst.displayparams
~~~~~~~Rewrite rules:~~~~~~~
Ø -> x / _ m Ø m
Ø -> x / _ l Ø o Ø l
~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

Σ: {'o', 'm', 'l'}
Γ: {'o', 'x', 'm', 'l'}
Q: {'<Øm>', '<ØlØo>', '<Ø>', '<λ>', '<ØlØ>', '<ØlØoØ>', '<ØmØ>', '<Øl>'}
q0: <λ>
v0: None
Finals: {'<λ>': '', '<Ø>': 'Ø', '<Øm>': 'Øm', '<ØmØ>': 'ØmØ', '<Øl>': 'Øl', '<ØlØ>': 'ØlØ', '<ØlØo>': 'ØlØo', '<ØlØoØ>': 'ØlØoØ'}
Delta:
╒═════════╤═════════╤══════════╤═════════╕
│ Start   │ Insym   │ Outsym   │ End     │
╞═════════╪═════════╪══════════╪═════════╡
│ <λ>     │ Ø       │ λ        │ <Ø>     │
│ <λ>     │ ?       │ ?        │ <λ>     │
│ <Ø>     │ m       │ λ        │ <Øm>    │
│ <Ø>     │ ?       │ Ø?       │ <λ>     │
│ <Ø>     │ l       │ λ        │ <Øl>    │
│ <Ø>     │ Ø       │ Øλ       │ <Ø>     │
│ <Øm>    │ Ø       │ λ        │ <ØmØ>   │
│ <Øm>    │ ?       │ Øm?      │ <λ>     │
│ <ØmØ>   │ m       │ xmλ      │ <Øm>    │
│ <ØmØ>   │ ?       │ ØmØ?     │ <λ>     │
│ <ØmØ>   │ l       │ Ømλ      │ <Øl>    │
│ <ØmØ>   │ Ø       │ ØmØλ     │ <Ø>     │
│ <Øl>    │ Ø       │ λ        │ <ØlØ>   │
│ <Øl>    │ ?       │ Øl?      │ <λ>     │
│ <ØlØ>   │ o       │ λ        │ <ØlØo>  │
│ <ØlØ>   │ ?       │ ØlØ?     │ <λ>     │
│ <ØlØ>   │ m       │ Ølλ      │ <Øm>    │
│ <ØlØ>   │ l       │ Ølλ      │ <Øl>    │
│ <ØlØ>   │ Ø       │ ØlØλ     │ <Ø>     │
│ <ØlØo>  │ Ø       │ λ        │ <ØlØoØ> │
│ <ØlØo>  │ ?       │ ØlØo?    │ <λ>     │
│ <ØlØoØ> │ l       │ xlØoλ    │ <Øl>    │
│ <ØlØoØ> │ ?       │ ØlØoØ?   │ <λ>     │
│ <ØlØoØ> │ m       │ ØlØoλ    │ <Øm>    │
│ <ØlØoØ> │ Ø       │ ØlØoØλ   │ <Ø>     │
╘═════════╧═════════╧══════════╧═════════╛
```
As you can see, the output of `.displayparams` here looks messy and hard to interpret. But its basically just your specified contexts interlaced with the null symbol. 

As mentioned before, because insertion is handled this way, sometimes transitions are just plain wrong. I'm not sure exactly why this is, it may have something to do with the null symbol getting involved with the $k$-prefix transitions. This was one of the last features implemented, so it is the least tested. 

This system will be overhauled during The Great Refactoring. It is clunky, ugly, and leads to more harm than good. 

I plan to change this system to instead detect the transduction environment and send an extra symbol (from your mapping) to the output tape. 

## Graphing

Using the `.to_graph()` method, one can create a picture of your machine through Graphviz and have it saved as a .png. Currently it only saves to the local directory and only saves as a .png.
```python
assimilation([("a", "b")], ["c _"]).to_graph()
```
(See the `my_machine.png` file for a graph of the above code)

## Tags

Another thing due to change are how "tags" are handled. I define tags as  multi-character symbols that represent some form of meaning. For example, morphological tags could look something like:
```python 
"[mod=imp]", "[tns=pst]", "[vce=psv]"
```
Basically, you need to enclose your tags with square brackets `[]`. During string parsing, all characters within those brackets are treated as one symbol. 

## Boundary symbols

One can specify mappings to occur at the beginning or end of string using the reserved `$` symbol:
```python
["$ b b _"]
["_ a b c $"]
["x y z _ $"]
```
(Another) `Disclaimer`: **insertion** sometimes doesn't play well with certain contexts involving boundary symbols. Just another case of my not-so-great implementation of insertion.

## Tests

To run the unit tests, cd to `deltastar/deltastar/tests` and run `pytest` in the terminal. Pytest will automatically detect the test file and run each function.


# Issues

`Please`, `please`, `please` if you encounter a bug (i.e. faulty transitions, output tape incorrect, etc...), open an issue. This helps me greatly because there are many edge cases w.r.t $k$-prefix transitions. This is evident from the wall of conditionals inside the `prefix_transitions` function.
I can't guarantee I'll be able to address the issue immediately, but know it will be seen and will assist in The Great Refactoring. 

In the issue, please include: 

- A brief description of the bug
- DFST object instantiation including the mappings and contexts
- Input string and expected output string

# Installation

Simply fork the repo and clone your copy onto your machine. 

I am currently using pipenv to manage my environment, although I may switch to something else later. If you're using pipenv, run `pipenv install` from the same directory. This will install all dependencies from the `Pipfile.lock` file. Then run `pipenv shell` to activate the environment.

Otherwise, you can just manually install the libraries specified in `Pipfile` by running `pip3 install <package_name>`. 

The graphing functionality requires [graphviz](https://graphviz.org/) to be installed.

Code was written in Python 3.10.

# Disclaimer

This is my first large scale endeavor, so if anyone has advice about project/code layout, I'm all ears.

# Contributions

Because of The Great Refactoring, I am currently not merging pull requests. However, you are still more than welcome to open them if you have suggestions for how to fix or optimize something.

# License
[MIT](https://choosealicense.com/licenses/mit/)
