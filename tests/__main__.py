""" Tests the modules safe_user, swarm_util, and FAC_slim
"""

__version__ = '0.1.0'
__author__ = 'Ask Neve Gamby'

import os
import sys
import decimal

import functools
import unittest
import hypothesis as hyp
import hypothesis.strategies as strat
import numpy as np
import math


# from swarmpyfac import safety as su
from swarmpyfac import utils as sw
from swarmpyfac import fac as slim

# try:
    # from swarmpyfac import safety as su
    # from swarmpyfac import utils as sw
    # from swarmpyfac import fac as slim
# except ImportError:
    # sys.path.insert(0, os.path.abspath('../'))
    # from swarmpyfac import safety as su
    # from swarmpyfac import utils as sw
    # from swarmpyfac import fac as slim

# from ..swarmpyfac import safety as su
# from ..swarmpyfac import utils as sw
# from ..swarmpyfac import fac as slim

_nice_text = r'[a-zA-Z0-9_ \t\n\r\f\v<>"\\\']'


hyp.settings.register_profile('fast',max_examples=12)
hyp.settings.register_profile('quality',max_examples=777)
hyp.settings.load_profile('fast')

# Breaks unittest
# if __name__ == '__main__':
    # temp = [i for i,v in enumerate(sys.argv) if v == '--profile']
    # if temp and len(sys.argv) > temp[0]:
        # try:
            # hyp.settings.load_profile(sys.argv[temp[0]])
        # except hyp.errors.InvalidArgument:
            # #wasnt what we looked for
            # pass

# Disclaimer:
# There is a reason the following code is considered privat.
# It contains a decent amount of higher order logic,
# and it is somewhat easy to make mistake with it
# if you are not familiar with higher order functions.
# The standard quality guidelines are therefor not applied,
# and you may should be cautios if you use them.


_mult_save_floats = ((),{'min_value':0. - 10.**100, 'max_value':10.**100})


def _maybe_pops(source, keys):
    """ Create a new dict based on the intersection of source keys and keys..
    
    Create a new dictionary. Each pair of key and value comes from source.
    Inclusion in the result is based on intersection of source's keys and keys.
    
    Parameters
    ----------
    source : dict
        A dictionary forming the base of the output.
        The result is a subset of this dictionary.
    keys : iterable(immutable)
        Effectively a list of the keys to extract from source
        (though any iterable should do).
        The keys do not need to be in source, and only those also
        in source will be in the result.
        
    Result
    ------
    dict
        The dict of key value pairs based on the intersection of 
        the source's keys and keys.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> options = {'flag':True, 'int':5, 'float':3.5,'array':np.arange(5)}
    >>> maybe_pops(options,['flag'])
    {'flag': True}
    >>> maybe_pops(options,['int','float'])
    {'int': 5, 'float': 3.5}
    >>> maybe_pops(options,['flag','array'])
    {'array': array([0, 1, 2, 3, 4])}
    >>> options
    {}
    """

    return {key: source.pop(key) for key in keys if key in source}


def _maybe_keys(source, keys):
    """ Create a new dict, by poping the intersection of source's keys and keys.
    
    Create a new dictionary. Each pair of key and value comes from source.
    Inclusion in the result is based on intersection of source's keys and keys.
    This function has the side-effect that the key-value pairs in the result
    are removed from source (poped).
    
    Parameters
    ----------
    source : dict
        A dictionary forming the base of the output.
        The result is a subset of this dictionary.
        There (may) be side-effect on this, of the form that some
        key-value pairs (may) be removed.
    keys : iterable(immutable)
        Effectively a list of the keys to extract from source
        (though any iterable should do).
        The keys do not need to be in source, and only those also
        in source will be in the result.
        
    Result
    ------
    dict
        The dict of key value pairs based on the intersection of 
        the source's keys and keys.
        
    Examples
    --------
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> options = {'flag':True, 'int':5, 'float':3.5,'array':np.arange(5)}
    >>> maybe_keys(options,['flag'])
    {'flag': True}
    >>> maybe_keys(options,['int','float'])
    {'int': 5, 'float': 3.5}
    >>> maybe_keys(options,['flag','array'])
    {'flag': True, 'array': array([0, 1, 2, 3, 4])}
    >>> options
    {'flag': True, 'int': 5, 'float': 3.5, 'array': array([0, 1, 2, 3, 4])}
    """
    return {key: source[key] for key in keys if key in source}


