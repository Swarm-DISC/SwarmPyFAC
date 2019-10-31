Installation
============    

The easiest way to install SwarmPyFAC is using ``pip``::

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


SwarmPyFAC can also be installed directly from the source code. This is especially usefull if one wants to work directly with the source code. The source code can be downloaded from GitHub and set up in a virtual enviroment::

    git clone https://github.com/Swarm-DISC/SwarmPyFAC
    cd SwarmPyFAC
    python3 -m venv penv
    source penv/bin/activate
    pip install -r requirements.txt
    pip install -e .
    
Using this setup changes to the source code will be able to affect code that uses this package, in the same way as if the modules in it was part of your working directory. It should be noted that this only puts your current shell into this virtual enviroment, and you will have to run a similar ``source`` command with equivalent path to activate it in other shells. One can leave a virtual enviroment with a ``deactivate`` command. 
    
    