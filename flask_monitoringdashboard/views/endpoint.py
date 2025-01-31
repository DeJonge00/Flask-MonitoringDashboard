from flask import jsonify, request, json

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.controllers.endpoints import get_endpoint_overview, get_api_performance, \
    set_endpoint_rule, get_endpoint_versions, get_endpoint_users, get_host_performance
from flask_monitoringdashboard.core.auth import secure, admin_secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope, row2dict
from flask_monitoringdashboard.database.host import get_host_hits
from flask_monitoringdashboard.database.endpoint import get_users, get_ips, get_endpoints, get_endpoints_hits, \
    get_endpoint_by_name


@blueprint.route('/api/overview')
@secure
def get_overview():
    """
    Get information per endpoint about the number of hits and median execution time
    :return: A JSON-list with a JSON-object per endpoint
    """
    with session_scope() as db_session:
        return jsonify(get_endpoint_overview(db_session))


@blueprint.route('/api/users/<endpoint_id>')
@secure
def users(endpoint_id):
    """
    :param endpoint_id: integer
    :return: A JSON-list with all users of a specific endpoint (user represented by a string)
    """
    with session_scope() as db_session:
        users_hits = get_users(db_session, endpoint_id)
        dicts = []
        for uh in users_hits:
            dicts.append({'user': uh[0], 'hits': uh[1]})
        return jsonify(dicts)


@blueprint.route('/api/ip/<endpoint_id>')
@secure
def ips(endpoint_id):
    """
    :param endpoint_id: integer
    :return: A JSON-list with all IP-addresses of a specific endpoint (ip represented by a string)
    """
    with session_scope() as db_session:
        ips_hits = get_ips(db_session, endpoint_id)
        dicts = []
        for ih in ips_hits:
            dicts.append({'ip': ih[0], 'hits': ih[1]})
        return jsonify(dicts)


@blueprint.route('/api/endpoints')
@secure
def endpoints():
    """
    :return: A JSON-list with information about every endpoint (encoded in a JSON-object)
        For more information per endpoint, see :func: get_overview
    """
    with session_scope() as db_session:
        return jsonify([row2dict(row) for row in get_endpoints(db_session)])


@blueprint.route('/api/endpoints_hits')
@secure
def endpoints_hits():
    """
    :return: A JSON-list with information about every endpoint and its total number of hits (encoded in a JSON-object)
        For more information per endpoint, see :func: get_overview
    """
    with session_scope() as db_session:
        end_hits = get_endpoints_hits(db_session)
        dicts = []
        for et in end_hits:
            dicts.append({'name': et[0], 'hits': et[1]})
        return jsonify(dicts)


@blueprint.route('/api/api_performance', methods=['POST'])
@secure
def api_performance():
    """
    input must be a JSON-object, with the following value: {
          'data': {
            'endpoints': ['endpoint', 'endpoint2']
          }
        }
    :return: A JSON-list for every endpoint with the following JSON-object: {
          'name': 'endpoint',
          'values': [100, 101, 102, ...]
        }
    """
    data = json.loads(request.data)['data']
    endpoints = data['endpoints']

    with session_scope() as db_session:
        return jsonify(get_api_performance(db_session, endpoints))


@blueprint.route('/api/host_hits')
@secure
def host_hits():
    """
    :return: A JSON-list with information about every host and its total number of hits (encoded in a JSON-object)
        For more information per endpoint, see :func: get_overview
    """
    with session_scope() as db_session:
        host_hits = get_host_hits(db_session)
        dicts = []
        for et in host_hits:
            dicts.append({'name': et[0], 'hits': et[1]})
        return jsonify(dicts)


@blueprint.route('/api/host_performance', methods=['POST'])
@secure
def host_performance():
    """
    input must be a JSON-object, with the following value: {
          'data': {
            'ids': [id1, id2],
            'endpoints': [endpoint1, endpoint2]
          }
        }
    :return: A JSON-list for every endpoint with the following JSON-object: {
          'name': 'hostname',
          'id': hostid,
          'values': [100, 101, 102, ...]
        }
    """

    data = json.loads(request.data)['data']
    host_ids = data['ids']

    with session_scope() as db_session:
        endpoints = [get_endpoint_by_name(db_session, name).id for name in data['endpoints']]
        return jsonify(get_host_performance(db_session, host_ids, endpoints))


@blueprint.route('/api/set_rule', methods=['POST'])
@admin_secure
def set_rule():
    """
        The data from the form is validated and processed, such that the required rule is monitored
    """
    endpoint_name = request.form['name']
    value = int(request.form['value'])
    with session_scope() as db_session:
        set_endpoint_rule(db_session, endpoint_name, value)
    return 'OK'


@blueprint.route('/api/endpoint_info/<endpoint_id>')
@secure
def endpoint_info(endpoint_id):
    """
    :return: A JSON-object with endpoint details, such as:
        - color: hashed color of the endpoint,
        - endpoint: endpoint-name
        - id: endpoint id
        - methods: HTTP methods (encoded as a JSON-list)
        - monitor-level: monitor level for this endpoint
        - rules: all rules for this endpoint (encoded as a JSON-list)
        - total_hits: number of hits
        - url: link to this endpoint
    """
    with session_scope() as db_session:
        return jsonify(get_endpoint_details(db_session, endpoint_id))


@blueprint.route('/api/endpoint_versions/<endpoint_id>', methods=['POST'])
@secure
def endpoint_versions(endpoint_id):
    with session_scope() as db_session:
        data = json.loads(request.data)['data']
        versions = data['versions']
        return jsonify(get_endpoint_versions(db_session, endpoint_id, versions))


@blueprint.route('/api/endpoint_users/<endpoint_id>', methods=['POST'])
@secure
def endpoint_users(endpoint_id):
    with session_scope() as db_session:
        data = json.loads(request.data)['data']
        users = data['users']
        return jsonify(get_endpoint_users(db_session, endpoint_id, users))
