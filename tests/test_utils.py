
import pytest
import numpy as np
import swarmpyfac.utils as utils
from unittest.mock import patch
import viresclient
import os


def test_pack_3d_examples():
    result = utils.pack_3d(range(5), np.arange(5)*2-3,[np.cos(xs*np.pi) for xs in range(5)])
    expected = np.array([
        [ 0., -3.,  1.],
        [ 1., -1., -1.],
        [ 2.,  1.,  1.],
        [ 3.,  3., -1.],
        [ 4.,  5.,  1.]])
    assert (result == expected).all()

def test_as_3d_examples():
    vec = np.arange(15).reshape(5,3)
    result = utils.as_3d(range(5)) * vec
    expected = np.array([
        [ 0.,  0.,  0.],
        [ 3.,  4.,  5.],
        [12., 14., 16.],
        [27., 30., 33.],
        [48., 52., 56.]])
    assert (result == expected).all()
    
def test_map_3d_examples():
    vec = np.arange(15).reshape(5,3)
    result = utils.map_3d(lambda xs: [x > 2 and x%4 != 0 for x in xs],vec)
    expected = np.array([
        [0., 0., 0.],
        [1., 0., 1.],
        [1., 1., 0.],
        [1., 1., 1.],
        [0., 1., 1.]])
    assert (result == expected).all()
    
def test_NEC_to_VSC_examples():
    v = np.arange(15).reshape(5,3)
    trans = utils.NEC_to_VSC(v)
    result = trans(v)
    expected = np.array([
        [ 0.7,  0.7,  2. ],
        [ 3.5,  3.5,  5. ],
        [ 6.5,  6.5,  8. ],
        [ 9.5,  9.5, 11. ],
        [12.5, 12.5, 14. ]])
    assert (np.abs(result-expected)<0.1).all()
    result2 = trans((v[::-1]-2.5) * (v + 3))
    expected2 = np.array([
        [ 49.8,   9.5,  57.5],
        [ 46.0,  46.4,  68. ],
        [ 34.8,  42.4,  60.5],
        [  7.0,  19.1,  35. ],
        [-38.4, -22.4,  -8.5]])
    assert (np.abs(result2-expected2)<0.1).all()
    
def test_delta_examples():
    result = utils.delta(np.arange(5))
    expected = np.array([1,1,1,1])
    assert (result == expected).all()
    result2 = utils.delta(np.array([4, 3, 7, 4, 2, 92]))
    expected2 = np.array([-1,  4, -3, -2, 90])
    assert (result2 == expected2).all()
    result3 = utils.delta(np.array([[1, 0, 0], [0, 1, 3], [7, -13, 4]]))
    expected3 = np.array([
        [ -1,   1,   3],
        [  7, -14,   1]])
    assert (result3 == expected3).all()
    
def test_means_examples():
    assert (
        utils.means(np.array(list(range(5))))
        == np.array([0.5, 1.5, 2.5, 3.5]) 
        ).all()
    assert (
        utils.means(np.array([4, 3, 7, 4, 2, 92]))
        == np.array([ 3.5,  5. ,  5.5,  3. , 47. ]) 
        ).all()
    assert (
        utils.means(np.array([[1, 0, 0], [0, 1, 3], [7, -13, 4]]))
        == np.array([
            [ 0.5,  0.5,  1.5],
            [ 3.5, -6. ,  3.5]]) 
        ).all()
    
def test_spherical_delta():
    vecs = np.arange(15).reshape(5,3)
    result = utils.spherical_delta(vecs)
    expected = np.array([
        [ 0.18317585,  0.18311308, -3.        ],
        [ 0.34018372,  0.33913504, -3.        ],
        [ 0.49719158,  0.49293804, -3.        ],
        [ 0.65419945,  0.64324482, -3.        ]])
    assert (abs(result - expected) < 0.0000001).all()
    #print (result - expected)
    assert np.allclose(result, expected)
    # assert (result == expected).all()
    
def test_curl_examples():
    vecs = utils.delta(np.arange(15).reshape(5,3))
    assert (
        utils.curl(vecs,vecs)
        == np.array([0., 0., 0., 0.])
        ).all()
    assert (
        utils.curl(utils.pack_3d(np.ones((4,)),-1.5 * np.ones((4,)),np.zeros((4,))),vecs)
        == np.array([5., 5., 5., 5.])
        ).all()
    
def test_inclination_examples():
    result = utils.inclination(np.arange(15).reshape(5,3))
    assert np.allclose(
        result,
        np.array([1.10714872, 0.78539816, 0.71469295, 0.68539502, 0.66942998])
        )
    assert np.allclose(
        np.sin(result),
        np.array([0.89442719, 0.70710678, 0.65538554, 0.63297887, 0.62053909])
        )
    
    
@pytest.mark.viresclient
def test_request_data_examples():
    # assert False
    with patch('viresclient.ReturnedData.to_file') as mock:
        token = os.environ.get('VIRES_TOKEN')
        utils.request_data(token=token)
        assert mock.call_count == 1
        utils.request_data(
            utils.date.datetime(2017, 7, 5),
            utils.date.datetime(2017, 7, 6),
            token=token)
        assert mock.call_count == 2
            
        
@pytest.mark.viresclient
def test_read_cdf():
    pass
    # try:
        # token = os.environ.get('VIRES_TOKEN')
        # data = utils.request_data(token=token,to_file=False)
        

