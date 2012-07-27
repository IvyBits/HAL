=================
The HAL AI Engine
=================

HAL is a matching AI engine that is designed to replace ALICE, Eliza, and
like. It currently has three main backends: regex, matrix (or word index),
and substring. It also has a few supplement backends: spam [1]_, oneword
[2]_, and generic.

Note that this is only a library, it doesn't have any fancy interfaces
pre-installed. There is only one script, ``hal``.

.. [1] detects keyboard spam and notify the user instead of giving
       a "I don't understand" response
.. [2] *one*-word variant of matrix, designed to run after matrix, but in
       practice never used.

Installation
============

To install, do: ``pip install HAL``.

After install, run python in interactive mode and run ``import HAL.dbtest``.
If it says you don't have fts (full-text search), then you should install
the ``pysqlite2`` module from `here
<http://code.google.com/p/pysqlite/downloads/list>`_.

Now you need a dataset, the main set that I am developing is here:
http://github.com/HALTeam/HALdata. Note that it was converted from an older
version that I wrote a few months ago, which has only a regex engine. The
dataset is based on the standard AIML set, which have a very different design
compared to HAL. So I expect many bugs in the dataset, feel free to report
them on GitHub.



