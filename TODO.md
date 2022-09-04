# TODO

This file contains personal notes, planned additions, random ideas, etc..

## Currently working on:

- explain boundary syms

## The Great Refactoring:
I plan to refactor the code base to be more `scalable`, `readable`, and `modular`. Changes include, but not limited to:
- Multiple specification will be changed dramatically when I implement composition 
    - Possible futue behavior: each specification will be turned into its own machine and then composed together
- Restructure how the user's input is handled
- Get rid of the three factory function style 
- Custom data structure for delta
- Greatly improve and simplify transition generation
    - this especially includes prefix transitions
    - **Treat all contexts like dual contexts? This may simplify the code greatly (if its possible)!**
- Improve how word boundary symbols are handled
- Make insertion mappings actually consistently work lol
    - Get rid of the wacky null interspersing I do and have multiple symbols in the output of insertion transduction transitions
- Have user provide a symbol table (similar to pynini)?
- Implement something analagous to sigmaStar
    - A way to specify: "arbitrary combination of symbols". This will let the user check if a substring exists regardless of its position in the string. 
    - This is not as important as the other changes here, but I do think it's crucial to have.

## Planned additions:

- simutaneous application, left-to-right, right-to-left specifications
- Pynini interaction



## Possible additions or random ideas: 

- Implement basic string acceptors?
- Possibly switch out `Pydot` for either `networkx` or `PyGraphviz` (Pydot seems to be deprecated, so I might want to switch to a more maintained package)


## Notes
- Should probably include mathematical formalisms and definitions once the code base is in a better spot (i.e. define a DFST, explain **?** transitions, etc...)

## Known issues:

- Under certain contexts and mappings, prefix transitions may generate incorrect transitions. This mostly involves rarer edge cases, but it does happen. 

