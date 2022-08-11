# Packaging tutorials

https://packaging.python.org/en/latest/tutorials/packaging-projects/

https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

https://web.archive.org/web/20201214181824/https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/


# Currently working on:

- tests
- Insertion, deletion rules
- BOW/EOW context handling


# Planned additions:
- Better (less confusing) naming schemes
- When overhauling graphs: default it to hide prefix / extra transitions
- Lock user into using [XXX] tags (may be changed in the future to allow any tags)
- Make custom exceptions
- More tests
- Context / mapping conflict detector

# Planned optimizations:
- Simplify context transition code. There's a lot of repeated and ugly code, so It needs to be organized better.


# Possible additions or random ideas:
- ISL / OSL toggle
- Monoid stuff
- weighted FSTs
- non-deterministic FSTs
- two-way transducers
- get rid of dict, write a filter function for transitions and just use a list of transitions? 

# Known issues:
- When specifying mulitple contexts and/or transductions, it is possible to input contexts and transductions that conflict with each other. I plan to implement a sanity check that tries to locate these issues. 



# Notes:

## Composition notes 
https://stackoverflow.com/questions/2649474/how-to-perform-fst-finite-state-transducer-composition

https://cseweb.ucsd.edu/classes/fa15/cse105-a/Lec/fst.pdf