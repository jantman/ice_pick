import unittest
from mock import patch
import datetime
from ice_pick import utils
from ice_pick.exceptions import APIRequestException
from ice_pick import api
from ice_pick.api import APIRequest, APIFilters


class TestUtils(unittest.TestCase):
    def test_format_datetime(self):
        '''Tests that the datetime formatter utils function returns the right
        format.
        '''
        utcnow = datetime.datetime.utcnow()
        datetime_format = '%Y-%m-%d %I%p'
        self.assertEquals(utcnow.strftime(datetime_format),
                          utils.format_datetime(utcnow))


class TestAPIFilters(unittest.TestCase):
    def test_filter_keys(self):
        '''Tests the name of the filter keys.'''
        self.assertEquals(APIFilters.ACCOUNTS, 'account')
        self.assertEquals(APIFilters.AGGREGATE, 'aggregate')
        self.assertEquals(APIFilters.BREAKDOWN, 'breakdown')
        self.assertEquals(APIFilters.CONSOLIDATE, 'consolidate')
        self.assertEquals(APIFilters.END, 'end')
        self.assertEquals(APIFilters.FACTOR_SPS, 'factorsps')
        self.assertEquals(APIFilters.GROUP_BY, 'groupBy')
        self.assertEquals(APIFilters.IS_COST, 'isCost')
        self.assertEquals(APIFilters.OPERATIONS, 'operation')
        self.assertEquals(APIFilters.PRODUCTS, 'product')
        self.assertEquals(APIFilters.REGIONS, 'region')
        self.assertEquals(APIFilters.SHOW_SPS, 'showsps')
        self.assertEquals(APIFilters.START, 'start')
        self.assertEquals(APIFilters.USAGE_TYPES, 'usageType')

    def test_types(self):
        '''Tests the types of the filters.'''
        types = APIFilters.TYPES
        self.assertEquals(types[APIFilters.ACCOUNTS], list)
        self.assertEquals(types[APIFilters.AGGREGATE], str)
        self.assertEquals(types[APIFilters.BREAKDOWN], bool)
        self.assertEquals(types[APIFilters.CONSOLIDATE], str)
        self.assertEquals(types[APIFilters.END], datetime.datetime)
        self.assertEquals(types[APIFilters.FACTOR_SPS], bool)
        self.assertEquals(types[APIFilters.GROUP_BY], str)
        self.assertEquals(types[APIFilters.IS_COST], bool)
        self.assertEquals(types[APIFilters.OPERATIONS], list)
        self.assertEquals(types[APIFilters.PRODUCTS], list)
        self.assertEquals(types[APIFilters.REGIONS], list)
        self.assertEquals(types[APIFilters.SHOW_SPS], bool)
        self.assertEquals(types[APIFilters.START], datetime.datetime)
        self.assertEquals(types[APIFilters.USAGE_TYPES], list)

    def test_default_filters(self):
        '''Tests the default filters key/value.'''
        utcnow = datetime.datetime.utcnow()
        start = datetime.datetime(utcnow.year, utcnow.month, 1)
        default_key_value = {
            APIFilters.IS_COST: True,
            APIFilters.AGGREGATE: 'data',
            APIFilters.GROUP_BY: 'Product',
            APIFilters.CONSOLIDATE: 'monthly',
            APIFilters.START: utils.format_datetime(start),
            APIFilters.END: utils.format_datetime(utcnow),
            APIFilters.BREAKDOWN: True,
            APIFilters.SHOW_SPS: False,
            APIFilters.FACTOR_SPS: False,
        }
        assert APIFilters.default_filters() == default_key_value