def _call(function, dict_, *args, use_pop=None, **kwargs):
    """ Call a function with arguments mixed from different sources.
    
    Call a function, by mixing the arguments for the function.
    Specifically it extract extra parameters from `dict_` 
    to use as default keyword arguments in case they have not
    been specified otherwise.
    If the function called accepts `**kwargs`, then all `dict_`
    arguments not otherwise relevant will also be added,
    so they can be passed further down possible call chains.
    
    Parameters
    ----------
    function : a -> b
        A function to be called with the composed arguments.
        Note that the argument names for this function is used
        to determine which keyword arguments to extract from `dict_`
    `dict_` : dict
        A directory of keyword argument pairs that might be 
        keyword arguments for the function.
        There is no requirement for any overlap with argument names
        of function, but only the overlap is used here.
    *args
        The positional arguments to be passed to function.
    use_pop : boolean, optional
        A flag for whether the arguments in `dict_` used in the call
        should be removed from dict.
        Defaults to False (None, which evaluates to False).
    **kwargs
        The keyword arguments to be passed to the function.
        These keyword arguments takes priority over those in `_dict`.
        
    Returns
    -------
    ?
        The result of the function call.
        
    Examples
    --------
    Base use:
    >>> from pyfac.utils import *  # doctest: +SKIP
    >>> options = {'password':'MyPassword','IV':16*'\x0F','target_index':1}
    >>> call(safe_user.box_content,options,'bla') # doctest: +ELLIPSIS
    b'...'
    """
    names = list(function.__code__.co_varnames[:function.__code__.co_argcount])
    residual = [name for name in names[len(args):] if name not in kwargs]
    maybe_get = _maybe_pops if use_pop else _maybe_keys
    options = maybe_get(dict_, residual)
    if function.__code__.co_flags & 0x08: #this flag is true if function as a **kwargs
        # consider the optimization of making a set(names) for faster lookups below
        options.update({k:v for k,v in dict_.items() if k not in names})
        # consider whether use_pop should be inheireted
        # if use_pop is not None:
            # options.update({'use_pop':use_pop})
    return function(*args, **kwargs, **options)
    

def _reg_gen(text,*args):
    return strat.from_regex(r'\A' + text.format(*args)+ r'\Z')

    
def _zip_map(function,*args):
    return map(lambda arg: function(*arg),zip(*args))
    
    
def _apply_args(function, options=None):
    assert callable(function)
    if options is None:
        options = ((),{})
    (args,kwargs) = options
    return function(*args, **kwargs)
    

#unused
def _succeds(function, options=None, exception=Exception):
    try:
        _apply_args(function,options)
    except exception:
        return False
    return True
    
    
def _apply_map(functions, args):
    assert(all(map(callable, functions)))
    if args is None:
        if not hasattr(functions, '__len__'):
            functions = [func for func in functions]
        args = [None] * len(functions)
    return [_apply_args(function, arg) for function, arg in zip(functions, args)]
    
    
def _merge_args(priority=None,fallback=None):
    if priority is None:
        priority = ((),{})
    if fallback is None:
        fallback = ((),{})
    args = priority[0] + fallback[0]
    kwargs = {**fallback[1],**priority[1]}
    return (args,kwargs)
    
    
