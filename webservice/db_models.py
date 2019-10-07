from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import ENUM

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

from webservice.number_validator import NumberValidator

db = SQLAlchemy()

# https://stackoverflow.com/questions/2377174/how-do-i-interpret-precision-and-scale-of-a-number-in-a-database
standard_numeric_precision = 8
standard_numeric_scale = 2


class DbModelExtension(db.Model):
    __abstract__ = True

    def to_dict(self):
        tmp_dict = self.__dict__
        ret_dict = {}
        for key in self.__table__.columns.keys():
            if key in tmp_dict:
                if tmp_dict[key].__class__.__name__ == 'datetime':
                    ret_dict[key] = tmp_dict[key].isoformat()
                else:
                    ret_dict[key] = tmp_dict[key]
        return ret_dict

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.to_dict() == other.to_dict():
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


partstatus = ('onboard', 'not_onboard', 'belongs_to_another_container', 'undersized', 'oversized', 'reserved_vertical',
              'reserved_horizontal', 'not_bookable')
partstatus_enum = ENUM(*partstatus, name="partstatus")

orderstatus = ('created', 'shreddered', 'in_production')
orderstatus_enum = ENUM(*orderstatus, name="orderstatus")


class Order(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    customer_order = db.Column(db.String)
    customer = db.Column(db.String)
    project = db.Column(db.String)
    # Interner verantwortlicher des Auftrags
    owner = db.Column(db.String)
    delivery_date = db.Column(db.DateTime)
    shipping_date = db.Column(db.DateTime)
    # Vorgabezeit Montage in Stunden
    expected_time_montage_h = db.Column(db.Integer)
    # Vorgabezeit Teilefertigung in Stunden
    expected_time_manufacturing_h = db.Column(db.Integer)
    # Vorgabezeit Oberfläche in Stunden
    expected_time_surface_h = db.Column(db.Integer)
    # Vorgabezeit Extern in Stunden
    expected_time_extern_h = db.Column(db.Integer)
    assembly_groups = db.relationship("AssemblyGroup", cascade="save-update, merge, delete")
    status = db.Column(orderstatus_enum)
    virtual_carriages = db.relationship("VirtualCarriage", cascade="save-update, merge, delete")


class VirtualCarriage(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    name = db.Column(db.String)
    type = db.Column(db.String)
    parts = db.relationship("Part", cascade="save-update, merge, delete")


class AssemblyGroup(DbModelExtension):
    """Baugruppe"""
    group_id = db.Column(db.Integer, primary_key=True)
    part_mapping = db.Column(db.Integer)
    group_name = db.Column(db.String)
    assembled = db.Column(db.Boolean)
    parts = db.relationship("Part", cascade="save-update, merge, delete")
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))


class Part(DbModelExtension):
    part_number = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    assembly_group_id = db.Column(db.Integer, db.ForeignKey('assembly_group.group_id'))
    imos_id = db.Column(db.Integer)
    virtual_carriage_id = db.Column(db.Integer, db.ForeignKey('virtual_carriage.id'))
    part_mapping = db.Column(db.Integer)
    material_code = db.Column(db.String)
    finished_length = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    finished_width = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    finished_thickness = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    cut_length = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    cut_width = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    overcapacity = db.Column(db.Integer)
    undercapacity = db.Column(db.Integer)
    grain_id = db.Column(db.Integer)
    description = db.Column(db.String)
    production_steps = db.relationship("ProductionStep", cascade="save-update, merge, delete")
    coatings = db.relationship("Coating", cascade="save-update, merge, delete")
    extra_route = db.Column(db.String)
    pattern_info = db.Column(db.String)
    label_info = db.Column(db.String)
    edge_transition = db.Column(db.String)
    batch_number = db.Column(db.String)
    status = db.Column(partstatus_enum)


    @validates('part_number', 'part_mapping')
    def validate_greater_zero(self, key, value):
        return NumberValidator.validate_greater_zero(key, value)

    @validates('overcapacity', 'undercapacity')
    def validate_greater_equals_zero(self, key, value):
        return NumberValidator.validate_greater_equals_zero(key, value)


class ProductionStep(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.Integer, db.ForeignKey('part.part_number'))
    name = db.Column(db.String)
    status = db.Column(db.String)
    description = db.Column(db.String)
    edge_position = db.Column(db.String)
    edge_value = db.Column(db.String)

    def __hash__(self):
        return self.id


class Carriage(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    carriage_name = db.Column(db.String)
    carriage_status = db.Column(db.String)
    current_location = db.Column(db.String)
    next_location = db.Column(db.String)
    destacking_mode = db.Column(db.String)


class Module(DbModelExtension):
    module_number = db.Column(db.Integer, primary_key=True)
    carriage_id = db.Column(db.Integer, db.ForeignKey('carriage.id'), nullable=False)
    max_length = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    max_width = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    max_thickness = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))

    @validates('max_length', 'max_width', 'max_thickness')
    def validate_greater_zero(self, key, value):
        return NumberValidator.validate_greater_zero(key, value)


class Slot(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    slot_name = db.Column(db.String)
    part_number = db.Column(db.Integer, db.ForeignKey('part.part_number'))
    module_number = db.Column(db.Integer, db.ForeignKey('module.module_number'), nullable=False)
    max_length = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    max_width = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))
    max_thickness = db.Column(db.Numeric(precision=standard_numeric_precision, scale=standard_numeric_scale))

    @validates('max_length', 'max_width', 'max_thickness')
    def validate_greater_zero(self, key, value):
        return NumberValidator.validate_greater_zero(key, value)


class Coating(DbModelExtension):
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.Integer, db.ForeignKey('part.part_number'))
    name = db.Column(db.String)
    text_short = db.Column(db.String)
    count = db.Column(db.Integer)
