
import numpy as np
import swarmpyfac.utils as utils


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