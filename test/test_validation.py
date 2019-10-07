from nose.tools import *

from webservice.number_validator import *
from webservice.exceptions.validation_error import ValidationError


def test_greater_equals_accepts_zero():
    result = NumberValidator.validate_greater_equals_zero('test', 0)
    assert_equal(result, 0)


@raises(ValidationError)
def test_greater_equals_does_not_accept_below_zero():
    NumberValidator.validate_greater_equals_zero('test', -0.1)


def test_greater_accepts_above_zero():
    result = NumberValidator.validate_greater_zero('test', 0.1)
    assert_equal(result, 0.1)


@raises(ValidationError)
def test_greater_does_not_accept_below_zero():
    NumberValidator.validate_greater_zero('test', 0)


@raises(ValidationError)
def test_greater_does_not_accept_below_zero():
    NumberValidator.validate_greater_zero('test', -0.1)
