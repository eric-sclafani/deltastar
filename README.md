# Overview
In its current state, `Deltastar` is a program that compiles rewrite rules into deterministic **finite-state string transducers** (FSTs). 
This type of machine is designed to edit (transduce) a string according to a defined set of mappings.

Linguists value FSTs because of their correspondance with rewrite rules, for which both *phonology* and *morphology* in particular 
have an abundance of. One can encode these linguistic mappings though finite-state string transducers.

# Inspiration

This project is directly inspired by [Pynini](https://pypi.org/project/pynini/), a python wrapper for the C++ library [OpenFST](https://www.openfst.org/twiki/bin/view/FST/WebHome) that hosts a powerful API for constructing FSTs. 
Through projects and experimentation, I have grown quite fond of Pynini and it seems (to me at least) that the bounds for 
the types of machines you want to make are seemingly endless. 

However, in my opinion, Pynini's API is not straight forward. As a linguist, when I began my Pynini journey, I had no formal language theory background.
Thus, it took a good chunk of time to understand the API and what was happening behind the scenes.

You may say, of course, that one should only use these machines provided they have prior knowledge. I disagree with this notion, for I became infatuated with finite-state technology long before I was exposed to the formalisms. 

This leads me to discuss the reason for Deltastar: I wish to make a fully-fledged FST library with an API that is both approachable and scalable.


# The Great Refactoring

I have learned a lot of things since I began this project, namely what my algorithms are capable of, and more importantly, **not capable of**. In order to sculpt deltastar to meet my vision, I need to refactor the entire code base. 

Like I mentioned before, deltastar in its current state is simply a rewrite rule compiler. However, I wish it to be more than that, which is why I've decided to not publish it to Pypi yet. Details for the sweeping changes are outlined
in TODO.md. 

# Usage

If you wish to experiment with the code, feel free to do so by forking the repo. However, the API will most likely see a dramatic change. 


Currently, there are three factory functions to construct a DFST inside of `transducers.py`: **assimilation**, **deletion**, and **insertion** 
(appropriately named for what types of rules they're used for, of course). 

Finally, below are examples on how to use the API. For more intricate examples, see the `examples/` directory

## Rule and mapping specification

For **assimilation** and **deletion** rewrite rules, one can specify multiple mappings and contexts for those mappings. This feature is temporary because it is a placeholder for FST closure properties, such as concatenation,
union and composition. 

For **insertion**, only one mapping can be supplied at a time because of how the function works. If you think about it,
insertion rules work by turning the empty string into a symbol. But one does not read in the empty string from the input, 
so how can we do this? 

My answer: intersperse the input string with symbols meant to represent the empty string (in this case, "Ø"). 
This lets us operate over the empty string. Because we are modifying the input string, however, it messes up transitions
when multiple mappings are supplied.

## String input

Each function expects symbols to be space delimited. This allows for symbols to have multiple characters:
```
"t h i s i s a s t r i n g"

"[tns=pst] [mod=imp] v e r b [pol=neg] [trns=yes]"
```

## Assimilation

**Assimilation** rules map already existing symbols to new ones. The snippet below shows one mapping and one context:

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

## Insertion


# Installation

Simply fork the repo and clone your copy onto your machine. I am currently using pipenv to manage my environment,
although I may switch to something else later.

The graphing functionality requires [graphviz](https://graphviz.org/) 

# License
[MIT](https://choosealicense.com/licenses/mit/)