class TestAPIRequest(unittest.TestCase):
    api_request = None
    dummy_ice_url = None
    dummy_list = None
    dummy_string = None
    dummy_datetime = None

    def setUp(self):
        self.dummy_ice_url = 'http://foo.com'
        self.api_request = APIRequest(self.dummy_ice_url)
        self.dummy_list = ['012345678900', '009876543210']
        self.dummy_str = 'foo'
        self.dummy_datetime = datetime.datetime.utcnow()

    def _join_list(self, value_list):
        return ','.join(value_list)

    def test_api_request_filter(self):
        is_cost = False
        dummy_filter = 'foo_bar'
        dummy_value = ['foo', 'bar']
        filters = {
            APIFilters.ACCOUNTS: self.dummy_list,
            APIFilters.IS_COST: is_cost,
            dummy_filter: dummy_value,
        }
        api_request = APIRequest(self.dummy_ice_url, **filters)
        request_filters = api_request.get_filters()
        self.assertEquals(request_filters[APIFilters.ACCOUNTS],
                          self._join_list(self.dummy_list))
        self.assertEquals(request_filters[APIFilters.IS_COST], is_cost)
        self.assertEquals(request_filters[dummy_filter], dummy_value)

    def _test_set_list(self, fn, filter_name):
        # Type error exception test
        self.assertRaises(TypeError,
                          fn,
                          self.dummy_str)
        # Filter value test
        fn(self.dummy_list)
        self.assertEquals(self.api_request.get_filters()[filter_name],
                          self._join_list(self.dummy_list))

    def _test_set_str(self, fn, filter_name):
        # Type error exception test
        self.assertRaises(TypeError, fn, [])
        # Filter value test
        fn(self.dummy_str)
        self.assertEquals(self.api_request.get_filters()[filter_name],
                          self.dummy_str)

    def _test_set_bool(self, fn, filter_name, value):
        # Type error exception test
        self.assertRaises(TypeError, fn, self.dummy_str)
        # Filter value test
        fn(value)
        self.assertEquals(self.api_request.get_filters()[filter_name], value)

    def _test_set_datetime(self, fn, filter_name):
        # Type error exception test
        self.assertRaises(TypeError, fn, self.dummy_str)
        # Filter value test
        fn(self.dummy_datetime)
        self.assertEquals(self.api_request.get_filters()[filter_name],
                          utils.format_datetime(self.dummy_datetime))

    def test_set_accounts(self):
        '''Tests set_accounts function exception and filter results'''
        self._test_set_list(self.api_request.set_accounts, APIFilters.ACCOUNTS)

    def test_set_aggregate(self):
        '''Tests set_aggregate function exception and filter results'''
        self._test_set_str(self.api_request.set_aggregate,
                           APIFilters.AGGREGATE)

    def test_set_breakdown(self):
        '''Tests set_breakdown function exception and filter results'''
        self._test_set_bool(self.api_request.set_breakdown,
                            APIFilters.BREAKDOWN, False)

    def test_set_consolidate(self):
        '''Tests set_consolidate function exception and filter results'''
        self._test_set_str(self.api_request.set_consolidate,
                           APIFilters.CONSOLIDATE)

    def test_set_end(self):
        '''Tests set_end function exception and filter results'''
        self._test_set_datetime(self.api_request.set_end, APIFilters.END)

    def test_set_factor_sps(self):
        '''Tests set_factor_sps function exception and filter results'''
        self._test_set_bool(self.api_request.set_factor_sps,
                            APIFilters.FACTOR_SPS, True)

    def test_set_group_by(self):
        '''Tests set_group_by function exception and filter results'''
        self._test_set_str(self.api_request.set_group_by,
                           APIFilters.GROUP_BY)

    def test_set_is_cost(self):
        '''Tests set_is_cost function exception and filter results'''
        self._test_set_bool(self.api_request.set_is_cost,
                            APIFilters.IS_COST, False)

    def test_set_operations(self):
        '''Tests set_operations function exception and filter results'''
        self._test_set_list(self.api_request.set_operations,
                            APIFilters.OPERATIONS)

    def test_set_products(self):
        '''Tests set_products function exception and filter results'''
        self._test_set_list(self.api_request.set_products,
                            APIFilters.PRODUCTS)

    def test_set_regions(self):
        '''Tests set_regions function exception and filter results'''
        self._test_set_list(self.api_request.set_regions,
                            APIFilters.REGIONS)

    def test_set_show_sps(self):
        '''Tests set_show_sps function exception and filter results'''
        self._test_set_bool(self.api_request.set_show_sps,
                            APIFilters.SHOW_SPS, True)

    def test_set_start(self):
        '''Tests set_start function exception and filter results'''
        self._test_set_datetime(self.api_request.set_start, APIFilters.START)

    def test_set_usage_types(self):
        '''Tests set_usage_types function exception and filter results'''
        self._test_set_list(self.api_request.set_usage_types,
                            APIFilters.USAGE_TYPES)

    def test_get_data(self):
        '''Tests the get_data function by mocking the requests.post'''
        class MockResponse():
            def __init__(self, status_code):
                self.status_code = status_code

            @property
            def content(self):
                return '''{
                    "data": {},
                    "groupBy": {},
                    "interval": 3600000,
                    "start": 1380585600000,
                    "stats": {},
                    "status": 200
                }'''

        with patch.object(api, '_requests') as mock_request:
            # Testing that if the post request comes back with a status_code
            # different than 200, the function get_data will raise an
            # APIRequestException.
            mock_request.post.return_value = MockResponse(500)
            self.assertRaises(APIRequestException, self.api_request.get_data)

            # Testing that if the post request status_code is 200, the function
            # get_data will return a dictionary.
            mock_request.post.return_value = MockResponse(200)
            self.assertTrue(isinstance(self.api_request.get_data(), dict))


if __name__ == '__main__':
    unittest.main()
