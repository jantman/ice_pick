import unittest
from mock import patch, call, Mock, MagicMock
import datetime
from ice_pick import utils
from ice_pick.exceptions import APIRequestException
from ice_pick import api
from ice_pick.api import APIRequest, APIFilters
from ice_pick.groups import Groups
import logging
from contextlib import nested
from ice_pick.filters import group_by as _group_by
from freezegun import freeze_time


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

    def test_set_http_auth(self):
        api_request = APIRequest(self.dummy_ice_url)
        self.assertEquals(api_request.auth, None)
        api_request.set_http_auth(('foo', 'bar'))
        self.assertEquals(api_request.auth, ('foo', 'bar'))

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

@patch('ice_pick.groups.logger', spec_set=logging.Logger)
@patch('ice_pick.groups._requests')
@patch('ice_pick.groups.Groups._ice_get')
@patch('ice_pick.groups.Groups._ice_post')
class TestGroups(unittest.TestCase):

    def setUp(self):
        self.dummy_ice_url = 'http://foo.com/'

    def test_init(self, mock_post, mock_get, mock_requests, mock_logger):
        g = Groups(self.dummy_ice_url)
        self.assertEquals(g.ice_url, self.dummy_ice_url)
        self.assertEquals(g.dry_run, False)
        self.assertEquals(g.auth, None)
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [])

    def test_init_bad_url(self, mock_post, mock_get, mock_requests, mock_logger):
        self.assertRaises(ValueError, Groups, 'foobar')
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [])

    def test_init_dry_run(self, mock_post, mock_get, mock_requests, mock_logger):
        g = Groups(self.dummy_ice_url, dry_run=True)
        self.assertEquals(g.dry_run, True)
        self.assertEquals(mock_logger.mock_calls,
                          [call.warning('DRY RUN only - will not make any changes')]
        )
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [])

    def test_set_auth(self, mock_post, mock_get, mock_requests, mock_logger):
        m = Mock()
        g = Groups(self.dummy_ice_url)
        g.set_http_auth(m)
        self.assertEquals(g.ice_url, self.dummy_ice_url)
        self.assertEquals(g.dry_run, False)
        self.assertEquals(g.auth, m)
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [])

    def test_get_account_names(self, mock_post, mock_get, mock_requests, mock_logger):
        mock_get.return_value = [
            {'name': '1234'},
            {'name': '5678'}
        ]
        g = Groups(self.dummy_ice_url, dry_run=False)
        res = g.get_account_names()
        self.assertEquals(mock_logger.mock_calls,
                          []
        )
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call('getAccounts?')])
        self.assertEquals(mock_post.mock_calls, [])
        self.assertEquals(res, ['1234', '5678'])

    def test_get_regions_for_account(self, mock_post, mock_get, mock_requests, mock_logger):
        mock_get.return_value = [
            {"name":"ap-northeast-1"},
            {"name":"us-east-1"},
            {"name":"us-west-2"}
        ]
        g = Groups(self.dummy_ice_url, dry_run=False)
        res = g.get_regions_for_account(['123456', '7890'])
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call('getRegions?account=123456%2C7890')])
        self.assertEquals(mock_post.mock_calls, [])
        self.assertEquals(res, ["ap-northeast-1", "us-east-1", "us-west-2"])

    def test_get_all_resource_groups(self, mock_post, mock_get, mock_requests, mock_logger):
        mock_get.return_value = [
            {"name":"tag1_tagA"},
            {"name":"tag2_tagA"},
            {"name":"tag1_tagB"},
            {"name":"tag2_tagB"},
        ]
        url = 'getResourceGroups?account=23456%2C7890&product=ec2%2Cs3%2Crds&region=us-east-1%2Cus-west-2'
        g = Groups(self.dummy_ice_url, dry_run=False)
        res = g.get_all_resource_groups(['23456', '7890'], ['us-east-1', 'us-west-2'], ['ec2', 's3', 'rds'])
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call(url)])
        self.assertEquals(mock_post.mock_calls, [])
        self.assertEquals(res, ["tag1_tagA", "tag2_tagA", "tag1_tagB", "tag2_tagB"])

    def test_get_products(self, mock_post, mock_get, mock_requests, mock_logger):
        mock_get.return_value = [
            {"name":"cloudfront"},
            {"name":"cloudwatch"},
            {"name":"ebs"},
        ]
        url = 'getProducts?account=1234%2C23456&region=us-east-1%2Cus-west-2&showResourceGroups=true'
        g = Groups(self.dummy_ice_url, dry_run=False)
        res = g.get_products(['1234', '23456'], ['us-east-1', 'us-west-2'])
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call(url)])
        self.assertEquals(mock_post.mock_calls, [])
        self.assertEquals(res, ["cloudfront", "cloudwatch", "ebs"])

    def test_get_resource_group_lists(self, mock_post, mock_get, mock_requests, mock_logger):
        mock_get.return_value = [
            {
                "product": { "name": "vpc" },
                "data": []
            },
            {
                "product": { "name":"rds" },
                "data":[
                    {"name":"tag1_tagA"},
                    {"name":"tag2_tagA"},
                    {"name":"tag1_tagB"},
                    {"name":"tag2_tagB"},
                ]
            },
            {
                "product": { "name":"ebs" },
                "data":[
                    {"name":"tag1_tagA"},
                    {"name":"tag2_tagA"},
                    {"name":"tag1_tagB"},
                    {"name":"tag2_tagB"},
                ]
            },
        ]
        url = 'getResourceGroupLists?'
        expected = {
            "vpc": [],
            "rds": [
                "tag1_tagA",
                "tag2_tagA",
                "tag1_tagB",
                "tag2_tagB",
            ],
            "ebs": [
                "tag1_tagA",
                "tag2_tagA",
                "tag1_tagB",
                "tag2_tagB",
            ],
        }

        g = Groups(self.dummy_ice_url, dry_run=False)
        res = g.get_resource_group_lists()
        self.assertEquals(mock_logger.mock_calls,
                          []
        )
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call(url)])
        self.assertEquals(mock_post.mock_calls, [])
        self.assertEquals(res, expected)

    def test_get_application_group(self, mock_post, mock_get, mock_requests, mock_logger):
        mock_get.return_value = {
            "name": "AppGroup",
            "owner": "nobody@example.com",
            "data": {
                "cloudwatch": [
                    {"name":"tag1_tagA"},
                    {"name":"tag2_tagA"},
                    {"name":"tag1_tagB"},
                    {"name":"tag2_tagB"},
                ],
                "ec2": [
                    {"name":"tag1_tagB"},
                    {"name":"tag2_tagB"},
                ],
                "ebs": [
                    {"name":"tag1_tagA"},
                    {"name":"tag2_tagA"},
                ],
            },
        }
        url = 'getApplicationGroup?name=foobar'
        g = Groups(self.dummy_ice_url, dry_run=False)
        res = g.get_application_group('foobar')
        self.assertEquals(mock_logger.mock_calls,
                          []
        )
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call(url)])
        self.assertEquals(mock_post.mock_calls, [])
        self.assertEquals(res, {
            'name': 'AppGroup',
            'owner': 'nobody@example.com',
            'products': {
                "cloudwatch": ["tag1_tagA", "tag2_tagA", "tag1_tagB", "tag2_tagB"],
                "ec2": ["tag1_tagB", "tag2_tagB"],
                "ebs": [ "tag1_tagA", "tag2_tagA"],
            }
        })

    def test_set_application_group(self, mock_post, mock_get, mock_requests, mock_logger):
        products = {
            "cloudwatch": ["tag1_tagA", "tag2_tagA", "tag1_tagB", "tag2_tagB"],
            "ec2": ["tag1_tagB", "tag2_tagB"],
            "ebs": [ "tag1_tagA", "tag2_tagA"],
        }
        params = {'owner': 'foo@example.com', 'name': 'MyName', 'data': products}

        g = Groups(self.dummy_ice_url, dry_run=False)
        g.set_application_group('MyName', products, 'foo@example.com')
        self.assertEquals(mock_logger.mock_calls, [
            call.info("POSTing to /saveApplicationGroup with data: {'owner': "
                      "'foo@example.com', 'data': {'ec2': ['tag1_tagB', 'tag2_tagB'],"
                      " 'cloudwatch': ['tag1_tagA', 'tag2_tagA', 'tag1_tagB', "
                      "'tag2_tagB'], 'ebs': ['tag1_tagA', 'tag2_tagA']},"
                      " 'name': 'MyName'}")
        ])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [
            call('saveApplicationGroup', params)
        ])

    def test_set_application_group_dry_run(self, mock_post, mock_get, mock_requests, mock_logger):
        products = {
            "cloudwatch": ["tag1_tagA", "tag2_tagA", "tag1_tagB", "tag2_tagB"],
            "ec2": ["tag1_tagB", "tag2_tagB"],
            "ebs": [ "tag1_tagA", "tag2_tagA"],
        }
        params = {'owner': 'foo@example.com', 'name': 'MyName', 'data': products}

        g = Groups(self.dummy_ice_url, dry_run=True)
        mock_logger.reset_mock()
        g.set_application_group('MyName', products, 'foo@example.com')
        self.assertEquals(mock_logger.mock_calls, [
            call.warning("DRY_RUN: would POST to /saveApplicationGroup with data: {'owner': "
                      "'foo@example.com', 'data': {'ec2': ['tag1_tagB', 'tag2_tagB'],"
                      " 'cloudwatch': ['tag1_tagA', 'tag2_tagA', 'tag1_tagB', "
                      "'tag2_tagB'], 'ebs': ['tag1_tagA', 'tag2_tagA']},"
                      " 'name': 'MyName'}")
        ])
        self.assertEquals(mock_requests.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [])

    def test_delete_application_group_dry_run(self, mock_post, mock_get, mock_requests, mock_logger):
        groups = Groups(self.dummy_ice_url, dry_run=True)
        mock_logger.reset_mock()
        groups.delete_application_group('foo')
        self.assertEquals(mock_logger.mock_calls,
                          [call.warning('Would GET deleteApplicationGroup?name=foo')]
        )
        self.assertEquals(mock_get.mock_calls, [])
        self.assertEquals(mock_post.mock_calls, [])

    def test_delete_application_group(self, mock_post, mock_get, mock_requests, mock_logger):
        groups = Groups(self.dummy_ice_url, dry_run=False)
        mock_logger.reset_mock()
        groups.delete_application_group('foo')
        self.assertEquals(mock_logger.mock_calls, [])
        self.assertEquals(mock_get.mock_calls, [call('deleteApplicationGroup?name=foo')])
        self.assertEquals(mock_post.mock_calls, [])


