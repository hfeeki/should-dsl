#coding: utf-8

class Should(object):
    
    def __init__(self, negate=False):
        self._negate = negate
        self._is_thrown_by = False
    
    def _evaluate(self, value):
        if self._negate:
            return not value
        return value
    
    def _negate_str(self):
        if not self._negate:
            return 'not '
        return ''
    
    def __rlshift__(self, lvalue):
        self._lvalue = lvalue
        if not self._has_rvalue:
            return self._check_assertion()
        return self
    
    def __rshift__(self, rvalue):
        self._rvalue = rvalue
        return self._check_assertion()
    
    @property
    def equal_to(self):
        self._func = lambda x, y: x == y
        self._error_message = lambda x, y: '%s is %sequal to %s' % (x, self._negate_str(), y)
        self._has_rvalue = True
        return self
    
    @property
    def true(self):
        self._func = lambda x: x is True
        self._error_message = lambda x: '%s is %sTrue' % (x, self._negate_str())
        self._has_rvalue = False
        return self
    
    @property
    def false(self):
        self._func = lambda x: x is False
        self._error_message = lambda x: '%s is %sFalse' % (x, self._negate_str())
        self._has_rvalue = False
        return self
    
    @property
    def none(self):
        self._func = lambda x: x == None
        self._error_message = lambda x: '%s is %sNone' % (x, self._negate_str())
        self._has_rvalue = False
        return self
    
    @property
    def into(self):
        self._func = lambda item, container: item in container
        self._error_message = lambda item, container: '%s is %sinto %s' % (item, self._negate_str(), container)
        self._has_rvalue = True
        return self 
    
    @property
    def have(self):
        self._func = lambda container, item: item in container
        self._error_message = lambda container, item: '%s does %shave %s' % (container, self._negate_str(), item)
        self._has_rvalue = True
        return self
    
    @property
    def thrown_by(self):
        def check_exception(exception, callable, *args, **kw):
            try:
                callable(*args, **kw)
                return False
            except exception:
                return True
        self._func = check_exception
        self._error_message = lambda exception, callable: '%s is %sthrown by %s' % (exception, self._negate_str(), callable)
        self._has_rvalue = True
        self._is_thrown_by = True
        return self
    
    def _check_assertion(self):
        if self._has_rvalue:
            evaluation = None 
            if self._is_thrown_by and self._rvalue.__class__ in (tuple, list, dict) and len(self._rvalue) > 1:
                evaluation = self._evaluate(self._func(self._lvalue, self._rvalue[0], *self._rvalue[1:]))
            else:
                evaluation = self._evaluate(self._func(self._lvalue, self._rvalue)) 
            if not evaluation:
                raise ShouldNotSatisfied, self._error_message(self._lvalue, self._rvalue)
            else:
                return True
        else:
            if not self._evaluate(self._func(self._lvalue)):
                raise ShouldNotSatisfied, self._error_message(self._lvalue)
            else:
                return True
            
            
class ShouldNotSatisfied(Exception):
    pass

should_be = Should(negate=False)
should_not_be = Should(negate=True)
should_have = Should(negate=False).have
should_not_have = Should(negate=True).have