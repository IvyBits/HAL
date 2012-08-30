=================
The HAL AI Engine
=================

HAL is an AI engine which tries to take a different approach than ALICE,
Eliza, and the like, by not only having one engine doing all processing,
but by having three.

It currently has three main engines: regex, matrix (or word index),
and substring. It also has a few supplement engines: spam [1]_, one word
[2]_, and generic.

Note that this is only a library, it doesn't have any fancy interfaces
pre-installed. There are two scripts, ``hal``, which will load command-
line HAL, and ``whal``, which will load a Tkinter-based GUI for it.

.. [1] detects keyboard spam and notify the user instead of giving
       an "I don't understand" response
.. [2] *one*-word variant of matrix, designed to run after matrix.

Installation
============

To install, do: ``pip install HAL``.

After installation, run python in interactive mode and run
``import HAL.dbtest``. If it says you don't have full-text search, then you
should install the ``pysqlite2`` module from `here
<http://code.google.com/p/pysqlite/downloads/list>`_. If you don't, HAL
will still function, albeit much slower.

Note that this is the raw engine, which accepts HAL file extensions to run.
If you do not wish to make your own, you can use the dataset we are developing
that is located here: http://github.com/HALTeam/HALdata.

To start HAL, run ``hal``. This will search for data files in the current
directory. Optionally, you can pass the directory where the dataset is as
an argument to ``hal``.

Note: The dataset is a converted AIML set, that was again converted to the new
HAL engine from a previous one that only had a regex engine. Because of this,
and that the entries were separated by a machine, we expect there to be a lot
of bugs. Please feel free to report them on GitHub.
