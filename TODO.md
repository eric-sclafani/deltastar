# TODO

This file contains personal notes, planned additions, random ideas, etc..

## Packaging tutorials

https://packaging.python.org/en/latest/tutorials/packaging-projects/

https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

https://web.archive.org/web/20201214181824/https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/


## Currently working on:

- tests
- update displayparams
- **Context / mapping conflict detector**


## Planned optimizations:
- I plan to refactor the code base to be more scalable, readable, and modular. This will take place after version 1.0. Changes could include, but not limited to:
    - Restructure how the user's input is handled
        - I want to get rid of the three factory function style (`assimilation`, `insertion`, `deletion`) and just have the user use `transducer`.
    - Remove dictonary for delta and use a custom class with the transitions
    - Greatly improve and simplify transition generation
    

## Planned additions:
**bold** = more important

- **Better (less confusing) naming schemes**
- When overhauling graphs: default it to hide extra transitions
- Lock user into using [XXX] tags (may be changed in the future to allow any tags)
- Create a ReadtheDocs and move the docs there
- Add a section to the ReadtheDocs or README for people who wish to contribute
- Make rewrite unit tests more intricate?
- **Add a function for the user to be able to make their own custom delta instead of using rewrite rule format**
- Remove `State` constructor
- add disclaimers about graphing functionality:
    - "Please note that graphing has only been tested on my Unix systems. I do not know if Windows plays nicely with graphviz (both graphing packages mentioned above use graphviz). I mention this because I've seen some threads that say certain functions in `Pydot` don't work on Windows. If there is an incompatibility, I currently have no plans to try and fix it, for I don't develop on Windows. However, if someone knows how to fix it and wants to open a pull request, you are more than welcome."
- Probablty switch out `Pydot` for either `networkx` or `PyGraphviz`



## Possible additions or random ideas:
- ISL / OSL toggle (this would *heavily* affect the prefix transitions)
- Monoid stuff
- weighted FSTs
- non-deterministic FSTs
- two-way transducers
- get rid of dict structure and use a custom class for delta
- make class for types of rewrite rules?
- ACCEPTORS!!!
- FST composition

## Known issues:
- When specifying mulitple contexts and/or transductions, it is possible to input contexts and transductions that conflict with each other. I plan to implement a sanity check that tries to locate these issues. 



