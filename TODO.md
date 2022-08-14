# TODO

This file contains personal notes, planned additions, random ideas, etc..

## Packaging tutorials

https://packaging.python.org/en/latest/tutorials/packaging-projects/

https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

https://web.archive.org/web/20201214181824/https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/


## Currently working on:

- tests
- Insertion, deletion rules
- BOW/EOW context handling
- update displayparams


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
- Make custom exceptions
- **Context / mapping conflict detector**
- Create a ReadtheDocs and move the docs there
- Add a section to the ReadtheDocs or README for people who wish to contribute
- **Make more intricate unit tests (check each transition to each other?) and add final function test to each transitions unit test**
- Add a debug mode to `.rewrite` that will display each state the user's string transitions to. 
- **Add a function for the user to be able to make their own custom delta instead of using rewrite rule format**
- FST composition



## Possible additions or random ideas:
- ISL / OSL toggle (this would *heavily* affect the prefix transitions)
- Monoid stuff
- weighted FSTs
- non-deterministic FSTs
- two-way transducers
- get rid of dict structure and use a custom class for delta
- make class for types of rewrite rules?
- ACCEPTORS!!!
- detect what type of rule user specified? 
- Currently, the user cannot mix assimilation, insertion, and deletion rules in one FST. This is because of the way insertion is handled and hence, the three factory function are there to prevent this mixing. I want to make this possible, however. I would need to make assimilation and deletion rules effectively "ignore" the null symbol when they come across it in the `.rewrite` method. 

## Known issues:
- When specifying mulitple contexts and/or transductions, it is possible to input contexts and transductions that conflict with each other. I plan to implement a sanity check that tries to locate these issues. 

- W.r.t dual contexts, the prefix transitions will almost always go back to a left context state. However, in order for a prefix transition to go the a right context state, the entire left context would need to be repeated in the user's input. As of now, my code does not account for this, and in my head, this scenerio seems unlikely. But, I need to do more tests with this.



