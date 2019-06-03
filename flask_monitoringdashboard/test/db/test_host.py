"""
    This file contains all unit tests for the host-table in the database. (Corresponding to the file:
    'flask_monitoringdashboard/database/host.py')
    See info_box.py for how to run the test-cases.
"""

import unittest

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.count import count_hosts
from flask_monitoringdashboard.test.utils import set_test_environment, clear_db, add_fake_data, NAME, IP


class TestHost(unittest.TestCase):

    def setUp(self):
        set_test_environment()
        clear_db()
        add_fake_data()

    def test_add_host(self):
        """
            Test whether the function returns the right values.
        """
        from flask_monitoringdashboard import config
        from flask_monitoringdashboard.database.host import add_host
        name2 = 'main2'
        self.assertNotEqual(NAME, name2, 'Both cannot be equal, otherwise the test will fail')
        with session_scope() as db_session:
            number_of_hosts = count_hosts(db_session)
            add_host(db_session, config.host_name, IP)
            self.assertEqual(count_hosts(db_session), number_of_hosts + 1)

    def test_hosts(self):
        """
            Test retrieval of all hosts
        """

        from flask_monitoringdashboard.database.host import get_hosts
        with session_scope() as db_session:
            number_of_hosts = count_hosts(db_session)
            self.assertEqual(len(list(get_hosts(db_session))), number_of_hosts)

    def test_get_host_id_by_name(self):
        """
        Tests retrieval of host by name
        """

        from flask_monitoringdashboard.database.host import get_host_id_by_name
        with session_scope() as db_session:
            host = get_host_id_by_name(db_session, 'host1')
            self.assertEqual(host.name, 'host1')