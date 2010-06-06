"""
This module implements support for deprecated features.
"""

class NativeMatcher(object):
    def message_for_failed_should(self):
        return self._should_message % (self._value, self.arg)

    def message_for_failed_should_not(self):
        return self._should_not_message % (self._value, self.arg)


class NativeHaveMatcher(NativeMatcher):
    def __init__(self):
        self._should_message = "%s does not have %s"
        self._should_not_message = "%s have %s"

    def match(self, value):
        self._value = value
        return self.arg in self._value


class NativeBeMatcher(NativeMatcher):
    def __init__(self):
        self._should_message = "%s is not %s"
        self._should_not_message = "%s is %s"

    def match(self, value):
        self._value = value
        return self._value is self.arg
