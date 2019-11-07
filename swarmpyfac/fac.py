""" The fac module is used for calculated field alligned currents.

This module contains functions used to calculated field alligned currents,
and some of the components used in the calculations.
This module is dependent on the swarm_util module, which contains
functions for utilities and some of the more general components needed.

This module currently only allows caluculation of the single satelite
version of the FAC product, and it uses data available from viresclient's
python client or another data source with similar format.
The major difference between this and the official ESA product,
is that the input from models are their effects at each measurement point,
since this is the format delivered by viresclient.

This means that there is a small algorithmic difference compared
to what is used in the official ESA products,
though experimental comparison have found the difference 
to be less than  1.2*10^(-4) micro A/m^2, and the average
difference to be less than 1% of this.

Running this module as a script will (outside of running some tests)
perform the default experiment.

Overview
--------
This section lists each of the functions in this module,
and give a short description of them.
You can use this as an easier way to look up what you might need.

split_models
    Takes measurements and up to several models,
    and returns the combined model and the residual on the measurements.
radial_current
    Calculate the radial currents for time-like series.
single_sat_fac
    Calculate the field alligned currents
    for a single satelinte on time-like series.
single_sat_fac_full
    Like single_sat_fac, but it handles input from a dictionary,
    and can figure out which models are pressent itself.
fetch_data
    Fetch the data needed, and can figure out itself whether
    it needs to download it first.
fac_from_file
    Do the entire single satelite field alligned currents calculations,
    but takes a possible file as input the same way as fetch_data.

Examples
--------
>>> from pyfac.fac import fac_from_file  # doctest: +SKIP
>>> import datetime as date
>>> results, input_data = fac_from_file(
...     start=date.datetime(2017, 4, 11),
...     end=date.datetime(2017, 4, 12),
...     force_download=True)  # doctest: +SKIP
>>> lat, fac = results[1][:, 0], results[3]  # doctest: +SKIP
"""
# """ A slim version of the FAC level 2 processing,
# but when using viresclient data instead of official ESA products.
# """

__version__ = '0.5.0'
__author__ = 'Ask Neve Gamby'

import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as sii

# from . import safety as safe_user
from . import utils as sw

_INKL_LIMIT = 30.

base_pairs = {
    'time': 'Timestamp',
    'Theta': 'Latitude', 
    'phi': 'Longitude', 
    'r': 'Radius'
    }

_name_pairings = {
    **base_pairs,
    'B_base': 'B_NEC',
    'B_core': 'B_NEC_MCO_SHA_2C',
    'B_lithosphere': 'B_NEC_MLI_SHA_2C',
    'B_magnetosphere_primary': 'B_NEC_MMA_SHA_2C-Primary',
    'B_magnetosphere_secondary': 'B_NEC_MMA_SHA_2C-Secondary',
    }


def split_models(baseline, *models):
    """ Seperate the effect of models from the baseline.
    
    Seperate the effect of model and risidual on the baseline,
    base on precalculated effects of each model.
    It is assumed that the models combine linearly with each
    other and a residual (meaning modelA + modelB + residual = baseline,
    but not modelA * modelB + residual = baseline or other such variations).
    
    Parameters
    ----------
    baseline : ndarray
        An array of the base measurements.
    *models : ndarray
        Arrays of the effects of each model to be removed.
        all models must have the same length as baseline.
    
    Returns
    -------
    tuple of ndarray
        A tuple, with the first component being an ndarray of the residual
        and the second component being an ndarray of the combined model.
        The result statisfies that the sum of the components
        is equal to the baseline.
        
    Examples
    --------
    >>> from pyfac.fac import *  # doctest: +SKIP
    >>> modelA = np.arange(15).reshape(5,3)**2
    >>> modelB = sw.as_3d(np.arange(7,2,-1))
    >>> data = (np.random.randn(5,3)*0.1 + modelA + modelB 
    ...         + sw.pack_3d(np.sin(np.arange(5)*0.5),
    ...                      np.cos(np.arange(5)*0.5),
    ...                      np.tan(np.arange(5)*0.5)))
    >>> split_models(data,modelA,modelB) # doctest: +ELLIPSIS
    (array([[...,...,...],
           [...,...,...],
           [...,...,...],
           [...,...,...],
           [...,...,...]]), array([[  7.,   8.,  11.],
           [ 15.,  22.,  31.],
           [ 41.,  54.,  69.],
           [ 85., 104., 125.],
           [147., 172., 199.]]))
    """
    model = sum(models)
    return (baseline - model,
            model)