def _nd_arrays(length,dims,elems=strat.floats,elem_args=None):
    if elems is strat.floats and elem_args is None:
        elem_args = ((),{'min_value':0. - 10.**280,
                         'max_value':10.**280})
    return strat.lists(strat.lists(_apply_args(elems,elem_args),
        min_size=dims, max_size=dims),
        min_size=length, max_size=length).map(np.array)
        
        
def _linked_gens(gens,links,gen_args=None,link_args=None, link_map=None):
    if gen_args is None:
        gen_args = [None] * len(gens)
    if link_args is None:
        link_args = [None] * len(links)
    def _inner_map(args):
        if link_map is None:
            args_list = map(functools.partial(_merge_args,(args,{})), gen_args)
        else:
            maped_args = [(f(*args),{}) for f in link_map]
            args_list = _zip_map(_apply_args, maped_args, gen_args)
        return strat.tuples(*_apply_map(gens,args_list))
        
    return strat.tuples(*_apply_map(links, link_args)).flatmap(_inner_map)
        # map(_apply_args,zip(gens,
            # map(functools.partial(_merge_args,(args,{})), gen_args)))))
    
    
def _several_nd_arrays(dims, elems=strat.floats, elem_args=None, min_length = 1, max_length = 1<<5, length_modifiers = None):
    if length_modifiers is not None:
        length_modifiers = [lambda i, mod=mod: i + mod 
                            for mod in length_modifiers]
    number = len(dims)
    return _linked_gens([_nd_arrays]*number,[strat.integers],gen_args=[((),{'elems':elems,'dims':dim,'elem_args':elem_args}) for dim in dims],link_args=[((),{'min_value':min_length,'max_value':max_length})], link_map=length_modifiers)
    
    
def _delta_index(first,second,relative_delta=0.1**1,absolute_delta=0.1**14):
    """ Like _close, but return how many times it is outside.
    _close could work like _delta_index(...) <= 1.
    """
    return abs(first-second) / (absolute_delta + relative_delta*max(abs(first),abs(second)))
    
def _close(first,second,relative_delta=1.e-14,absolute_delta=0, other_value=None,coordinate=(),find_other=None,**options):
    # consider setting absolute_delta default to 1.e-14 or 1.e-32, though 0 still works.
    if other_value is None:
        other_value = 0. if find_other is None else _call(find_other,options,*coordinate)
    return abs(first-second) <= absolute_delta + relative_delta*max(abs(first),abs(second),abs(other_value))
    
def _all_close(first,second, coordinate=(), **options):
    if not hasattr(first,'__len__'):
        return _call(_close,options,first,second,coordinate=coordinate) #_close(first,second)
    return all([_call(_all_close,options,one,two,coordinate=coordinate+(i,)) for i,(one,two) in enumerate(zip(first,second))])
    
    
def _assert_array_close(self, first, second, msg=None, **options):
    if msg is None:
        diff = None
        msg_comp = [str(first),'!~',str(second)]
        try:
            diff = first-second
            msg_comp += ['with difference',str(diff)]
        except Exception:
            pass
        msg = ' '.join(msg_comp)
    self.assertTrue(_call(_all_close, options,first,second,left=first,right=second),msg)
    #self.assertTrue(np.allclose(first,second),msg)
    
def _assert_array_equal(self, first, second, msg=None):
    self.assertTrue(np.alltrue(first == second),msg)
    
    
class AlphaTestUtilTests(unittest.TestCase):
    """ Named with prefix alpha to ensure that we test this first.
    This part tests the actual test framework.
    """

    @hyp.given(_nd_arrays(10,3))
    def test_nd_arrays(self,stuff):
        self.assertEqual(stuff.shape,(10,3))
        
    @hyp.given(_several_nd_arrays([3]*4))
    # @hyp.given(strat.tuples(strat.integers(min_value=0,max_value=1<<5),strat.integers(min_value=1,max_value=10)).flatmap(lambda args: _nd_arrays(args[0],args[1])))
    def test_several_nd_arrays(self,stuff):
        # print([array.shape for array in stuff])
        # print(stuff)
        self.assertEqual(len(stuff),4)
        self.assertEqual(stuff[0].shape[1], 3)
        self.assertTrue(all(map(lambda x: x.shape == stuff[0].shape,stuff[1:])))
    
    
    
    
    
