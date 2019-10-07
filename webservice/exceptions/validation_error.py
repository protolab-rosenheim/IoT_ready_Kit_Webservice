class ValidationError(Exception):
    """
        ValidationError to be raised if validating an input fails.
        According to https://flask-restless.readthedocs.io/en/latest/customizing.html#capturing-validation-errors
        'an instance of a specified validation error will have a errors attribute, which is a dictionary mapping
        field name to error description (note: one error per field)'.
        status_code is for information purpose only, changing the field will not change the actual http status code.
        """

    def __init__(self, error_message):
        Exception.__init__(self)
        self.errors = dict([("status_code", 400), ("error_message", error_message)])
