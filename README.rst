Overview
========
|docs| |version|

The SwarmPyFAC package is used for calculating Field Aligned Currents based on cdf-files possibly downloaded via viresclient. It is seperated into 3 modules:

- ``swarmpyfac.fac``, the main module. It contains functions to calculate field aligned currents, and related scientific steps. It is rolled into the main package, so you can call its functionality directly from there.
- ``swarmpyfac.utils``, the utility module. It contains functions for the underlaying mathematics, and should also be usefull for computing other products.
- ``swarmpyfac.safety``, the encryption module. It deals with storing credential information in a safe maner. Warning: This module is likely to be depreciated in the future.

Installation
------------

Using pip::

    pip install swarmpyfac

Dependencies:

- numpy
- cdflib
- viresclient
- matplotlib
- scipy
- pycryptodome

Extra dependencies for handling the source version:

- sphinx
- numpydoc
- hypothesis


Quick Start
-----------
The package handle imports of its own modules, so it is sufficient to import the base package. The different packages can be access from there:

.. code-block:: python

    >>> import swarmpyfac as fc
    >>> fc  # count as swarmpyfac.fac
    >>> fc.utils  # count as swarmpyfac.utils
    >>> fc.safety  # count as swarmpyfac.safety

Calculating the field aligned currents based on swarm data for some periode:

.. code-block:: python

    >>> import swarmpyfac as fc
    >>> import datetime as date
    >>> start = date.datetime(2016, 1, 1)
    >>> end = date.datetime(2016, 1, 2)
    >>> output = fc.fac_from_file(start, end, credentials={})
    >>> time, posision, __, fac, * = output
    
The steps in ``fc.fac_from_file`` is broken down into other functions, which one can use and replace for their own needs.

Documentation
-------------
See `swarmpyfac.readthedocs.io <https://swarmpyfac.readthedocs.io>`_.


Acknowledgments
---------------
The code is produced with support from ESA through the Swarm Data Innovation and Science Cluster (Swarm DISC). For more information on Swarm DISC, please visit https://earth.esa.int/web/guest/missions/esa-eo-missions/swarm/disc

The project is based on the matlab program for caclulating the fac product level 2 product for the swarm mission, which is written by `GFZ <https://www.gfz-potsdam.de/>`_.

Badges
------

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - package
      - | |version|


.. |docs| image:: https://readthedocs.org/projects/pyamps/badge/?version=latest
    :target: http://swarmpyfac.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |version| image:: https://badge.fury.io/py/swarmpyfac.svg
    :alt: PyPI Package latest release
    :target: https://badge.fury.io/py/swarmpyfac
    