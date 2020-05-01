=====
pyc2e
=====

A pure python interface for managing the
`Creatures Evolution Engine (c2e) <https://creatures.wiki/Creatures_Evolution_Engine>`_
with no external dependencies. Based off of
`Chris Double's documentation of the c2e shared memory interface <http://double.nz/creatures/developer/sharedmemory.htm>`_.

WIP. At the moment, it only handles running & injecting `CAOS script <https://creatures.wiki/CAOS>`_.
Much of the implementation may miss edge cases or just be gross. Posted early because people need it.

Engine, config, and run directory management for launching and fuzzing the c2e instances will be added later.
Assume just about everything could change. Not ready for use in production.

Assumes Python 3.7+, but it might work on lower versions.

License TBD, but you can try it out and run it for now.
