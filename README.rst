=====
pyc2e
=====

A pure Python interface for injecting `CAOS code <https://creatures.wiki/CAOS>`_ & reading output from the
`Creatures Evolution Engine (c2e) <https://creatures.wiki/Creatures_Evolution_Engine>`_. It works by wrapping parts of the Win32 API with `Python's built-in ctypes module <https://docs.python.org/3/library/ctypes.html>`_.

The only requirements are:

* Python 3.7+
* A compatible c2e version running in the same permission space as the Python interpreter

Created using `Chris Double's documentation of the c2e shared memory interface <http://double.nz/creatures/developer/sharedmemory.htm>`_.

**Warning: Running custom CAOS can break your Creatures 3 / DS install.**

License TBD, probably a BSD or LGPL.

---------------------------
How to inject CAOS from CLI
---------------------------

If you're still sure you want to try it, clone the repo and install via::

    pip install -e .

You can also install through pip, but this isn't guaranteed to be fresh: ::

    pip install pyc2e

pyc2e supports reading from stdin, ::

    cat filename.cos | pyc2e inject


from files, ::

    pyc2e inject --file filename.cos

and arbitrary strings passed from the command line: ::

    pyc2e inject --caos "outs \"testing\""

On windows, you might need to omit the escapes around the quotes.

---------------------
Current functionality
---------------------

At the moment, this project handles running & injecting `CAOS <https://creatures.wiki/CAOS>`_ on Windows.
The Linux implementation is partially complete due to lack of interest from the game's community. Engine, config, and launch management for testing and fuzzing may added later.
