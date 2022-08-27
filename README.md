# Overview
In its current state, `Deltastar` is a program that compiles rewrite rules into deterministic **finite-state string transducers** (FSTs). 
This type of machine is designed to edit (transduce) a string according to a defined set of mappings.

Linguists value FSTs because of their correspondance with rewrite rules, for which both *phonology* and *morphology* in particular 
have an abundance of. One can encode these linguistic mappings though finite-state string transducers.

# Inspiration

This project is directly inspired by [Pynini](https://pypi.org/project/pynini/), a python wrapper for the C++ library [OpenFST](https://www.openfst.org/twiki/bin/view/FST/WebHome) that hosts a powerful API for constructing FSTs. 
Through projects and personal experimentation, I have grown quite fond of Pynini and it seems (to me at least) that the bounds for 
the types of machines you want to make are endless. 

However, in my opinion, Pynini's API is not straight forward. As a linguist, when I began my Pynini journey, I had no formal language theory background.
Thus, it took a good chunk of time to understand the API and what was happening behind the scenes.

You may say, of course, that one should only use these machines provided they have prior knowledge. I disagree with this notion, for I became infatuated with finite-state technology long before I was exposed to the formalisms. 

This leads me to discuss the reason for Deltastar: I wish to make a fully-fledged FST library with an API that is both approachable and scalable. 

# Current Usage

TBA

# The Great Refactoring

I have learned a lot of things since I began this project, namely what my algorithms are capable of, and more importantly, **not capable of**. In order to sculpt deltastar to meet my vision, I need to refactor the entire code base. 


Like I mentioned before, deltastar in its current state is simply a rewrite rule compiler. However, I wish it to be more than that, which is why I've decided to not publish it to Pypi yet. 


# License
[MIT](https://choosealicense.com/licenses/mit/)