@patch('ice_pick.groups.logger', spec_set=logging.Logger)
@patch('ice_pick.groups._requests')
class TestGroupsRequests(unittest.TestCase):

    def test_ice_get(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 200, "data": ["foo","bar"] }
        mock_requests.get.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        res = g._ice_get('foobar')
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug('GETing http://foo.com/dashboard/foobar')]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.get('http://foo.com/dashboard/foobar', auth=None),
            call.get().json()
        ])
        self.assertEquals(res, ['foo', 'bar'])

    def test_ice_get_auth(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 200, "data": ["foo","bar"] }
        mock_requests.get.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        g.set_http_auth(('myuser', 'mypass'))
        mock_logger.reset_mock()
        res = g._ice_get('foobar')
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug('GETing http://foo.com/dashboard/foobar')]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.get('http://foo.com/dashboard/foobar', auth=('myuser', 'mypass')),
            call.get().json()
        ])
        self.assertEquals(res, ['foo', 'bar'])

    def test_ice_get_request_error(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=502)
        mock_requests.get.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        self.assertRaises(APIRequestException,
                          g._ice_get,
                          'foobar')
        self.assertEquals(mock_logger.mock_calls, [call.debug('GETing http://foo.com/dashboard/foobar')])
        self.assertEquals(mock_requests.mock_calls, [call.get('http://foo.com/dashboard/foobar', auth=None)])

    def test_ice_get_response_error(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 503, "data": ["foo","bar"] }
        mock_requests.get.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        self.assertRaises(APIRequestException,
                          g._ice_get,
                          'foobar')
        self.assertEquals(mock_logger.mock_calls, [call.debug('GETing http://foo.com/dashboard/foobar')])
        self.assertEquals(mock_requests.mock_calls, [
            call.get('http://foo.com/dashboard/foobar', auth=None),
            call.get().json()
        ])

    def test_ice_get_no_data(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 200}
        mock_requests.get.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        res = g._ice_get('foobar')
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug('GETing http://foo.com/dashboard/foobar')]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.get('http://foo.com/dashboard/foobar', auth=None),
            call.get().json()
        ])
        self.assertEquals(res, {})

    def test_ice_post(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 200}
        mock_requests.post.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        res = g._ice_post('foobar', {'baz': 'blam'})
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug("POSTing to http://foo.com/dashboard/foobar: {'baz': 'blam'}")]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.post('http://foo.com/dashboard/foobar', data='{"baz": "blam"}', auth=None),
            call.post().json()
        ])
        self.assertEquals(res, {})

    def test_ice_post_auth(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 200}
        mock_requests.post.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        g.set_http_auth(('myuser', 'mypass'))
        mock_logger.reset_mock()
        res = g._ice_post('foobar', {'baz': 'blam'})
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug("POSTing to http://foo.com/dashboard/foobar: {'baz': 'blam'}")]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.post('http://foo.com/dashboard/foobar', data='{"baz": "blam"}', auth=('myuser', 'mypass')),
            call.post().json()
        ])
        self.assertEquals(res, {})

    def test_ice_post_dry_run(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'

        g = Groups('http://foo.com/', dry_run=True)
        mock_logger.reset_mock()
        res = g._ice_post('foobar', {'baz': 'blam'})
        self.assertEquals(mock_logger.mock_calls,
                          [call.warning("DRY RUN: Would POST to http://foo.com/dashboard/foobar: {'baz': 'blam'}")]
        )
        self.assertEquals(mock_requests.mock_calls, [])

    def test_ice_post_request_error(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=404)
        mock_requests.post.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        self.assertRaises(APIRequestException,
                          g._ice_post,
                          'foobar',
                          {'baz': 'blam'}
        )
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug("POSTing to http://foo.com/dashboard/foobar: {'baz': 'blam'}")]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.post('http://foo.com/dashboard/foobar', data='{"baz": "blam"}', auth=None)
        ])

    def test_ice_post_response_error(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 403}
        mock_requests.post.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        self.assertRaises(APIRequestException,
                          g._ice_post,
                          'foobar',
                          {'baz': 'blam'}
        )
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug("POSTing to http://foo.com/dashboard/foobar: {'baz': 'blam'}")]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.post('http://foo.com/dashboard/foobar', data='{"baz": "blam"}', auth=None),
            call.post().json()
        ])

    def test_ice_post_data(self, mock_requests, mock_logger):
        url = 'http://foo.com/dashboard/foobar'
        mock_result = Mock(status_code=200)
        mock_result.json.return_value = {"status": 200, "data": {'foo': 'bar'}}
        mock_requests.post.return_value = mock_result

        g = Groups('http://foo.com/', dry_run=False)
        mock_logger.reset_mock()
        res = g._ice_post('foobar', {'baz': 'blam'})
        self.assertEquals(mock_logger.mock_calls,
                          [call.debug("POSTing to http://foo.com/dashboard/foobar: {'baz': 'blam'}")]
        )
        self.assertEquals(mock_requests.mock_calls, [
            call.post('http://foo.com/dashboard/foobar', data='{"baz": "blam"}', auth=None),
            call.post().json()
        ])
        self.assertEquals(res, {'foo': 'bar'})

    @freeze_time('2015-04-10 05:00:00')
    def test_get_application_group_names(self, mock_requests, mock_logger):
        mock_api = Mock()
        with patch('ice_pick.groups.APIRequest', spec_set=APIRequest) as mock_api_constr:
            mock_api_constr.return_value = mock_api
            mock_api.get_data.return_value = {'foo': {'bar': 'baz'}, 'blam': {'blarg': 'quux'}}
            g = Groups('http://foo.com/', dry_run=False)
            res = g.get_application_group_names()
        self.assertEqual(mock_api_constr.mock_calls[0], call('http://foo.com/'))
        self.assertEqual(mock_api.mock_calls, [
            call.set_aggregate('stats'),
            call.set_group_by(_group_by.APPLICATION_GROUP),
            call.set_end(datetime.datetime(2015, 4, 10, 5, 0)),
            call.set_start(datetime.datetime(2015, 3, 13, 5, 0)),
            call.get_data(),
        ])
        self.assertEqual(res, ['foo', 'blam'])
        self.assertEqual(mock_logger.mock_calls, [])

if __name__ == '__main__':
    unittest.main()
