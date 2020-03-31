from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
from tests.helpers import get_controller_mock
from napps.kytos.maintenance.main import Main
from napps.kytos.maintenance.models import MaintenanceWindow as MW

TIME_FMT = "%Y-%m-%dT%H:%M:%S"


class TestMain(TestCase):
    """Test the Main class of this NApp."""

    def setUp(self):
        """Initialization before tests are executed."""
        self.server_name_url = \
            'http://localhost:8181/api/kytos/maintenance'
        self.napp = Main(get_controller_mock())
        self.api = self.get_app_test_client(self.napp)

    @staticmethod
    def get_app_test_client(napp):
        """Return a flask api test client."""
        napp.controller.api_server.register_napp_endpoints(napp)
        return napp.controller.api_server.app.test_client()

    @patch('napps.kytos.maintenance.models.Scheduler.add')
    @patch('napps.kytos.maintenance.models.MaintenanceWindow.from_dict')
    def test_create_mw_case_1(self, from_dict_mock, sched_add_mock):
        """Test a successful case of the REST to create a maintenance
        window
        """
        url = f'{self.server_name_url}'
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        from_dict_mock.return_value.id = '1234'
        from_dict_mock.return_value.start = start
        from_dict_mock.return_value.end = end
        from_dict_mock.return_value.items = [
            "00:00:00:00:00:00:02",
            MagicMock(interface=MagicMock(), tag=MagicMock())
        ]
        payload = {
            "start": start.strftime(TIME_FMT),
            "end": end.strftime(TIME_FMT),
            "items": [
                {
                    "interface_id": "00:00:00:00:00:00:00:03:3",
                    "tag": {
                        "tag_type": "VLAN",
                        "value": 241
                    }
                },
                "00:00:00:00:00:00:02"
            ]
        }
        response = self.api.post(url, data=json.dumps(payload),
                                 content_type='application/json')
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(current_data, {'mw_id': '1234'})
        sched_add_mock.assert_called_once_with(from_dict_mock.return_value)

    @patch('napps.kytos.maintenance.models.Scheduler.add')
    @patch('napps.kytos.maintenance.models.MaintenanceWindow.from_dict')
    def test_create_mw_case_2(self, from_dict_mock, sched_add_mock):
        """Test a fail case of the REST to create a maintenance window"""
        url = f'{self.server_name_url}'
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        from_dict_mock.return_value = None
        payload = {
            "start": start.strftime(TIME_FMT),
            "end": end.strftime(TIME_FMT),
            "items": [
                {
                    "interface_id": "00:00:00:00:00:00:00:03:3",
                    "tag": {
                        "tag_type": "VLAN",
                        "value": 241
                    }
                },
                "00:00:00:00:00:00:02"
            ]
        }
        response = self.api.post(url, data=json.dumps(payload),
                                 content_type='application/json')
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(current_data, 'One or more items are invalid')
        sched_add_mock.assert_not_called()

    @patch('napps.kytos.maintenance.models.Scheduler.add')
    @patch('napps.kytos.maintenance.models.MaintenanceWindow.from_dict')
    def test_create_mw_case_3(self, from_dict_mock, sched_add_mock):
        """Test a fail case of the REST to create a maintenance window"""
        url = f'{self.server_name_url}'
        start = datetime.now() - timedelta(days=1)
        end = start + timedelta(hours=2)
        from_dict_mock.return_value.id = '1234'
        from_dict_mock.return_value.start = start
        from_dict_mock.return_value.end = end
        from_dict_mock.return_value.items = [
            "00:00:00:00:00:00:02",
            MagicMock(interface=MagicMock(), tag=MagicMock())
        ]
        payload = {
            "start": start.strftime(TIME_FMT),
            "end": end.strftime(TIME_FMT),
            "items": [
                {
                    "interface_id": "00:00:00:00:00:00:00:03:3",
                    "tag": {
                        "tag_type": "VLAN",
                        "value": 241
                    }
                },
                "00:00:00:00:00:00:02"
            ]
        }
        response = self.api.post(url, data=json.dumps(payload),
                                 content_type='application/json')
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(current_data, 'Start in the past not allowed')
        sched_add_mock.assert_not_called()

    @patch('napps.kytos.maintenance.models.Scheduler.add')
    @patch('napps.kytos.maintenance.models.MaintenanceWindow.from_dict')
    def test_create_mw_case_4(self, from_dict_mock, sched_add_mock):
        """Test a fail case of the REST to create a maintenance window"""
        url = f'{self.server_name_url}'
        start = datetime.now() + timedelta(days=1)
        end = start - timedelta(hours=2)
        from_dict_mock.return_value.id = '1234'
        from_dict_mock.return_value.start = start
        from_dict_mock.return_value.end = end
        from_dict_mock.return_value.items = [
            "00:00:00:00:00:00:02",
            MagicMock(interface=MagicMock(), tag=MagicMock())
        ]
        payload = {
            "start": start.strftime(TIME_FMT),
            "end": end.strftime(TIME_FMT),
            "items": [
                {
                    "interface_id": "00:00:00:00:00:00:00:03:3",
                    "tag": {
                        "tag_type": "VLAN",
                        "value": 241
                    }
                },
                "00:00:00:00:00:00:02"
            ]
        }
        response = self.api.post(url, data=json.dumps(payload),
                                 content_type='application/json')
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(current_data, 'End before start not allowed')
        sched_add_mock.assert_not_called()

    @patch('napps.kytos.maintenance.models.MaintenanceWindow.as_dict')
    def test_get_mw_case_1(self, mw_as_dict_mock):
        """Test get all maintenance windows, empty list"""
        url = f'{self.server_name_url}'
        response = self.api.get(url)
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_data, [])
        mw_as_dict_mock.assert_not_called()

    @patch('napps.kytos.maintenance.models.MaintenanceWindow.as_dict')
    def test_get_mw_case_2(self, mw_as_dict_mock):
        """Test get all maintenance windows"""
        start1 = datetime.now() + timedelta(days=1)
        end1 = start1 + timedelta(hours=6)
        start2 = datetime.now() + timedelta(hours=5)
        end2 = start2 + timedelta(hours=1, minutes=30)
        self.napp.maintenances = {
            '1234': MW(start1, end1, items=[
                '00:00:00:00:00:00:12:23'
            ]),
            '4567': MW(start2, end2, items=[
                '12:34:56:78:90:ab:cd:ef'
            ])
        }
        mw_dict = [
            {
                'id': '1234',
                'start': start1.strftime(TIME_FMT),
                'end': end1.strftime(TIME_FMT),
                'items': [
                    '00:00:00:00:00:00:12:23'
                ]
            },
            {
                'id': '4567',
                'start': start2.strftime(TIME_FMT),
                'end': end2.strftime(TIME_FMT),
                'items': [
                    '12:34:56:78:90:ab:cd:ef'
                ]
            }
        ]
        mw_as_dict_mock.side_effect = mw_dict
        url = f'{self.server_name_url}'
        response = self.api.get(url)
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_data, mw_dict)
        self.assertEqual(mw_as_dict_mock.call_count, 2)

    @patch('napps.kytos.maintenance.models.MaintenanceWindow.as_dict')
    def test_get_mw_case_3(self, mw_as_dict_mock):
        """Test get non-existent id"""
        start1 = datetime.now() + timedelta(days=1)
        end1 = start1 + timedelta(hours=6)
        start2 = datetime.now() + timedelta(hours=5)
        end2 = start2 + timedelta(hours=1, minutes=30)
        self.napp.maintenances = {
            '1234': MW(start1, end1, items=[
                '00:00:00:00:00:00:12:23'
            ]),
            '4567': MW(start2, end2, items=[
                '12:34:56:78:90:ab:cd:ef'
            ])
        }
        url = f'{self.server_name_url}/2345'
        response = self.api.get(url)
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(current_data, {'response': 'Maintenance with id 2345 '
                                                    'not found'})
        mw_as_dict_mock.assert_not_called()

    @patch('napps.kytos.maintenance.models.MaintenanceWindow.as_dict')
    def test_get_mw_case_4(self, mw_as_dict_mock):
        """Test get existent id"""
        start1 = datetime.now() + timedelta(days=1)
        end1 = start1 + timedelta(hours=6)
        start2 = datetime.now() + timedelta(hours=5)
        end2 = start2 + timedelta(hours=1, minutes=30)
        self.napp.maintenances = {
            '1234': MW(start1, end1, items=[
                '00:00:00:00:00:00:12:23'
            ]),
            '4567': MW(start2, end2, items=[
                '12:34:56:78:90:ab:cd:ef'
            ])
        }
        mw_dict = {
            'id': '4567',
            'start': start2.strftime(TIME_FMT),
            'end': end2.strftime(TIME_FMT),
            'items': [
                '12:34:56:78:90:ab:cd:ef'
            ]
        }
        mw_as_dict_mock.return_value = mw_dict
        url = f'{self.server_name_url}/4567'
        response = self.api.get(url)
        current_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_data, mw_dict)
        mw_as_dict_mock.assert_called_once()