# class SafeUserHypothesisTests(unittest.TestCase):
    
    # @hyp.given(strat.text())
    # @hyp.example('')
    # def test_pad_unpad_invariance1(self, text):
        # self.assertEqual(su.remove_padding(su.add_padding1(text)), text)
        
    # @hyp.given(strat.text())
    # @hyp.example('')
    # def test_pad_unpad_invariance2(self, text):
        # self.assertEqual(su.remove_padding(su.add_padding2(text)), text)
        
    # @hyp.given(strat.text())
    # @hyp.example('')
    # def test_pad_unpad_invariance3(self, text):
        # self.assertEqual(su.remove_padding(su.add_padding3(text)), text)
        
    # @hyp.given(strat.text(),strat.integers(min_value=4, max_value=1<<15))
    # @hyp.example('other message',16)
    # @hyp.example('another message',8)
    # @hyp.example('',1)
    # def test_pad_unpad_invaraince1_other_base(self, text, base):
        # self.assertEqual(su.remove_padding(su.add_padding1(text,base)), text)
        
    # @hyp.given(strat.text(),strat.integers(min_value=4, max_value=1<<15))
    # @hyp.example('other message',16)
    # @hyp.example('another message',8)
    # @hyp.example('',1)
    # def test_pad_unpad_invaraince2_other_base(self, text, base):
        # self.assertEqual(su.remove_padding(su.add_padding2(text,base)), text)
        
    # @hyp.given(strat.text(),strat.integers(max_value=1<<15))
    # @hyp.example('other message',16)
    # @hyp.example('another message',8)
    # @hyp.example('',1)
    # def test_pad_unpad_invaraince2_other_base(self, text, base):
        # self.assertEqual(su.remove_padding(su.add_padding3(text,base)), text)
        
    # # @hyp.given(strat.text(),strat.integers(min_value=4))
    # # @hyp.example('other message',16)
    # # @hyp.example('another message',8)
    # # @hyp.example('',1)
    # # def test_pad_12_same_other_base(self, text, base):
        # # self.assertEqual(su.add_padding1(text,base), su.add_padding2(text,base))
        
    # @hyp.given(strat.text(),strat.integers(min_value=4, max_value=1<<15))
    # @hyp.example('other message',16)
    # @hyp.example('another message',8)
    # @hyp.example('',1)
    # def test_pad_length_other_base(self, text, base):
        # a1 = su.add_padding1(text,base)
        # a2 = su.add_padding2(text,base)
        # a3 = su.add_padding3(text,base)
        # gt = lambda t,ref: self.assertTrue(len(t) > ref,'failed on: ' + str(len(t)) + ' > ' + str(ref))
        # gt(a1, base >>1)
        # gt(a2, base >>1)
        # gt(a3, base >>1)
        # gt(a3, base - len(text))
        # # self.assertTrue(len(a1) > base>>1)
        # # self.assertTrue(len(a2) > base>>1 )
        # # self.assertTrue(len(a3) > base>>1 )
        # # self.assertTrue(len(a3) > base - len(text) )
        # self.assertEqual(len(a1),len(a2))
        # self.assertTrue(len(a2) <= len(a3))
        
    # @hyp.given(strat.text())
    # @hyp.example('')
    # def test_pad_len_mod_16_0_base(self, text):
        # self.assertEqual(len(su.add_padding1(text)) % 16, 0)
        
    # @hyp.given(strat.text())
    # @hyp.example('')
    # def test_pad_len_mod_16_0_2(self, text):
        # self.assertEqual(len(su.add_padding2(text)) % 16, 0)
        
    # @hyp.given(text=_reg_gen(r'({}{})*',_nice_text,r'{16}'), password=strat.text())
    # @hyp.example('','')
    # def test_encrypt_decrypt_invariance(self, text, password):
        # self.assertEqual(su.decrypt(su.encrypt(text, password), password), text)
    
    # @hyp.given(text=_reg_gen(r'{}*',_nice_text), password=strat.text())
    # @hyp.example('','')
    # def test_box_unbox_invariance(self, text, password):
        # self.assertEqual(su.unbox_content(su.box_content(text, password), password), text)
    
