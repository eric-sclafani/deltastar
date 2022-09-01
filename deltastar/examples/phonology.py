import sys
sys.path.append("/home/eric/python/projects/deltastar/deltastar")

from transducers import assimilation, deletion, insertion
from itertools import product


# DISCLAIMER: I am not a phonologist so don't hurt me if some of these rules are wrong xD

#
### INTERVOCALIC VOICING
#
vowels = "a i o u e æ ɛ ə ɔ I ʊ".split()

# create all intervocalic environments
environments = list(product(vowels, "_", vowels))
environments = list(map(lambda x: " ".join(x), environments))

mappings = [
    ("t", "ɾ"),
    ("p", "b"),
    ("k", "g"),
    ("p", "b"),
    ("f", "v"),
    ("s", "z"),
]
intervocalic_voicing = assimilation(mappings, environments)

#
### NASAL PLACE ASSIMILATION
#

environments = ["_ k", "_ g"]
mappings = [("n", "ŋ")]

nasal_place_assim  = assimilation(mappings, environments)


#
### POST NASAL VOICING
#

environments = ["m _", "ŋ _"]
mappings = [
    ("t", "d"),
    ("p", "b"),
    ("k", "g"),
]

post_nasal_vce = assimilation(mappings, environments)