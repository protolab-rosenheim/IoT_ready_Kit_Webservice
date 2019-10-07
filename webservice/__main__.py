import json
import logging
import logging.config
import datetime
import time

from webservice.db_models import *
from webservice.exceptions import validation_error
from webservice.__init__ import *

import flask
import flask_restless
from flask import request, abort , jsonify
from flask_cors import CORS
from opcua import Client
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def setup_logging(path_to_config, default_level=logging.INFO):
    if os.path.exists(path_to_config):
        with open(path_to_config, 'rt') as config_file:
            config = json.load(config_file)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == "__main__":
    setup_logging(config_folder + '/logging.json')
    logger = logging.getLogger(__name__)

    # Create the Flask application and the Flask-SQLAlchemy object.
    app = flask.Flask(webservice_conf['webserver']['name'])
    app.config['DEBUG'] = debug_mode
    app.config['LOGGER_NAME'] = 'iot_ready_kit_webservice'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_drivername + '://' + \
                                            db_username + ':' + \
                                            db_password + '@' + \
                                            db_host+ ':' + \
                                            db_port + '/' +\
                                            db_database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)

    # Create the database tables.
    db.create_all()

    # Create the Flask-Restless API manager.
    manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker()
    Session.configure(bind=engine)

    api_version_string = '/api/v1'
    # Create API endpoints, which will be available at /api/v1/<tablename> by
    # default. Allowed HTTP methods can be specified as well.
    manager.create_api(Order, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True)
    manager.create_api(AssemblyGroup, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True)
    manager.create_api(Part, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True)
    manager.create_api(Carriage, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True)
    manager.create_api(Module, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                      results_per_page=0, allow_delete_many=True)
    manager.create_api(Slot, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True)
    manager.create_api(ProductionStep, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True, allow_patch_many=True, )
    manager.create_api(Coating, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True)
    manager.create_api(VirtualCarriage, methods=['GET', 'POST', 'PUT', 'DELETE'], url_prefix=api_version_string,
                       results_per_page=0, allow_delete_many=True, )


    @app.route(api_version_string + '/marrying', methods=['PUT'])
    def marry():
        params = request.get_json()
        # set carriage to first location
        carriages = Carriage.query.all()
        for carriage in carriages:
            carriage.carriage_status = 'in use'
            carriage.current_location = 'CU1'
            db.session.commit()
        # carriage should be empty
        slots = Slot.query.all()
        for slot in slots:
            slot.part_number = None
            db.session.commit()

        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        # reset all other database entries
        sql = text(
            'DROP TABLE IF EXISTS   public.order CASCADE ; DROP TABLE IF EXISTS public.part CASCADE ; DROP TABLE IF EXISTS  public.coating CASCADE; '
            'DROP TABLE IF EXISTS   public.assembly_group CASCADE; DROP TABLE IF EXISTS  public.virtual_carriage CASCADE; DROP TABLE IF EXISTS  public.production_step CASCADE;  ')
        engine.execute(sql)
        db.create_all()

        orders = params['orders']
        assemblygroups = params['assemblyGroups']
        parts = params['parts']
        vcarriages = params['vCarriages']
        coatings = params['coatings']
        prodsteps = params['prodSteps']

        try:
            for order in orders:
                db.session.add(Order(
                    id=order['id'],
                    customer_order=order['customer_order'],
                    customer=order['customer'],
                    delivery_date=order['delivery_date'],
                    shipping_date=order['shipping_date'],
                    status=order['status']
                ))
                db.session.commit()
                logger.info('%s %i %s', 'order', order['id'], 'added to database')

            for vCarriage in vcarriages:
                db.session.add(VirtualCarriage(
                    id=vCarriage['id'],
                    order_id=vCarriage['order_id'],
                    name=vCarriage['name'],
                    type=vCarriage['type']
                ))
                db.session.commit()
                logger.info('%s %i %s', 'virtual carriage', vCarriage['id'], 'added to database')

            for asG in assemblygroups:
                db.session.add(AssemblyGroup(
                    group_id=asG['group_id'],
                    part_mapping=asG['part_mapping'],
                    group_name=asG['group_name'],
                    assembled=asG['assembled'],
                    order_id=asG['order_id']))
                db.session.commit()
                logger.info('%s %i %s', 'assembly group', asG['group_id'], 'added to database')

            for part in parts:
                db.session.add(Part(
                    part_number=part['part_number'],
                    order_id=part['order_id'],
                    assembly_group_id=part['assembly_group_id'],
                    imos_id=part['imos_id'],
                    virtual_carriage_id=part['virtual_carriage_id'],
                    part_mapping=part['part_mapping'],
                    material_code=part['material_code'],
                    finished_length=part['finished_length'],
                    finished_width=part['finished_width'],
                    finished_thickness=part['finished_thickness'],
                    cut_length=part['cut_length'],
                    cut_width=part['cut_width'],
                    overcapacity=part['overcapacity'],
                    undercapacity=part['undercapacity'],
                    grain_id=part['grain_id'],
                    description=part['description'],
                    extra_route=part['extra_route'],
                    pattern_info=part['pattern_info'],
                    label_info=part['label_info'],
                    edge_transition=part['edge_transition'],
                    batch_number=part['batch_number'],
                    status=part['status']))
                db.session.commit()
                logger.info('%s %i %s', 'part', part['part_number'], 'added to database')

            for coating in coatings:
                db.session.add(Coating(
                    id=coating['id'],
                    part_number=coating['part_number'],
                    name=coating['name'],
                    text_short=coating['text_short'],
                    count=coating['count']
                ))
                db.session.commit()
                logger.info('%s %i %s', 'coating', coating['id'], 'added to database')

            for prodstep in prodsteps:
                db.session.add(ProductionStep(
                    id=prodstep['id'],
                    part_number=prodstep['part_number'],
                    name=prodstep['name'],
                    status=prodstep['status'],
                    description=prodstep['description'],
                    edge_position=prodstep['edge_position'],
                    edge_value=prodstep['edge_value']
                ))
                db.session.commit()
                logger.info('%s %i %s', 'ProductionStep', prodstep['id'], 'added to database')



        except Exception as e:
            abort(500)

        finally:
            return jsonify(
                status=200
            )


    @app.route(api_version_string + '/call', methods=['POST'])
    def call():
        api_call_params = request.get_json()

        if any(param not in api_call_params for param in ('serverUrl', 'methodPath')):
            abort(400)

        opcua_server_url = api_call_params['serverUrl']
        method_path = api_call_params['methodPath']

        if 'params' in api_call_params:
            method_parameter = api_call_params['params']
        else:
            method_parameter = None

        opcua_client = Client(opcua_server_url)

        try:
            opcua_client.connect()
            root_node = opcua_client.get_root_node()
            method = root_node.get_child(method_path)
            if method:
                if type(method_parameter) == list:
                    root_node.call_method(method, *method_parameter)
                if method_parameter:
                    root_node.call_method(method, method_parameter)
                else:
                    root_node.call_method(method)
            else:
                abort(400)
        except Exception as e:
            abort(500)
        finally:
            opcua_client.disconnect()
            return jsonify(
                method=str(method_path),
                status=200
            )


    @app.route(api_version_string + '/part/outstanding', methods=['GET'])
    def parts_group():
        step = request.args.get('step')
        sorting_parameter = request.args.get('sorting')
        # Timeout for longpolling requests in ms
        lp_timeout = request.args.get('lpTimeout')
        if lp_timeout:
            lp_exp_timestamp = datetime.datetime.now() + datetime.timedelta(milliseconds=int(lp_timeout))

        if step is None or sorting_parameter is None:
            abort(400)

        try:
            if ',' in sorting_parameter:
                sort_by = sorting_parameter.split(',')
                sort_by_criteria = list(map(lambda criterion: get_attribute(criterion), sort_by))
            else:
                sort_by_criteria = [getattr(Part, sorting_parameter)]
        except AttributeError:
            abort(400)

        # Select parts with outstanding production steps, multiple criteria will be joined together using and
        # See also http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.filter_by
        result = Part.query.join(Part.production_steps) \
            .filter_by(status='outstanding', name=step) \
            .order_by(*sort_by_criteria).all()
        result_json = list(map(lambda part: part.to_dict(), result))

        if lp_timeout:
            # While not reached timeout for long polling, check every 0.2 seconds for new data
            while datetime.datetime.now() < lp_exp_timestamp:
                lp_result = Part.query.join(Part.production_steps) \
                    .filter_by(status='outstanding', name=step) \
                    .order_by(*sort_by_criteria).all()
                lp_result_json = list(map(lambda part: part.to_dict(), lp_result))

                if result_json != lp_result_json:
                    result_json = lp_result_json
                    break

                time.sleep(0.2)

        return jsonify(
            num_results=len(result),
            objects=result_json,
            page=1,
            total_pages=1
        )


    @app.route(api_version_string + '/part/finished', methods=['GET'])
    def parts_group_finished():
        step = request.args.get('step')
        sorting_parameter = request.args.get('sorting')

        if step is None or sorting_parameter is None:
            abort(400)

        try:
            if ',' in sorting_parameter:
                sort_by = sorting_parameter.split(',')
                sort_by_criteria = list(map(lambda criterion: get_attribute(criterion), sort_by))
            else:
                sort_by_criteria = [getattr(Part, sorting_parameter)]
        except AttributeError:
            abort(400)
        # Select parts with finished production steps, multiple criteria will be joined together using and
        # See also http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.filter_by
        result = Part.query.join(Part.production_steps) \
            .filter_by(status='finished', name=step) \
            .order_by(*sort_by_criteria).all()
        result_json = list(map(lambda part: part.to_dict(), result))

        return jsonify(
            num_results=len(result),
            objects=result_json,
            page=1,
            total_pages=1
        )


    def get_attribute(criterion):
        try:
            return getattr(Part, criterion)
        except AttributeError:
            return getattr(ProductionStep, criterion)


    cors = CORS(app)

    # start the flask loop
    app.run(host=webservice_conf['webserver']['hostname'],
            port=int(webservice_conf['webserver']['port']),
            threaded=True)
