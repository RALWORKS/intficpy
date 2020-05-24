# Getting Started
---

To get started with IntFicPy, you will first need to obtain and install the Python
module.

For prospective IntFicPy game developers, downloading the latest release is
reccommended. Releases can be downloaded from GitHub at
https://github.com/JSMaika/intficpy/releases

Alternately, you can clone the IntFicPy repo to work with the latest code. However,
master branch is not guaranteed to be stable at any given time.

Once you have pulled or downloaded the code, and unizpped the file if needed, create
a Python virtual environment for your IntFicPy project, and install InfFicPy's
requirements.

```
$ cd intficpy
$ pipenv shell
$ pipenv install
```

Then, install IntFicPy.

```
$ pip install -e .
```

You should now be able to run the example game.
```
$ python examples/testgame.py
```

You can also run the tests.
```
$ python -m unittest discover
```
