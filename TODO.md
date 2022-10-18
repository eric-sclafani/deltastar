# TODO

This file contains personal notes, planned additions, random ideas, etc..

## Currently working on:

- re-implement prefix transitions
- get rid of Rule class (no need for it)

## The Great Refactoring:
I plan to refactor the code base to be more `scalable`, `readable`, and `modular`. Changes include, but not limited to:
- Multiple specification will be changed dramatically when I implement composition 
    - Possible futue behavior: each specification will be turned into its own machine and then composed together
- Restructure how the user's input is handled
- Get rid of the three factory function style 
- Custom data structure for delta
- Greatly improve and simplify transition generation
    - this especially includes prefix transitions
    - **Treat all contexts like dual contexts? This may simplify the code greatly!**
- Improve how word boundary symbols are handled
- Make insertion mappings actually consistently work lol
    - Get rid of the wacky null interspersing I do and have multiple symbols in the output of insertion transduction transitions
- Have user provide a symbol table (similar to pynini)?
- Implement something analagous to sigmaStar
    - A way to specify: "arbitrary combination of symbols". This will let the user check if a substring exists regardless of its position in the string. 
    - I'm thinking I can do this by reserving asterick `*` to mean "any combination of symbols"

## Planned additions:

- simutaneous application, left-to-right, right-to-left specifications
- Pynini interaction
- rename displayparams to .summary()
- add debug mode to graphing, will add exra lambdas to indicate symbols not output
- https://code-maven.com/interactive-shell-with-cmd-in-python
- https://towardsdatascience.com/write-clean-python-code-using-pipes-1239a0f3abf5



## Possible additions or random ideas: 

- Implement basic string acceptors?
- subsequence transducer: "s -> sh / _ .. sh"? (use a stack or queue?)


## Notes
- Should probably include mathematical formalisms and definitions once the code base is in a better spot (i.e. define a DFST, explain **?** transitions, etc...)
https://stackoverflow.com/questions/6392739/what-does-the-at-symbol-do-in-python/28997112#28997112

## Known issues:

- 

