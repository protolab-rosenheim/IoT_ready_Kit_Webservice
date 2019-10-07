from nose.tools import *
from datetime import datetime

from webservice.db_models import *


class SomeClass(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    customer_order = db.Column(db.String)
    shipping_date = db.Column(db.DateTime)


def test_date_time_is_iso_format():
    now = datetime.now()
    test_object = SomeClass(id=1, customer_order='some order', shipping_date=now)
    dict = test_object.to_dict()
    assert_equal(dict['shipping_date'], now.isoformat())


def test_missing_attribute_is_not_in_dict():
    test_object = SomeClass(customer_order='some order')
    dict = test_object.to_dict()
    assert_false(id in dict)


def test_attribute_is_in_dict():
    test_object = SomeClass(customer_order='some order')
    dict = test_object.to_dict()
    assert_equal(dict['customer_order'], 'some order')
