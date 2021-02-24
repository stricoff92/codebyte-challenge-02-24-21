
from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework import status

from .base_test_case import BaseTestBase
from api.lib.policy_data import api_wrapper


class TestPolicyData(BaseTestBase):

    def setUp(self):

        self.mock_fetch_data = patch.object(api_wrapper, 'fetch_data').start()
        self.mock_fetch_data.return_value = [
            {"deductible":5000, "stop_loss":6000, "oop_max":5000} for i in range(3)
        ]

        self.mock_check_for_cached_response = patch.object(api_wrapper, 'check_for_cached_response').start()
        self.mock_check_for_cached_response.return_value = None

        self.mock_set_cached_response = patch.object(api_wrapper, 'set_cached_response').start()
        self.mock_set_cached_response.return_value = None

        super().setUp()


    def tearDown(self):
        self.mock_fetch_data.stop()
        self.mock_check_for_cached_response.stop()
        self.mock_set_cached_response.stop()
        super().tearDown()


    def test_anonymous_user_cannot_access_policy_data(self):
        url = reverse("policy-data")

        # Anonymous user gets a 403
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Logged in user does not get a 403
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_member_id_query_parameter_is_required(self):
        self.client.force_login(self.user)
        url = reverse("policy-data")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'member_id is required'})


    def test_member_id_query_parameter_must_be_castable_to_an_int(self):
        self.client.force_login(self.user)
        url = reverse("policy-data")

        response = self.client.get(url + "?member_id=foobar")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'invalid member_id'})

        response = self.client.get(url + "?member_id=25")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_policy_data_with_unknown_strategy(self):
        self.client.force_login(self.user)
        url = reverse("policy-data")

        response = self.client.get(url + "?member_id=25&coalesce_strategy=foobar_strategy")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error':'unknown coalesce_strategy'})


    def test_get_policy_data_with_average_coalesce_strategy(self):
        self.mock_fetch_data.return_value = [
            {"deductible":1000, "stop_loss":6000, "oop_max":5000},
            {"deductible":2000, "stop_loss":7000, "oop_max":8000},
            {"deductible":3000, "stop_loss":12000, "oop_max":7000},
        ]
        self.client.force_login(self.user)
        url = reverse("policy-data")

        response = self.client.get(url + "?member_id=25&coalesce_strategy=average_strategy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.round_float(response.data['deductible']),
            self.round_float(2000.0)
        )
        self.assertEqual(
            self.round_float(response.data['stop_loss']),
            self.round_float(8333.3333)
        )
        self.assertEqual(
            self.round_float(response.data['oop_max']),
            self.round_float(6666.6667)
        )


    def test_get_policy_data_with_max_coalesce_strategy(self):
        self.mock_fetch_data.return_value = [
            {"deductible":1000, "stop_loss":6000, "oop_max":5000},
            {"deductible":2000, "stop_loss":7000, "oop_max":8000},
            {"deductible":3000, "stop_loss":12000, "oop_max":7000},
        ]
        self.client.force_login(self.user)
        url = reverse("policy-data")

        response = self.client.get(url + "?member_id=25&coalesce_strategy=max_strategy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.round_float(response.data['deductible']),
            self.round_float(3000.0)
        )
        self.assertEqual(
            self.round_float(response.data['stop_loss']),
            self.round_float(12000.0)
        )
        self.assertEqual(
            self.round_float(response.data['oop_max']),
            self.round_float(8000.0)
        )


    def test_cache_is_set_when_calculating_policy_data(self):
        self.mock_fetch_data.return_value = [
            {"deductible":1000, "stop_loss":6000, "oop_max":5000},
            {"deductible":2000, "stop_loss":7000, "oop_max":8000},
            {"deductible":3000, "stop_loss":12000, "oop_max":7000},
        ]
        self.client.force_login(self.user)
        url = reverse("policy-data")
        member_id = 25

        response = self.client.get(url + f"?member_id={member_id}&coalesce_strategy=max_strategy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.mock_set_cached_response.assert_called_once_with(
            member_id, "max_strategy", {'deductible': 3000, 'stop_loss': 12000, 'oop_max': 8000})

