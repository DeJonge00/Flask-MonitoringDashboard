import datetime

from numpy import median

from flask_monitoringdashboard import config
from flask_monitoringdashboard.core.colors import get_color
from flask_monitoringdashboard.core.measurement import add_decorator
from flask_monitoringdashboard.core.timezone import to_local_datetime, to_utc_datetime
from flask_monitoringdashboard.core.utils import simplify
from flask_monitoringdashboard.database import Request
from flask_monitoringdashboard.database.count_group import count_requests_group, get_value
from flask_monitoringdashboard.database.data_grouped import get_endpoint_data_grouped, get_user_data_grouped, \
    get_version_data_grouped, get_host_data_grouped
from flask_monitoringdashboard.database.endpoint import get_last_requested, get_endpoints, get_endpoint_by_name, \
    update_endpoint
from flask_monitoringdashboard.database.host import get_host_name_by_id
from flask_monitoringdashboard.database.versions import get_first_requests


def get_endpoint_overview(db_session):
    """
    :param db_session: session for the database
    :return: A list of properties for each endpoint that is found in the database
    """
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    now_local = to_local_datetime(datetime.datetime.utcnow())
    today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = to_utc_datetime(today_local)

    hits_today = count_requests_group(db_session, Request.time_requested > today_utc)
    hits_week = count_requests_group(db_session, Request.time_requested > week_ago)
    hits = count_requests_group(db_session)

    median_today = get_endpoint_data_grouped(db_session, median, Request.time_requested > today_utc)
    median_week = get_endpoint_data_grouped(db_session, median, Request.time_requested > week_ago)
    median_overall = get_endpoint_data_grouped(db_session, median)
    access_times = get_last_requested(db_session)

    return [{
        'id': endpoint.id,
        'name': endpoint.name,
        'monitor': endpoint.monitor_level,
        'color': get_color(endpoint.name),
        'hits-today': get_value(hits_today, endpoint.id),
        'hits-week': get_value(hits_week, endpoint.id),
        'hits-overall': get_value(hits, endpoint.id),
        'median-today': get_value(median_today, endpoint.id),
        'median-week': get_value(median_week, endpoint.id),
        'median-overall': get_value(median_overall, endpoint.id),
        'last-accessed': get_value(access_times, endpoint.name, default=None)
    } for endpoint in get_endpoints(db_session)]


def get_endpoint_users(db_session, endpoint_id, users):
    """
    :param db_session: session for the database
    :param endpoint_id: id for the endpoint
    :param users: a list of users to be filtered on
    :return: a list of dicts with the performance of each user
    """
    times = get_user_data_grouped(db_session, lambda x: simplify(x, 100), Request.endpoint_id == endpoint_id)
    first_requests = get_first_requests(db_session, endpoint_id)
    return [{
        'user': u,
        'date': get_value(first_requests, u),
        'values': get_value(times, u),
        'color': get_color(u)
    } for u in users]


def get_endpoint_versions(db_session, endpoint_id, versions):
    """
    :param db_session: session for the database
    :param endpoint_id: id for the endpoint
    :param versions: a list of version to be filtered on
    :return: a list of dicts with the performance of each version
    """
    times = get_version_data_grouped(db_session, lambda x: simplify(x, 100), Request.endpoint_id == endpoint_id)
    first_requests = get_first_requests(db_session, endpoint_id)
    return [{
        'version': v,
        'date': get_value(first_requests, v),
        'values': get_value(times, v),
        'color': get_color(v)
    } for v in versions]


def get_api_performance(db_session, endpoints):
    """
    :param db_session: session for the database
    :param endpoints: a list of endpoints, encoded by their name
    :return: for every endpoint in endpoints, a list with the performance
    """
    db_endpoints = [get_endpoint_by_name(db_session, end) for end in endpoints]
    data = get_endpoint_data_grouped(db_session, lambda x: simplify(x, 10))
    return [{
        'name': end.name,
        'values': get_value(data, end.id, default=[])
    } for end in db_endpoints]


def get_host_performance(db_session, host_ids: [str], endpoint_ids: [str]):
    """
    :param db_session: session for the database
    :param host_ids: a list of hosts, encoded by their id
    :param endpoints: a list of endpoints, encoded by their id
    :return: for every endpoint in endpoints, a list with the performance
    """
    db_host_ids = [(host, get_host_name_by_id(db_session, host)) for host in host_ids]
    data = get_host_data_grouped(db_session, lambda x: x, Request.endpoint_id.in_(endpoint_ids))
    return [{
        'name': name,
        'id': id,
        'values': get_value(data, id, default=[])
    } for (id, name) in db_host_ids]


def set_endpoint_rule(db_session, endpoint_name, monitor_level):
    """
    :param db_session: session for the database
    :param endpoint_name: name of the endpoint
    :param monitor_level: integer, representing the monitoring-level
    :return:
    """
    update_endpoint(db_session, endpoint_name, value=monitor_level)

    # Remove wrapper
    original = getattr(config.app.view_functions[endpoint_name], 'original', None)
    if original:
        config.app.view_functions[endpoint_name] = original
    db_session.commit()

    add_decorator(get_endpoint_by_name(db_session, endpoint_name))
