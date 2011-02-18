===============
Custom Matchers
===============

Extending Should-DSL with custom matchers is very easy. It is possible to add matchers through functions and classes, for simple and complex behaviors.


Simple Custom Matchers through Functions
========================================

For extending Should-DSL with simple matchers a simple decorated function is enough. The function name must be the name of the matcher. The function must have no parameters and it must return a tuple containing two elements.

The first tuple item is the function (or lambda), receiving two parameters, to be run for the comparison, and the second is the failure message. The failure message must have three string formatting operators (like ``%s``, ``%r``, ``%d``, etc) placeholders. The first operator will be the placeholder for a 'not ' string for failed |should_not| expectations, and an empty string for failed |should| ones. The second and the third will be used for the expected and actual values, respectively. The message is intended to be something like "expected [not ]something from expected_value, got actual_value", but you can use anything you want as long as your message has the same order (placeholder for "not ", expected value, actual value).

::

    >>> from should_dsl import matcher, should, should_not

    >>> @matcher
    ... def be_the_square_root_of():
    ...     import math
    ...     return (lambda x, y: x == math.sqrt(y), "expected %sthe square root of %s, got %s")

    >>> 3 |should| be_the_square_root_of(9)

    >>> 4 |should| be_the_square_root_of(9)
    Traceback (most recent call last):
    ...
    ShouldNotSatisfied: expected the square root of 9, got 4


    >>> 4 |should_not| be_the_square_root_of(16)
    Traceback (most recent call last):
    ...
    ShouldNotSatisfied: expected not the square root of 16, got 4



Not So Simple Matchers through Classes
======================================

If your custom matcher has a more complex behaviour, or if both should and should_not messages differ, or if your messages need to be more richer than those provided by function matchers, you can create custom matchers as classes. In fact, classes as matchers are the preferred way to create matchers, being function matchers only a convenience for simple cases.

Below is an example of the square root matcher defined as a class::

    >>> import math
    >>> class SquareRoot(object):
    ...
    ...     name = 'be_the_square_root_of'
    ...
    ...     def __call__(self, radicand):
    ...         self._radicand = radicand
    ...         return self
    ...
    ...     def match(self, actual):
    ...         self._actual = actual
    ...         self._expected = math.sqrt(self._radicand)
    ...         return self._actual == self._expected
    ...
    ...     def message_for_failed_should(self):
    ...         return 'expected %s to be the square root of %s, got %s' % (
    ...             self._actual, self._radicand, self._expected)
    ...
    ...     def message_for_failed_should_not(self):
    ...         return 'expected %s not to be the square root of %s' % (
    ...             self._actual, self._radicand)
    ...
    >>> matcher(SquareRoot)
    <class ...SquareRoot...>
    >>> 3 |should| be_the_square_root_of(9)
    >>> 4 |should| be_the_square_root_of(9)
    Traceback (most recent call last):
    ...
    ShouldNotSatisfied: expected 4 to be the square root of 9, got 3.0
    >>> 2 |should_not| be_the_square_root_of(4.1)
    >>> 2 |should_not| be_the_square_root_of(4)
    Traceback (most recent call last):
    ...
    ShouldNotSatisfied: expected 2 not to be the square root of 4


.. note::

    If you are using Python 2.6 or greater you can use the class decorator feature (just a cool syntax sugar)::

        @matcher
        class SquareRoot(object):
            """same body here"""


        # instead of:

        class SquareRoot(object):
            """same body here"""

        matcher(SquareRoot)

A matcher class must fill the following requirements:

- a class attribute called *name* containing the desired name for the matcher;
- a *match(actual)* method receiving the actual value of the expectation as a parameter (e.g., in
  *2 \|should\| equal_to(3)* the actual is 2 and the expected is 3). This method should return
  the boolean result of the desired comparison;
- two methods, called *message_for_failed_should* and *message_for_failed_should_not* for returning
  the failure messages for, respectively, should and should_not.

The most common way the expected value is inject to the matcher is through making the matcher
callable. Thus, the matcher call can get the expected value and any other necessary or optional
information. By example, the *close_to* matcher's *__call__()* method receives 2 parameters:
the expected value and a delta. Once a matcher is a regular Python object, any Python can be used.
In *close_to*, delta can be used as a named parameter for readability purposes.


should or should_not?
=====================

For the most matchers, should is the exact opposite to should_not. For the same
expected and actual values, if should_not fails, should will pass; in the same
way, if should fails, should_not passes. However, this is not true for all matchers.
Depending on your matcher semantics, the same expected and actual values can
fail or pass both should and should_not. A good example is the matcher
include_keys. The calls shown below will fail::

    >>> {'a': 1, 'b': 2, 'c': 3} |should| include_keys('a', 'd')
    Traceback (most recent call last):
    ...
    ShouldNotSatisfied: expected target to include key 'd'

    >>> {'a': 1, 'b': 2, 'c': 3} |should_not| include_keys('a', 'd')
    Traceback (most recent call last):
    ...
    ShouldNotSatisfied: expected target to not include key 'a'


In order to make possible to implement matchers like include_keys, Should-DSL
injects, into all matchers, information about what kind of should is being run:
should or should_not. The matcher can access this information in the attribte
"run_with_negate". So, within your matcher you can have::

    if self.run_with_negate:
        # do what you want for a should_not
    else:
        # this matcher was run with should


With this information, the matcher can act according to the way it is being run.

