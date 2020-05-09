=====
pyc2e
=====

A pure python interface for managing the
`Creatures Evolution Engine (c2e) <https://creatures.wiki/Creatures_Evolution_Engine>`_
with no external dependencies. Based off of
`Chris Double's documentation of the c2e shared memory interface <http://double.nz/creatures/developer/sharedmemory.htm>`_.

**This isn't ready for real-world use yet. It might break your Creatures 3 / DS install.**

See bottom for more details.

License TBD, probably a BSD or LGPL.


---------------------------
How to inject CAOS from CLI
---------------------------

If you're still sure you want to try it, clone the repo and::

    pip install -e .


It supports reading from stdin, ::

    cat filename.cos | pyc2e inject


from files, ::

    pyc2e inject --file filename.cos

and arbitrary strings passed from the command line: ::

    pyc2e inject --caos "outs \"testing\""

On windows, you might need to omit the escapes around the quotes  .

-----------------------------------------
Not ready for use in production, very WIP
-----------------------------------------

At the moment, it only handles running & injecting `CAOS <https://creatures.wiki/CAOS>`_ on Windows.
It's posted early because some developers need it. Much of the implementation may miss edge cases or just be ugly.

Engine, config, and launch management for testing and fuzzing will be added later. Linux support will be
added later as well. Assume just about everything could change.

Assumes Python 3.7+, but it might work on lower versions.