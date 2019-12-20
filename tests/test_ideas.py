""" This module is supposed to tests ideas about the code,
such as whether two approaches yield the same result and so on.
Failure in this module should be handled differently,
and tests in this module are more temporary.
"""

import pytest
import numpy as np
import hypothesis as hyp
import hypothesis.strategies as strat

import testhelpers as helper
import swarmpyfac as sw

@hyp.given(helper._several_nd_arrays([3]))
def test_ab_pack_3d_vs_np_stack(vectors):
    vector = vectors[0]
    a = sw.utils.pack_3d(*[vector[:,i] for i in range(3)])
    b = np.stack(tuple(vector[:,i] for i in range(3)),axis=1)
    assert (a == b).all()