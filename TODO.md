# Packaging tutorials

https://packaging.python.org/en/latest/tutorials/packaging-projects/

https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

https://web.archive.org/web/20201214181824/https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/


# Currently working on:

- Add more test cases (especially for multi-character symbols)
- Insertion, deletion rules
- BOW/EOW context handling

# Planned additions:
- Better (less confusing) naming schemes
- When overhauling graphs: default it to hide prefix / extra transitions
- Lock user into using [XXX] tags (may be changed in the future to allow any tags)
- Make custom exceptions

# Planned optimizations:
- Simplify context transition code. There's a lot of repeated and ugly code, so It needs to be organized better.


# Possible additions or random ideas:
- ISL / OSL toggle
- Monoid stuff
- weighted FSTs
- non-deterministic FSTs
- two-way transducers

# Known issues:
- I'm not sure about this, but since multiple mappings / contexts can be specified at once, depending on the types of rules input by the user, some conflicts may happen. For example, inputting overlapping contexts may lead to some issues. The multiple mapping stuff is mostly just a temporary substitution for not having FST union or composition. When (or if) those get added, multiple mappings might get yeeted. Not sure ¯\\_(ツ)_/¯



# Notes:

## Composition notes 
https://stackoverflow.com/questions/2649474/how-to-perform-fst-finite-state-transducer-composition

https://cseweb.ucsd.edu/classes/fa15/cse105-a/Lec/fst.pdf