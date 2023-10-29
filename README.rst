dobles
=======

**Fork of https://www.github.com/uber/doubles with support for python 3.8+**

.. image:: https://badge.fury.io/py/dobles.svg
    :target: https://badge.fury.io/py/dobles

.. image:: https://readthedocs.org/projects/dobles/badge/?version=latest
    :target: https://dobles.readthedocs.io/en/latest/?badge=latest

.. image:: https://coveralls.io/repos/github/smartfastlabs/dobles/badge.svg?branch=master
    :target: https://coveralls.io/github/smartfastlabs/dobles?branch=master

**dobles** is a Python package that provides test doubles for use in automated tests. 

It provides functionality for stubbing, mocking, and verification of test doubles against the real objects they double.
In contrast to the Mock package, it provides a clear, expressive syntax and better safety guarantees to prevent API
drift and to improve confidence in tests using dobles. It comes with drop-in support for test suites run by Pytest or standard unittest.


Documentation
-------------

Documentation is available at http://dobles.readthedocs.org/en/latest/.

Development
-----------

Source code is available at https://github.com/smartfastlabs/dobles.

To install the dependencies on a fresh clone of the repository, run ``make bootstrap``.

To run the test suite, run ``make test``.

To build the documentation locally, run ``make docs``.

License
-------

MIT: http://opensource.org/licenses/MIT