class UtilHypothesisTests(unittest.TestCase):
    
    @hyp.given(_several_nd_arrays([3]))
    def test_pack_3d_self_pack_invariance(self,vectors):
        vector = vectors[0]
        _assert_array_equal(self,sw.pack_3d(*[vector[:,i] for i in range(3)]),vector)
    
    @hyp.given(_several_nd_arrays([1]))
    def test_as_3d_self_pack_invariance(self,vectors):
        base = vectors[0][:,0]
        vector = sw.as_3d(base)
        _assert_array_equal(self, base, np.squeeze(vector[:,0]))
        _assert_array_equal(self, base, np.squeeze(vector[:,1]))
        _assert_array_equal(self, base, np.squeeze(vector[:,2]))
        
        
    @hyp.given(_several_nd_arrays([1,3],min_length=2))
    def test_delta_properties(self,vectors):
        for vector in vectors:
            highest = np.max(abs(vector))
            vector_mod = sw.delta(vector)
            self.assertEqual(len(vector_mod), len(vector)-1)
            effective_sum = np.array([math.fsum(vector_mod[:,i]) for i in range(vector.shape[1])])
            _assert_array_close(self,effective_sum,vector[-1]-vector[0],other_value=highest)
    
    @hyp.given(_several_nd_arrays([1,3],min_length=2))
    def test_means_properties(self,vectors):
        for vector in vectors:
            vector_mod = sw.means(vector)
            self.assertEqual(len(vector_mod), len(vector)-1)
            is_ascending = np.logical_and(vector[:-1] <= vector_mod,
                                          vector_mod <= vector[1:])
            is_decending = np.logical_and(vector[:-1] >= vector_mod,
                                          vector_mod >= vector[1:])
            self.assertTrue(np.alltrue(np.logical_or(is_ascending, is_decending)))
    
    @hyp.given(_several_nd_arrays([1,3],min_length=3))
    def test_delta_means_together(self,vectors):
        for vector in vectors:
            vec_delta = sw.delta(vector)
            vec_mean = sw.means(vector)
            self.assertEqual(len(vec_delta),len(vec_mean))
            is_ascending = np.logical_and(vector[:-1] <= vec_mean,
                                          vec_mean <= vector[1:])
            is_decending = np.logical_and(vector[:-1] >= vec_mean,
                                          vec_mean >= vector[1:])
            _assert_array_equal(self,is_ascending,vec_delta >= 0)
            _assert_array_equal(self,is_decending,vec_delta <= 0)
            _assert_array_close(self,sw.means(vec_delta),sw.delta(vec_mean), find_other=lambda i,j: vector[i+1,j])
        
    @hyp.given(_several_nd_arrays([3], elem_args=_mult_save_floats, min_length=2))
    def test_self_transform(self,vectors):
        (velocities,) = vectors
        transform = sw.NEC_to_VSC(velocities)
        in_vsc = transform(velocities)
        _assert_array_close(self,in_vsc[:,0],in_vsc[:,1])
        _assert_array_close(self,in_vsc[:,0]**2 + in_vsc[:,1]**2,
                            velocities[:,0]**2 + velocities[:,1]**2)
        
    # @hyp.seed(306531992837016658513041913990675809140) # IDed: floating point rounding error
    @hyp.given(_several_nd_arrays([3,3],min_length=2))
    def test_diff_transform_invariance(self,vectors):
        velocities, Bs = vectors
        transform = sw.NEC_to_VSC(velocities[:-1])
        # conversion = lambda xss: np.array([[decimal.Decimal(x) for x in xs] for xs in xss])
        # # velocities = conversion(velocities)
        # Bs = conversion(Bs)
        # angles = -np.arctan2(velocities[:-1, 0] - velocities[:-1, 1],
                            # velocities[:-1, 0] + velocities[:-1, 1])
        # sines = np.array(list(map(decimal.Decimal,np.sin(angles))))
        # cosines = np.array(list(map(decimal.Decimal,np.cos(angles))))
        # transform = lambda xs: sw.pack_3d(
                        # cosines * xs[:,0] + sines * xs[:,1],
                        # - sines * xs[:,0] + cosines * xs[:,1],
                        # xs[:,2])
        B1 = transform(Bs[:-1])
        B2 = transform(Bs[1:])
        # find = lambda i,j,left,right:max(np.max(abs(left[i,:])),np.max(abs(right[i,:])))
        find = lambda i,j,left,right:max(*map(lambda x: np.max(abs(x)),[left[i,:],right[i,:],Bs[i,:]]))
        # left = B2-B1
        # right = transform(sw.delta(Bs))
        # if not _all_close(left,right):
            # print('Failure on:')
            # print('velocities',velocities)
            # print('Bs',Bs)
            # print('left: ', left)
            # print('right: ', right)
            # print('diff: ', left-right)
            # print('is close', np.array([[_close(one,two) for one,two in zip(oneA,twoA)] for oneA,twoA in zip(left,right)]))
        # _assert_array_close(self,left,right)
        # print(Bs,sw.delta(Bs))
        _assert_array_close(self,B2-B1,transform(sw.delta(Bs)),find_other=find)
        
    @hyp.given(_several_nd_arrays([3], elem_args=_mult_save_floats, min_length=2))
    def test_inclination_as_sin(self,vectors):
        (vectors,) = vectors
        inclinations = sw.inclination(vectors)
        L2 = np.sum(vectors*vectors,axis=1)**0.5
        reference = np.zeros_like(inclinations)
        reference[L2 != 0.] = vectors[L2 != 0.,2]
        _assert_array_close(self,np.sin(inclinations)*L2,reference)
        
    # this test makes no sense
    # # @hyp.settings(max_examples=5000)
    # @hyp.given(_several_nd_arrays([3], min_length=2))
    # def test_curl_sanity(self,vectors):
        # (vectors,) = vectors
        # vectors = sw.delta(vectors)
        # non_zeros = list(map(all,vectors != 0.))
        # # print(non_zeros)
        # vec_non_zero = vectors[non_zeros]
        # left,right = sw.curl(vec_non_zero,vec_non_zero),np.zeros(len(vec_non_zero))
        # result = _all_close(left,right)
        # if not result:
            # print(non_zeros,vectors,left,right,result)
        # self.assertTrue(result)
        # # _assert_array_close(self,left,right)
        
    #TODO: insert test to check whether .func_code.co_flags bit 0x08 still refers to whether **kwargs is in the function
    
class FACSlimHypothesisTests(unittest.TestCase):
    @hyp.given(_several_nd_arrays([3]*4))
    def test_split_models(self, vectors):
        # base, others = np.array([]), [np.array([])]
        base,*others = vectors
        (res, model) = slim.split_models(base, *others)
        self.assertEqual(len(base),len(res))
        self.assertEqual(len(res),len(model))
        total = model + res
        def find(i,j):
            return max(*map(lambda x: abs(x[i,j]),others))
        _assert_array_close(self, base, total, find_other=find)
        _assert_array_close(self, model, sum(others), find_other=find)
    
if __name__ == '__main__':
    # hyp.settings.load_profile('quality')
    unittest.main()
