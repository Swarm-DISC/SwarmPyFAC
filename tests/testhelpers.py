""" This module includes some helpers for writing more complicated tests.
"""

import functools

import numpy as np
import hypothesis as hyp
import hypothesis.strategies as strat

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
    
def test_fail_me():
    assert False
    