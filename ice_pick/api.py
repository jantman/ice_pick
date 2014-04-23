"""
ice_pick.api
~~~~~~~~~~~~

This module implements the Ice Pick API.

Copyright 2014 Demand Media.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""


import datetime
import json as _json
import urlparse as _urlparse
import requests as _requests
import exceptions as _exceptions
import utils as _utils
from filters import group_by as _group_by, consolidate as _consolidate


class APIFilters(object):
    ACCOUNTS = 'account'
    AGGREGATE = 'aggregate'
    BREAKDOWN = 'breakdown'
    CONSOLIDATE = 'consolidate'
    END = 'end'
    FACTOR_SPS = 'factorsps'
    GROUP_BY = 'groupBy'
    IS_COST = 'isCost'
    OPERATIONS = 'operation'
    PRODUCTS = 'product'
    REGIONS = 'region'
    SHOW_SPS = 'showsps'
    START = 'start'
    USAGE_TYPES = 'usageType'

    # Filter key type map
    TYPES = {
        ACCOUNTS: list,
        AGGREGATE: str,
        BREAKDOWN: bool,
        CONSOLIDATE: str,
        END: datetime.datetime,
        FACTOR_SPS: bool,
        GROUP_BY: str,
        IS_COST: bool,
        OPERATIONS: list,
        PRODUCTS: list,
        REGIONS: list,
        SHOW_SPS: bool,
        START: datetime.datetime,
        USAGE_TYPES: list,
    }

    @classmethod
    def default_filters(cls):
        end_datetime = datetime.datetime.utcnow()
        start_datetime = datetime.datetime(end_datetime.year,
                                           end_datetime.month, 1)
        return {
            cls.AGGREGATE: 'data',
            cls.BREAKDOWN: True,
            cls.CONSOLIDATE: _consolidate.MONTHLY,
            cls.START: _utils.format_datetime(start_datetime),
            cls.END: _utils.format_datetime(end_datetime),
            cls.FACTOR_SPS: False,
            cls.GROUP_BY: _group_by.PRODUCT,
            cls.IS_COST: True,
            cls.SHOW_SPS: False,
        }


class APIRequest(object):
    '''Handles Ice "scraping" as and API.'''
    # Ice monitoring base URL
    ice_use = None
    # Current filters to be apply or already applied
    _filters = None
    # Last data fetch from Ice
    _data = None

    def __init__(self, ice_url, **filters):
        ''':params ice_url: base URL to your Ice instance. It must include\
        "http" or "https://" and end with "/".
        :type ice_url: str or unicode.
        '''
        self.ice_url = ice_url
        self._filters = APIFilters.default_filters()
        self._set_filters(**filters)

    def _set_filters(self, **filters):
        for filter_key, value in filters.iteritems():
            if not filter_key in APIFilters.TYPES:
                self._filters[filter_key] = value
                continue
            self._set_one_filter(filter_key, value)

    def _set_one_filter(self, filter_key, value):
        filter_type = APIFilters.TYPES[filter_key]
        fn = None
        if filter_type == list:
            fn = self._set_filter_list
        elif filter_type == bool:
            fn = self._set_filter_bool
        elif filter_type == datetime.datetime:
            fn = self._set_filter_datetime
        else:
            fn = self._set_filter_str
        fn(filter_key, value)

    def _set_filter_list(self, filter_key, value_list):
        if isinstance(value_list, list):
            self._filters[filter_key] = ','.join(value_list)
        else:
            raise TypeError('Parameter %s must be a list.' % filter_key)

    def _set_filter_bool(self, filter_key, value):
        if isinstance(value, bool):
            self._filters[filter_key] = value
        else:
            raise TypeError('Parameter %s must be a boolean.' % filter_key)

    def _set_filter_datetime(self, filter_key, value):
        if isinstance(value, datetime.datetime):
            self._filters[filter_key] = _utils.format_datetime(value)
        else:
            raise TypeError('Parameter %s must be a datetime.' % filter_key)

    def _set_filter_str(self, filter_key, value):
        if isinstance(value, str):
            self._filters[filter_key] = value
        else:
            raise TypeError('Parameter %s must be a string.' % filter_key)

    def set_accounts(self, account_list):
        '''Parses the account list and adds it to the filters'''
        self._set_one_filter(APIFilters.ACCOUNTS, account_list)

    def set_aggregate(self, aggregate):
        self._set_one_filter(APIFilters.AGGREGATE, aggregate)

    def set_breakdown(self, breakdown):
        self._set_one_filter(APIFilters.BREAKDOWN, breakdown)

    def set_consolidate(self, consolidate):
        self._set_one_filter(APIFilters.CONSOLIDATE, consolidate)

    def set_end(self, end):
        self._set_one_filter(APIFilters.END, end)

    def set_factor_sps(self, factor_sps):
        self._set_one_filter(APIFilters.FACTOR_SPS, factor_sps)

    def set_group_by(self, group_by):
        self._set_one_filter(APIFilters.GROUP_BY, group_by)

    def set_is_cost(self, is_cost):
        self._set_one_filter(APIFilters.IS_COST, is_cost)

    def set_operations(self, operation_list):
        '''Parses the operation list and adds it to the filters'''
        self._set_one_filter(APIFilters.OPERATIONS, operation_list)

    def set_products(self, product_list):
        '''Parses the product list and adds it to the filters'''
        self._set_one_filter(APIFilters.PRODUCTS, product_list)

    def set_regions(self, region_list):
        '''Parses the region list and adds it to the filters'''
        self._set_one_filter(APIFilters.REGIONS, region_list)

    def set_show_sps(self, show_sps):
        self._set_one_filter(APIFilters.SHOW_SPS, show_sps)

    def set_start(self, start):
        self._set_one_filter(APIFilters.START, start)

    def set_usage_types(self, usage_type_list):
        '''Parses the usage type list and adds it to the filters'''
        self._set_one_filter(APIFilters.USAGE_TYPES, usage_type_list)

    def get_filters(self):
        ''' Returns a copy of the current API filters.'''
        return self._filters.copy()

    def get_data(self):
        '''Fetches data from Ice and returns it as a dictonary'''
        request_url = _urlparse.urljoin(self.ice_url, 'dashboard/getData')
        data_filters = _json.dumps(self._filters)
        headers = {
            'content-type': 'application/json;charset=utf-8'
        }
        r = _requests.post(request_url, data=data_filters, headers=headers)
        status_code = r.status_code
        if status_code == 200:
            response = r.content
            data = _json.loads(response)
            return data
        raise _exceptions.APIRequestException('POST', request_url,
                                              status_code)