def radial_current(delta_B, velocity, delta_time, MU_0=sw.MU_0):
    """ Calculate the radial curents (IRC) over a time series.
    
    Parameters
    ----------
    delta_B : ndarray
        The change in the B (magnetic) field in a time series in
        an ndarray of vectors.
        Standard use requires this to be in the VSC frame.
    velocity : ndarray
        An ndarray of vectors of the spartial velocities
        at each point in the timeseries.
    delta_time : ndarray
        An ndarray of scalars of the time steps between 
        each point in the timeseries of delta_B and velocity.
    MU_0 : float, optional
        The constant of permubility of vacum, in the given units.
        Defaults to swarm_util.MU_0, which assumes velocity 
        and delta_time are in base SI units, and delta_B in nT.
        
    Returns
    -------
    ndarray
        An ndarray of vectors, each of which describes
        the radial current at the respective point in the timseries.
        
    Examples
    --------
    >>> from pyfac.fac import *  # doctest: +SKIP
    >>> vecs = sw.delta(np.arange(15).reshape(5,3))
    >>> radial_current(vecs,vecs,np.ones(len(vecs)))
    array([-0., -0., -0., -0.])
    >>> radial_current(vecs, sw.pack_3d(np.ones((4,)),-1.5 * np.ones((4,)),np.zeros((4,))),np.ones(len(vecs)))
    array([-1989.43678865, -1989.43678865, -1989.43678865, -1989.43678865])
    """
    change = sw.curl(delta_x=velocity, delta_field=delta_B)
    return ((-.001 / (2*MU_0)) * change / delta_time)


def single_sat_fac(time, positions, B_res, B_model):
    """ Calculate the Field Aligned Currents on a single satelites path.
    
    This function runs through the same logic as needed for the single
    satelite version of the official FAC product.
    This function is not designed to deal with data flaged in some way as bad.
    There are several extra outputs usefull for debuging and comparisons.
    
    Parameters
    ----------
    time : ndarray
        An array of scalars of time stamps in seconds.
    poisitions : ndarray
        An array of vectors (theta, phi,r) of the position of the 
        satelite in spherical coordinates.
    B_res : ndarray
        An array of vectors of the residual of the magnetic field 
        measurements after the model have been substracted.
        The vectors are assumed to be in the NEC coordinate system.
    B_model : ndarray
        An array of vectors of the model of the magnetic field
        at the point of measurements.
        The vectors are assumed to be in the NEC coordinate system.
        
    Returns
    -------
    The return is a tuple consiting of the following:
    time : ndarray
        An ndarray of  scalars describing the time each point
        in the calculations corrisond to.
        Note that it is off compared to the parameter time.
    position : ndarray
        An ndarray of spherical coordinates describing the postion
        of each point in the time series where the calculations
        are suppose to apply at. The coordinates are arranged as
        theta, phi, r.
        Note tht this is off compared to the parameter positions.
    irc : ndarray
        An ndarray of vectors of the radial currents (the radial components,
        of currents) found when solving one of Maxwells equations
        on the magnetic field.
        Note that this is given in the VSC (spacecraft velocity) frame.
    fac : ndarray
        An ndarray of vectors of the field alligned currents.
        Note that this is given in the VSC (spacecraft velocity) frame.
    V : ndarray
        An ndarray of vectors of the velocity in the NEC frame.
    V_VSC : ndarray
        An ndarray of vectors of the velocity in the VSC frame.
    pos_ltl : ndarray
        An ndarray of scalars of positions where local time is acounted for.
        Each position reference the same position as positions output.
        Note tht this is off compared to the parameter positions.
    inclination :
        An ndarray of scalars of the inclination of the aproximation 
        of the magnetic field, where the calculations
        are supposed to be applied at.
        
    Examples
    --------
    >>> from pyfac.fac import *  # doctest: +SKIP
    >>> time = np.arange(0,10,0.1)
    >>> positions = sw.pack_3d(np.sin(0.01 * time)*90,(0.01 * time % np.pi)/sw.TO_RADIANS ,np.ones(len(time)))
    >>> B_res = np.random.randn(len(time),3)* sw.as_3d(10 *positions[:,1])
    >>> B_model = sw.as_3d(positions[:,2])*sw.pack_3d(np.sin(positions[:,0]),np.zeros(len(time)),2*np.cos(positions[:,0]))
    >>> single_sat_fac(time,positions,B_res,B_model)  # doctest: +ELLIPSIS
    (array([...]), array([[...]]), array([...]), array([...]), array([[...]]), array([[...]]), array([[...]]), array([...]))
    """
    dt = sw.delta(time)
    pos_ltl = sw.pack_3d(positions[:,0],
                         ((positions[:,1] + 180 + time/86400 * 360)%360)-180,
                         positions[:,2])
    V = sw.spherical_delta(pos_ltl)/sw.as_3d(dt)
    transform = sw.NEC_to_VSC(V)
    V_VSC = transform(V)  # V is in VSC frame now
    B1 = transform(B_res[:-1])
    B2 = transform(B_res[1:])
    #transform(sw.delta(B_res)
    irc = radial_current(B2-B1, V_VSC, dt)
    target_time = sw.means(time)
    B_interpolated = sw.map_3d(lambda data: 
        sii.splev(target_time,sii.splrep(time,data)),
        B_model)
    inclination = sw.inclination(B_interpolated) #we approximate local field by interpolation
    fac = -irc / np.sin(inclination)
    fac[abs(inclination) < _INKL_LIMIT * sw.TO_RADIANS] = np.nan
    is_good = dt <= 1
    return (sw.means(time)[is_good],
            sw.means(positions)[is_good],
            irc[is_good],
            fac[is_good],
            V[is_good],
            V_VSC[is_good],
            sw.means(pos_ltl)[is_good],
            inclination[is_good])


def single_sat_fac_full(input_data):
    """ Calculate the Field Aligned Currents on a single satelites path.
    
    This is mainly designed as a wrapper for single_sat_fac,
    which can extract the relevant parameters from a dictionary
    
    This function runs through the same logic as needed for the single
    satelite version of the official FAC product.
    This function is not designed to deal with data flaged in some way as bad.
    There are several extra outputs usefull for debuging and comparisons.
    
    Parameters
    ----------
    There is only one parameter: input_data, which is a dictionary.
    This dictionary functions effectively as a superset of
    the relevant parameters.  The relevant parameters are given below:
    time : ndarray
        An array of scalars of time stamps in seconds.
    Theta : ndarray
        An array of scalars representing the polar angle component
        of the satelite in spherical coordinates.
    phi : ndarray
        An array of scalars representing the azimuth angle component
        of the satelite in spherical coordinates.
    r : ndarray
        An array of scalars representing the radial angle component
        of the satelite in spherical coordinates.
    B_base : ndarray
        An array of vectors of the magnetic field measurements.
        The vectors are assumed to be in the NEC coordinate system.
    B_core : ndarray, optional
        An array of vectors of the magnetic field component
        derived from a model of Earth's core.
    B_lithosphere : ndarray, optional
        An array of vectors of the magnetic field component
        derived from a model of the Earthø's lithosphere (crust).
    B_magnetosphere_primary : ndarray, optional
        An array of vectors of the magnetic field component
        derived from a model of the primary magnetosphere field.
    B_magnetosphere_secondary : ndarray, optional
        An array of vectors of the magnetic field component
        derived from a model of the induced field from the magnetosphere.
        
    Returns
    -------
    The return is a tuple consiting of the following:
    time : ndarray
        An ndarray of  scalars describing the time each point
        in the calculations corrisond to.
        Note that it is off compared to the parameter time.
    position : ndarray
        An ndarray of spherical coordinates describing the postion
        of each point in the time series where the calculations
        are suppose to apply at. The coordinates are arranged as
        theta, phi, r.
        Note tht this is off compared to the parameter positions.
    irc : ndarray
        An ndarray of vectors of the radial currents (the radial components,
        of currents) found when solving one of Maxwells equations
        on the magnetic field.
        Note that this is given in the VSC (spacecraft velocity) frame.
    fac : ndarray
        An ndarray of vectors of the field alligned currents.
        Note that this is given in the VSC (spacecraft velocity) frame.
    V : ndarray
        An ndarray of vectors of the velocity in the NEC frame.
    V_VSC : ndarray
        An ndarray of vectors of the velocity in the VSC frame.
    pos_ltl : ndarray
        An ndarray of scalars of positions where local time is acounted for.
        Each position reference the same position as positions output.
        Note tht this is off compared to the parameter positions.
    inclination :
        An ndarray of scalars of the inclination of the aproximation 
        of the magnetic field, where the calculations
        are supposed to be applied at.
        
    Examples
    --------
    >>> from pyfac.fac import *  # doctest: +SKIP
    >>> time = np.arange(0,10,0.1)
    >>> positions = sw.pack_3d(np.sin(0.01 * time)*90,(0.01 * time % np.pi)/sw.TO_RADIANS ,np.ones(len(time)))
    >>> B_res = np.random.randn(len(time),3)* sw.as_3d(10 *positions[:,1])
    >>> B_core = sw.as_3d(positions[:,2])*sw.pack_3d(np.sin(positions[:,0]),np.zeros(len(time)),2*np.cos(positions[:,0]))
    >>> single_sat_fac_full({'time':time,'Theta':positions[:,0],'phi':positions[:,1],'r':positions[:,2],'B_base':B_res+B_core,'B_core':B_core})  # doctest: +ELLIPSIS
    (array([...]), array([[...]]), array([...]), array([...]), array([[...]]), array([[...]]), array([[...]]), array([...]))
    """
    return single_sat_fac(
        input_data['time'],
        sw.pack_3d(input_data['Theta'], input_data['phi'], input_data['r']),
        *split_models(input_data['B_base'], *[input_data[key] for key in [
            'B_core', 'B_lithosphere',
            'B_magnetosphere_primary',
            'B_magnetosphere_secondary'] if key in input_data]))


def fetch_data(force_download=False, temp_file='tempdata.cdf',**options):
    """ Fetch cdf form data from a file or by downloading it.
    
    This function is made to hide the complexity of getting
    data from a cdf file that you might need to download first.
    The idea is a dowloaded file will be saved as some temporary file
    temp_file and then opened.
    If the file have already been downloaded then it will be assumed
    that the file at temp_file is the one wanted, unless
    force_download is set to true to indicate that this cache
    should be flushed and overwritten by a new download.
    
    Parameters
    ----------
    force_download : boolean, optional
        A flag on whether to force downloading of the data and
        thereby overwrite the temp_file if it already exists.
        If set to False the program will only download the data
        if it cannot find the temp_file.
        Default is False.
    temp_file : string
        A string of the file path for where the downloaded file should be.
        If the file already exists then this may take priority
        depending on the force_download flag.
        
    Returns
    -------
    dict
        A dictionary map of _name_pairings, where the values
        have been replaced with the data entry of
        the previous value.
    
    Examples
    --------
    >>> from pyfac.fac import *  # doctest: +SKIP
    >>> fetch_data()  # doctest: +ELLIPSIS, +SKIP
    {...}
    """
    name_pairings = options.pop('name_pairings',_name_pairings)
    if temp_file is None or not os.path.isfile(temp_file) or force_download:
        sw.request_data(**options, target_file=temp_file)
    return sw.read_cdf(temp_file, **name_pairings)


def fac_from_file(**options):
    """ Compute FAC for a single satelite from data in an outside source.
    
    This function is inteded as the topmost function of this module.
    It is therefore suggested to just strait up use this function,
    when one wants to use this as a module instead of as a script.
    
    The function will read a cdf-file or download it,
    if such a file is not already cached.
    It will then calculate FAC (field aligned currents),
    and other related measures, and return those results.
    
    Parameters
    ----------
    **options
        options to be passed to other lower level function(s),
        mainly fetch_data.
        
    Returns
    -------
    The return is a tuple consiting of the following:
    time : ndarray
        An ndarray of  scalars describing the time each point
        in the calculations corrisond to.
        Note that it is off compared to the parameter time.
    position : ndarray
        An ndarray of spherical coordinates describing the postion
        of each point in the time series where the calculations
        are suppose to apply at. The coordinates are arranged as
        theta, phi, r.
        Note tht this is off compared to the parameter positions.
    irc : ndarray
        An ndarray of vectors of the radial currents (the radial components,
        of currents) found when solving one of Maxwells equations
        on the magnetic field.
        Note that this is given in the VSC (spacecraft velocity) frame.
    fac : ndarray
        An ndarray of vectors of the field alligned currents.
        Note that this is given in the VSC (spacecraft velocity) frame.
    V : ndarray
        An ndarray of vectors of the velocity in the NEC frame.
    V_VSC : ndarray
        An ndarray of vectors of the velocity in the VSC frame.
    pos_ltl : ndarray
        An ndarray of scalars of positions where local time is acounted for.
        Each position reference the same position as positions output.
        Note tht this is off compared to the parameter positions.
    inclination :
        An ndarray of scalars of the inclination of the aproximation 
        of the magnetic field, where the calculations
        are supposed to be applied at.
            
    Examples
    --------
    >>> from pyfac.fac import *  # doctest: +SKIP
    >>> fac_from_file()  # doctest: +ELLIPSIS, +SKIP
    (array([...]), array([[...]]), array([...]), array([...]), array([[...]]), array([[...]]), array([[...]]), array([...]))
    """
    input_data = fetch_data(**options, use_pop=False)
    input_data['time'] *= 0.001  # conversion to seconds
    return (single_sat_fac_full(input_data),
            input_data)


if __name__ == '__main__':
    # Test docstrings
    import doctest
    doctest.testmod()

    results, input_data = fac_from_file()
    lat, fac = results[1][:, 0], results[3]
    reference = sw.read_cdf(
        'otherData/SW_OPER_FACATMS_2F_20160101T000000_20160101T235959_0301.cdf',
        lat='Latitude',
        fac='FAC')
    plt.plot(reference['lat'], reference['FAC'], 'b')
    plt.plot(lat, fac, 'r:')
    # plt.show()
