Usage
=====
The main part of interest belongs to the ``swarmpyfac.fac`` module. It is however recommended to import the package itself, as it will also import the modules in a fitting namespace::
    
.. code-block:: python

    >>> import swarmpyfac as fc
    >>> fc  # count as swarmpyfac.fac
    >>> fc.utils  # count as swarmpyfac.utils
    >>> fc.safety  # count as swarmpyfac.safety
    

Calculating the field aligned currents based on swarm data for some periode::

.. code-block:: python

    >>> import swarmpyfac as fc
    >>> import datetime as date
    >>> start = date.datetime(2016, 1, 1)
    >>> end = date.datetime(2016, 1, 2)
    >>> output, input_data = fc.fac_from_file(start=start, end=end, user_file=None)
    >>> time, position, __, fac, *___ = output
    
The steps in ``fc.fac_from_file`` is broken down into other functions, which one can use and replace for their own needs.
    
TODO: include more usage