from webservice.exceptions.validation_error import ValidationError


class NumberValidator(object):
    @staticmethod
    def validate_greater_zero(key, value):
        if value > 0:
            return value
        else:
            raise ValidationError(key + " must be greater than 0")

    @staticmethod
    def validate_greater_equals_zero(key, value):
        if value >= 0:
            return value
        else:
            raise ValidationError(key + " must be greater than or equal to 0")
