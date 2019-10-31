Overview
========
|docs| |version|

The SwarmPyFAC package is used for calculating Geomagnetic Field-Aligned Currents based on cdf-files possibly downloaded via viresclient.

Geomagnetic Field-Aligned Currents are current systems that connect the magnetosphere to the ionosphere, and one of the fundamental interactions between these two regions. These currents, as their name suggests, flow in a direction aligned with the local magnetic field. Swarm is able to estimate these currents using the horizontal component of the magnetic field information alongside a baseline magnetic field estimation. These can then be used with Ampere’s law to determine the currents that flowing in the field-aligned direction. More detailed information on this formulation can be found in Ritter et. al. (2013).

The SwarmPyFAC package contains 2 modules:

- ``swarmpyfac.fac``, the main module. It contains functions to calculate field aligned currents, and related scientific steps. It is rolled into the main package, so you can call its functionality directly from there.
- ``swarmpyfac.utils``, the utility module. It contains functions for the underlaying mathematics, and should also be usefull for computing other products.

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

Calculating the field aligned currents based on swarm data for some periode:

.. code-block:: python

    >>> import swarmpyfac as fc
    >>> import datetime as date
    >>> start = date.datetime(2016, 1, 1)
    >>> end = date.datetime(2016, 1, 2)
    >>> output, input_data = fc.fac_from_file(start=start, end=end, user_file=None)
    >>> time, position, __, fac, *___ = output
    
The steps in ``fc.fac_from_file`` is broken down into other functions, which one can use and replace for their own needs.

Documentation
-------------
See `swarmpyfac.readthedocs.io <https://swarmpyfac.readthedocs.io>`_.

References
----------
Ritter, P., H. Lühr, and J. Rauberg (2013), Determining field-aligned currents with the Swarm constellation mission, Earth Planets Space, 65(11), 1285-1294. `doi: 10.5047/eps.2013.09.006  <https://doi.org/10.5047/eps.2013.09.006>`_


See also:
Swarm Level 2 product description: `Swarm_L2_FAC_single_product_description <https://earth-planets-space.springeropen.com/articles/10.5047/eps.2013.09.006>`_.

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
    