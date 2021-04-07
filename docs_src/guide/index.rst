=================
IntFicPy Guide
=================

Basic Topics
------------

.. toctree::
   :maxdepth: 2

   rooms
   items
   characters

Advanced Topics
-----------------

.. toctree::
   :maxdepth: 2

   ifp_objects

Running the example game
-------------------------

To get a feel for IntFicPy quickly, let's use the example game as a jumping off point.

First, get a copy of IntFicPy.
IntFicPy is currently distributed only in source. Download or clone it from `the IntFicPy GitHub repository <https://github.com/JSMaika/intficpy>`_.

Once you have IntFicPy, find the `testgame.py` module in the `examples` directory, and copy it to a place where you can work with it.

In the Python environment where you're going to work on `testgame.py`, install the IntFicPy module,
and its dependencies. Install intficpy with `pip install ../path/to/intficpy`.

This should be enough for the test game to run.

`python testgame.py`

The game will run in the terminal by default, however, it can be configured to run in a GUI.

At the time of writing (November 2020), there is one official GUI for IntFicPy, built using PyQt5.
It can be found `here <https://github.com/JSMaika/IFP-Qt-GUI>`_.
