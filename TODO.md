# TODO

This file contains personal notes, planned additions, random ideas, etc..

## Currently working on:



## Planned optimizations for next major version:
- I plan to refactor the code base to be more scalable, readable, and modular. This will take place after version 1.0. Changes could include, but not limited to:
    - Restructure how the user's input is handled
    - I want to get rid of the three factory function style (`assimilation`, `insertion`, `deletion`) and just have the user use `transducer`.
        - The reason why there are three functions is that `insertion` modifies the input string by placing null symbols everywhere, making insertion actually possible to do. Because of this input modification, other rewrite rtules (`assimilation` and `deletion` would not work)
    - Remove dictonary for delta and use a custom class with the transitions
    - Greatly improve and simplify transition generation
        - this especially includes prefix transitions
    - Improve how word boundary symbols are handled
- Pynini interaction!!

## Planned additions:

- **Better (less confusing) naming schemes**

- Probablty switch out `Pydot` for either `networkx` or `PyGraphviz` and generate an actual dot file instead of directly converting into a png (Pydot seems to be deprecated, so I might want to switch to a more maintained package)

- simutaneous application, left-to-right, right-to-left


## Possible additions or random ideas: 
- two-way transducers
- get rid of dict structure and use a custom class for delta
- make class for types of rewrite rules?

## Known issues:



