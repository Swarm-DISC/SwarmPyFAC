""" The swarm_util module provides a host of utilities function.

This module stores a vararity of different functions and constants,
which is deemed general usefull when working on swarm data,
specifically when such data is loaded from 
the viresclient python client.

There is a mix of general constants, such as the permuability of vacum,
and different types of functions.
The functions can generally be categorised into twi types:
Functions for working on arrays of scalars or vectors,
and functions to work with viresclient.
These categories have their own sections, with a short descriptions on each.
    
Array Utilities
---------------
These functions are used to work on numpy arrays of scalars or vectors.
They are mostly geared toward dealign with time-like series.

pack_3d
    Take 3 equaly long arrays of scalars and make an array of 3d vectors.
as_3d
    Like pack_3d, but uses dublicates of the same array of scalars.
    Usefull for aggregating scalar-vector operations over an array.
map_3d
    A map function over arrays of 3d vectors,
    where the function maped takes a 3d vector to a 3d vector.
NEC_to_VSC
    Build a transformation from the NEC frame to the VSC frame.
    The return is a function, which will transfrom
    its input from the NEC frame to the VSC frame.
delta
    Calculate the changes of a time-like series.
means
    Calculate the intermediate value (by linear interpolation)
    for a time-like series.
spherical_delta
    Calculate the changes in spherical coordinates as NEC frame vectors.
curl
    Calculate a single component of curl for an array of vectors.
inclination
    Calculate the inclination for an awway of vectors.
    
Viresclient
-----------
These are the functions related to fetching and loading data
from the viresclient python client.

request_data
    Builds and send a request for a CDF file to vires.
    Most usefull for defaulting all the relevant parameters.
read_cdf
    A function to read a cdf file based on a dictionary pairing
    of attributes you want to read from the cdf file,
    and what you want to refere to them as afterwards.
"""
# """ Utilities for working on swarm data,
# when using the viresclient python client.
# """

__version__ = '0.1.3'
__author__ = 'Ask Neve Gamby'

import datetime as date
import getpass
import numpy as np
import cdflib

from viresclient import SwarmRequest, ClientConfig

# from . import safety as safe_user

MU_0 = 4.0 * np.pi * 10**(-7)
TO_RADIANS = np.pi / 180

    
# def _pack_nd(*scalarss):
    # """ Pack n arrays of scalars into an array of n dimensional vectors.
    # """
    # if len(scalarss) < 1:
        # return None
    # elif len(scalarss) == 1:
        # return np.expand_dims(scalarss[0],1)
    # dimensions = len(scalarss)
    # result = np.zeros((len(scalarss[0]),dimensions))
    # for i, scalars in enumerate(scalarss):
        # result[:,i] = scalars
    # return results

    
def pack_3d(xs, ys, zs):
    """ Pack 3 array-likes into an array of 3d vectors.
    
    Parameters
    ----------
    xs : array-like
        The first (xs) components of the final vector.
        Must be equivalent to an array of scalars,
        generators are not accepted (though ranges are).
        Must have a reasoable response to len(xs),
        which must be the same as len(ys) and len(zs).
    ys : array-like
        The second (ys) components of the final vector.
        Must be equivalent to an array of scalars,
        generators are not accepted.
        Must have a reasoable response to len(ys),
        which must be the same as len(xs) and len(zs).
    zs : array-like
        The third (zs) components of the final vector.
        Must be equivalent to an array of scalars,
        generators are not accepted.
        Must have a reasoable response to len(zs),
        which must be the same as len(ys) and len(xs).
        
    Returns
    -------
    ndarray
        An array of vectors each with 3 dimensions,
        and the same length as xs.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> pack_3d(range(5),np.arange(5)*2-3,[np.cos(xs*np.pi) for xs in range(5)])
    array([[ 0., -3.,  1.],
           [ 1., -1., -1.],
           [ 2.,  1.,  1.],
           [ 3.,  3., -1.],
           [ 4.,  5.,  1.]])
    """
    # return _pack_nd(xs,ys,zs)
    result = np.zeros((len(xs), 3))
    # if (len(xs) != len(ys) or len(xs) != len(zs)):
        # raise ValueError('lengths not equal, with: '
                         # + '!='.join(map(lambda i: str(len(i)),[xs,ys,zs])))
    result[:, 0] = xs
    result[:, 1] = ys
    result[:, 2] = zs
    return result
    
    
# def _as_nd(scalars, n=3):
    # """ Copies an array of scalars so it becomes an array of vectors.
    # """
    # return pack_3d(*[scalars]*n)


def as_3d(scalars):
    """ As pack_3d, but with the same scalars in on all components.
    
    Parameters
    ----------
    scalars : array-like
        An array-like of scalars.
        
    Returns
    -------
    ndarray
        An array of 3 dimensional vectors with the same length as xs.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> vec = np.arange(15).reshape(5,3)
    >>> as_3d(range(5)) * vec
    array([[ 0.,  0.,  0.],
           [ 3.,  4.,  5.],
           [12., 14., 16.],
           [27., 30., 33.],
           [48., 52., 56.]])
    """
    # return _as_nd(xs)
    # """ As pack_3d, but with the same vector in on all components.
    # Use this form array operations where one part has a scalars (this),
    # and another 3d vectors.
    # """
    return pack_3d(scalars, scalars, scalars)

    
# # currently unused, alternative to NEC_to_VSC,
# # in consideration as replacement
# class _NEC_to_VSC2:
    
    # def __init__(self, velocities=None,angles=None,sines_cosines = None):
        # # self.ready = False
        # if sines_cosines is not None:
            # self.sines, self.cosines = sines_cosines
            # # self.ready = True
        # elif angles is not None:
            # self.from_angles(angles)
        # elif velocities is not None
            # self.from_velocities(velocities)
        # else:
            # raise ValueError("At least one parameter must be not None")
        
    # def from_angles(self,angles):
        # self.sines = np.sin(angles)
        # self.cosines = np.cos(angles)
        # # self.ready = True
        
    # def from_velocities(self, velocities):
        # self.from_angles(-np.arctan2(velocities[:, 0] - velocities[:, 1],
                                     # velocities[:, 0] + velocities[:, 1]))
                                     
    # def __call__(self,vectors):
        # return pack_3d(self.cosines*vectors[:, 0] + self.sines*vectors[:, 1],
                       # - self.sines*vectors[:, 0] + self.cosines*vectors[:, 1],
                       # vectors[:, 2])
                       
    # def inverse(self):
        # self.sines = -self.sines
        # # return pack_3d(self.cosines*vectors[:, 0] - self.sines*vectors[:, 1],
                       # # self.sines*vectors[:, 0] + self.cosines*vectors[:, 1],
                       # # vectors[:, 2])
    

def map_3d(function,vectors):
    """ map_3d maps a function for 1d data to each dimension in 3d data.
    
    Parameters
    ----------
    function : ndarray -> ndarray
        A function that takes a scalar array
        and maps it to another scalar array.
    vectors : ndarray
        An array of 3 dimensional vectors.
        
    Returns
    -------
    ndarray
        An array of 3 dimensional vectors.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> vec = np.arange(15).reshape(5,3)
    >>> map_3d(lambda xs: [x > 2 and x%4 != 0 for x in xs],vec)
    array([[0., 0., 0.],
           [1., 0., 1.],
           [1., 1., 0.],
           [1., 1., 1.],
           [0., 1., 1.]])
    """
    return pack_3d(*[function(vectors[:,i]) for i in range(3)])

def NEC_to_VSC(velocities):
    """ Construct a function to transform from the NEC frame to the VSC frame.
    
    This function generates another function,
    which is a transform of vectors from the NEC frame to the VSC frame.
    This specific transformation may be different for each data point.
    
    Parameters
    ----------
    velocities : ndarray
        The velocities describe thw forward direction in the VSC frame,
        and they can be different for each data point.
    
    Returns
    -------
    function
        A function that takes a list of vectors
        of the same length as velocities and
        transform them from the NEC frame to the VSC frame.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> v = np.arange(15).reshape(5,3)
    >>> trans = NEC_to_VSC(v)
    >>> trans(v) # doctest: +ELLIPSIS
    array([[ 0.7...,  0.7...,  2. ...],
           [ 3.5...,  3.5...,  5. ...],
           [ 6.5...,  6.5...,  8. ...],
           [ 9.5...,  9.5..., 11. ...],
           [12.5..., 12.5..., 14. ...]])
    >>> trans((v[::-1]-2.5) * (v + 3)) # doctest: +ELLIPSIS
    array([[ 49.8...,   9.5...,  57.5...],
           [ 46.0...,  46.4...,  68. ...],
           [ 34.8...,  42.4...,  60.5...],
           [  7.0...,  19.1...,  35. ...],
           [-38.4..., -22.4...,  -8.5...]])
    """
    # """ Build a transform going from the NEC frame to the VEC frame.
    # This is done based on the velocities at each point, so the
    # transformation will act differently on each point.
    # Returns the actual transformation function,
    # which can then be applied to compariable series.
    # """
    angles = -np.arctan2(velocities[:, 0] - velocities[:, 1],
                         velocities[:, 0] + velocities[:, 1])
    sines = np.sin(angles)
    cosines = np.cos(angles)

    def transform(vectors):
        """ Transforms from the NEC frame to the VSC frame
        
        This function takes an array of vectors,
        which is in the NEC frame and returns them transformed
        into the VSC frame.
        The transform will may be different for each vector,
        and is fixed when this function is constructed.
        
        Parameters
        ----------
        vectors : ndarray
            An array of 3d points or vectors in the NEC frame.
            
        Returns
        -------
        ndarray
            An array of the vectors in the VSC frame.
            
        Note
        ----
        See NEC_to_VSC for examples of use.
        """
        # """ Transforms from the NEC frame to the VEC frame.
        # Note that the frames have alligned origos,
        # so vectors and points transform the same way.
        # """
        return pack_3d(cosines*vectors[:, 0] + sines*vectors[:, 1],
                       - sines*vectors[:, 0] + cosines*vectors[:, 1],
                       vectors[:, 2])  # Does the 3rd dimension flip?
    return transform


def delta(vectors):
    """ Computes the finite difference on an arralike.

    Parameters
    ----------
    vectors : ndarray
        An array of vectors or scalars.
        
    Returns
    -------
    ndarray
        An array of vectors or scalars of shape (n-1,...),
        when vectors input have shape (n,...).
    
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> delta(np.arange(5))
    array([1, 1, 1, 1])
    >>> delta(np.array([4, 3, 7, 4, 2, 92]))
    array([-1,  4, -3, -2, 90])
    >>> delta(np.array([[1, 0, 0], [0, 1, 3], [7, -13, 4]]))
    array([[ -1,   1,   3],
           [  7, -14,   1]])
    """
    assert len(vectors) >= 2
    return vectors[1:] - vectors[:-1]


def means(vectors):
    """ Computes the means between this and the next point.

    Parameters
    ----------
    vectors : ndarray
        An array of vectors or scalars.
        
    Returns
    -------
    ndarray
        An array of vectors or scalars of shape (n-1,...),
        when vectors input have shape (n,...).
    
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> means(np.array(list(range(5))))
    array([0.5, 1.5, 2.5, 3.5])
    >>> means(np.array([4, 3, 7, 4, 2, 92]))
    array([ 3.5,  5. ,  5.5,  3. , 47. ])
    >>> means(np.array([[1, 0, 0], [0, 1, 3], [7, -13, 4]]))
    array([[ 0.5,  0.5,  1.5],
           [ 3.5, -6. ,  3.5]])
    """
    assert len(vectors) >= 2
    return (vectors[1:] + vectors[:-1]) * 0.5


def spherical_delta(positions):
    """ Computes the change of sherical positions as a NEC vector.
    
    Parameters
    ----------
    positions : ndarray
        An array of positions (3d vectors) described in spherical coordinates.
        
    Returns
    -------
    ndarray : ndarray
        An array of vectors in the NEC frame.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> vecs = np.arange(15).reshape(5,3)
    >>> spherical_delta(vecs)
    array([[ 0.18317585,  0.18311308, -3.        ],
           [ 0.34018372,  0.33913504, -3.        ],
           [ 0.49719158,  0.49293804, -3.        ],
           [ 0.65419945,  0.64324482, -3.        ]])
    """
    theta, Lambda, r = (positions[:, i] for i in range(3))
    r_means = means(r)
    return pack_3d(r_means * np.sin(TO_RADIANS * delta(theta)),
                   r_means * np.sin(TO_RADIANS * delta(Lambda))
                           * np.cos(TO_RADIANS * means(theta)),
                   -delta(r))

  
                   
def curl(delta_x, delta_field, target_index=2):
         # delta_left=None, delta_right=None, target_index=2):
    """ Compute a single component of curl for an array of vectors.
    
    This function is used to calculate a finite difference apporximation
    of curl. Its starting point is similar to a finite difference 
    approximation of a partial derivative, where you use both the 
    recoded change in the function and what you differentiate with respect to.
    In practice this calculate an array of in independent curl operations,
    as given by a single step.
    
    Parameters
    ----------
    delta_x : ndarray
        An array of the finite difference in the considered step.
    delta_field : ndarray
        An array of the finite difference of the field under
        the relevant considered step.
    target_index : int, optional
        The index of the dimension of the curl that should be given as output.
        
    Returns
    -------
    ndarray
        An array of the curl-like quantity,
        but only target_index dimension of it.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> vecs = delta(np.arange(15).reshape(5,3))
    >>> curl(vecs,vecs)
    array([0., 0., 0., 0.])
    >>> curl(pack_3d(np.ones((4,)),-1.5 * np.ones((4,)),np.zeros((4,))),vecs)
    array([5., 5., 5., 5.])
    """
    assert target_index // 3 == 0
    index_x = (target_index+1) % 3
    index_y = (target_index+2) % 3
    # if delta_left is None:
        # if left is None:
            # raise ValueError("Either left or delta_left must be specified.")
        # delta_left = delta(left)
    # if delta_right is None:
        # if right is None:
            # raise ValueError("Either right or delta_right must be specified.")
        # delta_right = delta(right)
    return (delta_field[:, index_y] / delta_x[:, index_x]
            - delta_field[:, index_x] / delta_x[:, index_y])


def inclination(vectors):
    """ Calculates the inclination of vectors.
    
    Calculate the inclination for each individual vector in vectors.
    This means this is equivalent to the tilt of the vectors toward
    the third dimention.
    
    Parameters
    ----------
    vectors : ndarray
        An array of 3d vectors.
        
    Returns
    -------
    ndarray
        An array of scalars, where each is the inclination
        of their respective vector in vectors.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> inclination(np.arange(15).reshape(5,3))
    array([1.10714872, 0.78539816, 0.71469295, 0.68539502, 0.66942998])
    >>> np.sin(_)
    array([0.89442719, 0.70710678, 0.65538554, 0.63297887, 0.62053909])
    """
    length_first_second_dims = (vectors[:, 0]**2 + vectors[:, 1]**2)**0.5
    return np.arctan2(vectors[:, 2], length_first_second_dims)


# def request_data_old(start=date.datetime(2016, 1, 1),
                 # end=date.datetime(2016, 1, 2),
                 # user_file='safe_xml.txt',
                 # credentials = None,
                 # password = None,
                 # target_file='tempdata.cdf',
                 # filters=[{'parameter': 'Latitude',
                           # 'minimum': -90.,
                           # 'maximum': 90.}],
                 # target_url='https://staging.viresdisc.vires.services/openows',
                 # collection='SW_OPER_MAGA_LR_1B',
                 # product_options={'auxiliaries': ['QDLat', 'QDLon']},
                 # sampling_step='PT1S',
                 # models=['MCO_SHA_2C', 'MLI_SHA_2C',
                         # 'MMA_SHA_2C-Primary', 'MMA_SHA_2C-Secondary'],
                 # measurements=['F', 'B_NEC']):
    # """ Request data from a vires server.
    
    # This function sets up a request to a vires server.
    # It is a wrapper on viresclient functionality,
    # where default arguments have been provided.
    
    # The data will be saved to as a cdf file.
    
    # Parameters
    # ----------
    # start : datatime, optional
        # The inclusive starting time of the requested data.
        # Defaults to 1st of Janurary 2016
    # end : datetime, optional
        # The exclusive end time of the requested data.
        # Defaults to 2nd of Janurary 2016
    # user_file : str, optional
        # Filepath to the safe_user encrypted file with login credentials.
        # If set to None you will be prompted for login credentials in runtime.
        # Defaults to 'safe_xml.txt'
    # password : str, optional
        # The password needed to decrypt user_file.
        # If not provided/set to None you will be prompted for it in runtime.
    # target_file : str, optional
        # Filepath for the output cdf file. Must include name and extension.
        # Defaults to 'tempdata.cdf'
    # filters : list(dict), optional
        # A list of dictionaries, where each dictionary is the options
        # for a filter to be applied to the data.
    # target_url : str, optional
        # The full url for the server to request the data at.
        # Defaults to 'https://staging.viresdisc.vires.services/openows'
    # collection : str, optional
        # See viresclient set_collection. Defaults to 'SW_OPER_MAGA_LR_1B'.
    # product_options : dict, optional
        # Extra options to viresclient set_products.
        # Defaults to {'auxiliaries': ['QDLat', 'QDLon']}
    # sampling_step : str, optional
        # Describes the sampling frequency, 
        # since vires may otherwise downsample the data.
        # The default is 1Hz by 'PT1S'.
    # models : list(str), optional
        # The models calculated at the data points.
        # See viresclient set_products models for details.
        # Defaults to [
        # 'MCO_SHA_2C', 'MLI_SHA_2C',
        # 'MMA_SHA_2C-Primary', 'MMA_SHA_2C-Secondary']
    # measurements : list(str), optional
        # Measured quantities to be included for each data point.
        # Defaults to ['F', 'B_NEC']
    
    # Examples
    # --------
    # >>> from pyfac.utils import *  # doctest: +SKIP
    # >>> request_data_old() # doctest: +SKIP
    # >>> request_data_old(date.datetime(2017, 7, 5),
    # ...              date.datetime(2017, 7, 6))# doctest: +SKIP
                     
    # Note
    # ----
    # These examples are skiped by doctest due to security reasons,
    # and unintentional side-effects.
    
    # Warning
    # -------
    # This is the older version of request_data used for 
    # """
    # if credentials is None:
        # if user_file is not None:
            # credentials = safe_user.fetch_login('safe_xml.txt')
        # else:
            # (username, password) = safe_user.prompt_login_data()
            # credentials = {'username':username,'password':password}
    # request = SwarmRequest(url=target_url, **credentials)
                           # # **safe_user.fetch_login('safe_xml.txt'))
    # request.set_collection(collection)
    # request.set_products(measurements=measurements, models=models,
                         # sampling_step=sampling_step, **product_options)
    # for filter in filters:
        # request.set_range_filter(**filter)
    # data = request.get_between(start_time=start, end_time=end)
    # data.to_file(target_file)
    # # return data


def build_credentials(
        url=None,
        token=None,
        username=None,
        password=None):
    """ Generate a valid set of url and token or username/password combination
    """
    config = ClientConfig()
    if url is None:
        url = config.default_url
    site_config = config.get_site_config(url)
    if any([token, username, password]):
        # If any of these are set/true, user-input will be used
        if token:
            credentials = {'token':token}
            credentials['token'] = token
        else:
            if not username:
                if 'username' in site_config:
                    username = site_config['username']
                else:
                    username = input('Enter username: ')
            if not password:
                if 'password' in site_config and username == site_config['username']:
                    password = site_config['password']
                else:
                    password = getpass.getpass('Enter password: ')
            credentials = {'username':username, 'password':password}
    else:
        credentials = site_config
    return url, credentials


def request_data(
        start=date.datetime(2016, 1, 1),
        end=date.datetime(2016, 1, 2),
        token=None,
        username=None,
        password=None,
        target_file='tempdata.cdf',
        filters=[{'parameter': 'Latitude',
                  'minimum': -90.,
                  'maximum': 90.}],
        url='https://vires.services/ows',
        collection='SW_OPER_MAGA_LR_1B',
        product_options={'auxiliaries': ['QDLat', 'QDLon']},
        sampling_step='PT1S',
        models=['MCO_SHA_2C', 'MLI_SHA_2C',
                'MMA_SHA_2C-Primary', 'MMA_SHA_2C-Secondary'],
        measurements=['F', 'B_NEC']):
    """ Request data from a vires server.
    
    This function sets up a request to a vires server.
    It is a wrapper on viresclient functionality,
    where default arguments have been provided.
    
    The data will be saved to as a cdf file.
    
    Parameters
    ----------
    start : datatime, optional
        The inclusive starting time of the requested data.
        Defaults to 1st of Janurary 2016
    end : datetime, optional
        The exclusive end time of the requested data.
        Defaults to 2nd of Janurary 2016
    token : str, optional
        Token for authenticating with the target_url.
        You need either a token or a username/password combination.
        The default options for the website will be used if all are set to None.
    username : str, optional
        username for authenticating with the target_url.
        You need either a token or a username/password combination.
        The default options for the website will be used if all are set to None.
    password : str, optional
        username for authenticating with the target_url.
        You need either a token or a username/password combination.
        The default options for the website will be used if all are set to None.
    target_file : str, optional
        Filepath for the output cdf file. Must include name and extension.
        Defaults to 'tempdata.cdf'
    filters : list(dict), optional
        A list of dictionaries, where each dictionary is the options
        for a filter to be applied to the data.
    target_url : str, optional
        The full url for the server to request the data at.
        Defaults to 'https://staging.viresdisc.vires.services/openows'
    collection : str, optional
        See viresclient set_collection. Defaults to 'SW_OPER_MAGA_LR_1B'.
    product_options : dict, optional
        Extra options to viresclient set_products.
        Defaults to {'auxiliaries': ['QDLat', 'QDLon']}
    sampling_step : str, optional
        Describes the sampling frequency, 
        since vires may otherwise downsample the data.
        The default is 1Hz by 'PT1S'.
    models : list(str), optional
        The models calculated at the data points.
        See viresclient set_products models for details.
        Defaults to [
        'MCO_SHA_2C', 'MLI_SHA_2C',
        'MMA_SHA_2C-Primary', 'MMA_SHA_2C-Secondary']
    measurements : list(str), optional
        Measured quantities to be included for each data point.
        Defaults to ['F', 'B_NEC']
    
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> request_data() # doctest: +SKIP
    >>> request_data(date.datetime(2017, 7, 5),
    ...              date.datetime(2017, 7, 6))# doctest: +SKIP
                     
    Note
    ----
    These examples are skiped by doctest due to security reasons,
    and unintentional side-effects.
    """
        
    url, credentials = build_credentials(url, token, username, password)
    request = SwarmRequest(url=url, **credentials)
    request.set_collection(collection)
    request.set_products(measurements=measurements, models=models,
                         sampling_step=sampling_step, **product_options)
    for filter in filters:
        request.set_range_filter(**filter)
    data = request.get_between(start_time=start, end_time=end)
    data.to_file(target_file)
    # return data
    



def read_cdf(file, **name_pairings):
    """ Read data from a cdf file.
    
    Read a cdf file and construct a dictionary based on
    name_parings. This may open and read a file as a side-effect.
    
    Parameters
    ----------
    file : str or cdfread
        The file to read the data from. 
        Accepts both a string filepath to the file and an opened cdfread file.
    **name_pairings
        Pairs of names used to link a name in the output with its 
        corrisponding name in the cdf file.
        
    Returns
    -------
    dict
        The keys are the keywords used in name_parings,
        while the values are the variables loaded from
        the cdf file with the name of the corrisponding argument.
        
    Examples
    --------
    We can directly ask for variables:
    
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> read_cdf('tempdata.cdf') # doctest: +SKIP
    {}
    >>> read_cdf('tempdata.cdf', time='Timestamp') # doctest: +SKIP,+ELLIPSIS
    {'time': array([...])}
    
    We can also make use of predefined options:
    
    >>> options = {'time': 'Timestamp', 'B_base': 'B_NEC'}
    >>> read_cdf('tempdata.cdf', **options) # doctest: +SKIP,+ELLIPSIS
    {'time': array([...]), 'B_base': array([[...]])}
    
    Note
    ----
    These examples are skiped by doctest due to dependency 
    on the existance of a 'tempdata.cdf' file.
    """
    if not isinstance(file, cdflib.cdfread.CDF):
        file = cdflib.CDF(file)
    return {name: file.varget(cdf_name)
            for name, cdf_name in name_pairings.items()}


if __name__ == '__main__':
    # Test docstrings
    import doctest
    doctest.testmod()
