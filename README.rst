=====
pyc2e
=====

.. |PyTest results| image:: https://github.com/pushfoo/pyc2e/actions/workflows/test.yaml/badge.svg
   :target: https://github.com/pushfoo/Fontknife/actions/workflows/test.yaml

.. |GitHub license| image:: https://img.shields.io/github/license/pushfoo/pyc2e.svg?color=brightgreen
   :target: https://github.com/pushfoo/pyc2e/blob/master/LICENSE

.. |PRs Welcome| image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
   :target: https://makeapullrequest.com

|PyTest results| |GitHub license| |PRs Welcome|


A pure Python interface for injecting `CAOS code <https://creatures.wiki/CAOS>`_ & reading output from the
`Creatures Evolution Engine (c2e) <https://creatures.wiki/Creatures_Evolution_Engine>`_.


It works by calling relevant parts of the Win32 API through `Python's built-in ctypes module <https://docs.python.org/3/library/ctypes.html>`_, as described in `Chris Double's documentation
of the c2e shared memory interface <http://double.nz/creatures/developer/sharedmemory.htm>`_.


----------
Installing
----------

The only requirements are:

* Python 3.9+
* A compatible c2e version running in the same permission space as the Python interpreter

.. list-table::
   :header-rows: 1

   * - Install Method
     - Benefits
     - Steps

   * - With `pip`
     - Easiest
     - #. `Create & activate a virtual environment <https://docs.python.org/3/library/venv.html>`_
       #. ``pip install pyc2e``

   * - From source
     - Freshest code
     - #. `Clone this repository <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository>`_
       #. ``cd pyc2e``
       #. `Create & activate a virtual environment <https://docs.python.org/3/library/venv.html>`_
       #. ``pip install -e .``


-------------------
Usage & Limitations
-------------------

*Warning: Running custom CAOS can break your Creatures 3 / DS install.*

Running & injecting `CAOS <https://creatures.wiki/CAOS>`_ on Windows is reasonably complete.

.. list-table::
   :header-rows: 1

   * - CAOS Origin
     - Command Syntax

   * - From files
     - ``pyc2e inject --file filename.cos``

   * - Piping from standard input
     - ``cat filename.cos | pyc2e inject``

   * - Strings passed as arguments*
     - ``pyc2e inject --caos "outs \"testing\""``

*\*On Windows, you might need to omit the escapes around the quotes.*

----------------------
Unimplemented Features
----------------------

Engine, config, and launch management for testing and/or fuzzing may be added later.

Support for the Linux version will likely stay incomplete because the community prefers the Windows version for multiple reasons:

#. The Linux version is difficult to install:

   #. Dwindling support for 32 bit code on maintained amd64 Linux distros
   #. Bit rot is rendering precompiled dependencies unusable
   #. Difficulty finding package downloads of linux packages built in 2000

#. All Windows versions crash much less than the Linux builds
#. Running WINE or a VM does not have prohibitive performance penalty for a game this old
#. There are Windows versions of Docking Station and C3 available from multiple sources:

   .. list-table::
      :header-rows: 1

      * - Source Link
        - Price
        - Creatures 3 Included
        - Win10 Compatibility Patches

      * - `EemFoo archive <https://eem.foo/archive/downloads/d238-dockingstation-195-exe>`_
        - Free
        - No
        - No

      * - `Steam (Creatures: The Albian Years) <https://store.steampowered.com/app/1818340/Creatures_The_Albian_Years>`_
        - $5.99 USD
        - Yes
        - Yes

      * - `GOG (Creatures: The Albian Years) <https://www.gog.com/en/game/creatures_the_albian_years>`_
        - $5.99 USD
        - Yes
        - Yes

