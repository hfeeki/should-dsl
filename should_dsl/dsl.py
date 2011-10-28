import sys
import re
from types import FunctionType


_predicate_regexes = set(['is_(.+)', 'is(.+)'])


class Should(object):

    def __init__(self, negate=False):
        self._negate = negate
        self._matchers_by_name = dict()
        self._identifiers_named_equal_matchers = dict()
        self._outer_frame = None

    def _evaluate(self, value):
        if self._negate:
            return not value
        return value

    def __ror__(self, lvalue):
        self._lvalue = lvalue
        self._inject_negate_information()
        return self

    def __or__(self, rvalue):
        self._rvalue = rvalue
        return self._check_expectation()

    def _check_expectation(self):
        if not self._evaluate(self._rvalue.match(self._lvalue)):
            raise ShouldNotSatisfied(self._negate and \
                self._rvalue.message_for_failed_should_not() or \
                self._rvalue.message_for_failed_should())


    def _inject_negate_information(self):
        for matcher_name, matcher_function in self._matchers_by_name.items():
            matcher = getattr(sys.modules['should_dsl'], matcher_name)
            try:
                matcher.run_with_negate = self._negate
            except AttributeError:
                pass

    def add_matcher(self, matcher_object):
        if (hasattr(matcher_object, 'func_name') or
            isinstance(matcher_object, FunctionType)):
            function, message, not_for_should, not_for_should_not = \
                self._process_custom_matcher_function(matcher_object)
            class GeneratedMatcher(object):
                name = matcher_object.__name__
                def __init__(self):
                    self._function, self._message = function, message
                def __call__(self, arg):
                    self._arg = arg
                    return self
                def match(self, value):
                    self._value = value
                    return self._function(self._value, self._arg)
                def message_for_failed_should(self):
                    return self._build_message(not_for_should)
                def message_for_failed_should_not(self):
                    return self._build_message(not_for_should_not)
                def _build_message(self, not_):
                    try:
                        return self._message % (self._value, not_, self._arg)
                    except TypeError:
                        return self._message % {
                            'expected': self._arg,
                            'not': not_,
                            'actual': self._value}

            matcher_object = GeneratedMatcher
            name = GeneratedMatcher.name
        else:
            name = matcher_object.name
        self._ensure_matcher_init_doesnt_have_arguments(matcher_object)
        setattr(sys.modules['should_dsl'], name, matcher_object())
        self._matchers_by_name[name] = matcher_object

    def _ensure_matcher_init_doesnt_have_arguments(self, matcher_object):
        try:
            matcher_object()
        except TypeError:
            e = sys.exc_info()[1]
            if str(e).startswith('__init__() takes exactly'):
                raise TypeError('matcher class constructor cannot have arguments')
            else:
                raise

    def _process_custom_matcher_function(self, matcher_function):
        values = matcher_function()
        function, message = values[0:2]
        if len(values) <= 2:
            nots = ('not ', '')
        else:
            nots = values[2]._negate and ('', 'not ') or ('not ', '')
        return (function, message) + nots

    def add_aliases(self, **aliases):
        for name, alias in aliases.items():
            matcher = self._matchers_by_name[name]
            self._matchers_by_name[alias] = matcher
            setattr(sys.modules['should_dsl'], alias, matcher())


class ShouldNotSatisfied(AssertionError):
    '''Extends AssertionError for unittest compatibility'''


should = Should(negate=False)
should_not = Should(negate=True)

def matcher(matcher_object):
    '''Adds given matcher to should objects. We recommend you use it as a decorator'''
    should.add_matcher(matcher_object)
    should_not.add_matcher(matcher_object)
    return matcher_object

def matcher_configuration(verifier, message, word_not_for=should_not):
    return (verifier, message, word_not_for)

def aliases(**kwargs):
    should.add_aliases(**kwargs)
    should_not.add_aliases(**kwargs)

