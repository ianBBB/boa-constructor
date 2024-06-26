__version__ = 0,1,1
__doc__ = """\
This module, Signature, contains a single class Signature. This class
permits the convenient examination of the call signatures of Python
callable objects.

Here's some examples of its use:

    >>> def foo(x, y, z=-1.0, *args, **kw):
    ...     return (x+y)**z
    ...
    >>> f = Signature(foo)

    >>> print 'ordinary arglist:', f.ordinary_args()
    ordinary arglist: ('x', 'y', 'z')

    >>> print 'special_args:', f.special_args()
    special_args: {'keyword': 'kw', 'positional': 'args'}

    >>> print 'full_arglist:', f.full_arglist()
    full_arglist: ['x', 'y', 'z', 'args', 'kw']

    >>> print 'defaults:', f.defaults()
    defaults: {'z': -1.0}

    >>> print 'signature:', str(f)
    signature: foo(x, y, z=-1.0, *args, **kw)

The methods of the Signature class are documented below:

o Signature(func)

  Arguments: func -- this is any callable object written in Python
  Returns:   a Signature instance
  Raises:    TypeError, ValueError

  Behavior:

  The Signature constructor returns a Signature instance for the callable
  object func. If func is not callable, then a TypeError is raised. If
  it is callable, but can't be handled, then a ValueError is raised. (At
  the moment, the latter category are any C builtins.)

o Signature.ordinary_args()

  Returns:   A tuple of strings containing the names of all 'normal'
             arguments.

  Behavior:

  If the callable object has no arguments, the empty tuple is returned.
  The definition of 'normal' includes explicit keyword arguments and the
  'self' argument for methods, but does not include the special arguments
  specified with the '*' or '**' syntax.

o Signature.special_args()

  Returns: A dictionary with the names of the special arguments.

  Behavior:

  This method returns a dictionary of 0, 1, or 2 arguments. An entry
  with a key of 'positional' has the name of the '*'-argument as its
  value, and an entry with a key of 'keyword' has the name of the
  '**'-argument as its value. If the dictionary is empty, then there
  are no special arguments.

o Signature.full_arglist()

  Returns:   A list of all the arguments to the function, whether special
             or not.

  Behavior:

  If there are no special arguments, Signature.full_arglist()'s returns
  a list with the same elements as Signature.ordinary_args(). If there
  are are special arguments, they appended to the end of the list, with
  the '*'-argument preceding the '**'-argument. No asterisks are added
  to the argument names in the returned list.

o Signature.defaults()

  Returns:   A dictionary containing the argument names (as a string) as
             the keys and the default objects as values.

  Behavior:

  If there are no arguments with default values, then an empty dictionary
  is returned. The special arguments specified with the '*' and '**'
  syntax are not considered.


o Signature.__str__()

  Returns:   A string that should resemble the function or method
             declaration.

  Behavior:

  While it's impossible to exactly match the actual declaration, in most
  cases this should look pretty close.
"""

import types, string

class Signature:
    # Magic numbers: These are the bit masks in func_code.co_flags that
    # reveal whether or not the function has a *arg or **kw argument.
    #
    POS_LIST = 4
    KEY_DICT = 8
    def __init__(self, func):
        self.type = type(func)
        self.name, self.func = _getcode(func)
    def ordinary_args(self):
        n = self.func.__code__.co_argcount
        return self.func.__code__.co_varnames[0:n]
    def special_args(self):
        n = self.func.__code__.co_argcount
        x = {}
        #
        #
        #
        if self.func.__code__.co_flags & (self.POS_LIST|self.KEY_DICT):
            x['positional'] = self.func.__code__.co_varnames[n]
            try:
                x['keyword'] = self.func.__code__.co_varnames[n+1]
            except IndexError:
                x['keyword'] = x['positional']
                del x['positional']
        elif self.func.__code__.co_flags & self.POS_LIST:
            x['positional'] = self.func.__code__.co_varnames[n]
        elif self.func.__code__.co_flags & self.KEY_DICT:
            x['keyword'] = self.func.__code__.co_varnames[n]
        return x
    def full_arglist(self):
        base = list(self.ordinary_args())
        x = self.special_args()
        if 'positional' in x:
            base.append(x['positional'])
        if 'keyword' in x:
            base.append(x['keyword'])
        return base
    def defaults(self):
        defargs = self.func.__defaults__
        args = self.ordinary_args()
        mapping = {}
        if defargs is not None:
            for i in range(-1, -(len(defargs)+1), -1):
                mapping[args[i]] = defargs[i]
        else:
            pass
        return mapping
    def __str__(self):
        defaults = self.defaults()
        specials = self.special_args()
        l = []
        for arg in self.ordinary_args():
            if arg in defaults:
                l.append( arg + '=' + str(defaults[arg]) )
            else:
                l.append( arg )
        if 'positional' in specials:
            l.append( '*' + specials['positional'] )
        if 'keyword' in specials:
            l.append( '**' + specials['keyword'] )
        return "%s(%s)" % (self.name, ', '.join(l))

def _getcode(f):
    """_getcode(f)

    This function returns the name and """
    def method_get(f):
        return f.__name__, f.__func__
    def function_get(f):
        return f.__name__, f
    def instance_get(f):
        if hasattr(f, '__call__'):
            return ("%s%s" % (f.__class__.__name__, '__call__'),
                    f.__call__.__func__)
        else:
            s = ("Instance %s of class %s does not have a __call__ method" %
                 (f, f.__class__.__name__))
            raise TypeError(s)
    def class_get(f):
        if hasattr(f, '__init__'):
            return f.__name__, f.__init__.__func__
        else:
            return f.__name__, lambda: None
    codedict = { types.UnboundMethodType: method_get,
                 types.MethodType       : method_get,
                 types.FunctionType     : function_get,
                 types.InstanceType     : instance_get,
                 type        : class_get
                 }
    try:
        return codedict[type(f)](f)
    except KeyError:
        if callable(f): # eg, built-in functions and methods
            raise ValueError("type %s not supported yet." % type(f))
        else:
            raise TypeError("object %s of type %s is not callable." %
                                     (f, type(f)))

if __name__ == '__main__':
    def foo(x, y, z=-1.0, *args, **kw):
        return (x+y)**z
    f = Signature(foo)
    print("ordinary arglist:", f.ordinary_args())
    print("special_args:", f.special_args())
    print("full_arglist:", f.full_arglist())
    print("defaults:", f.defaults())
    print("signature:", end=' ')
