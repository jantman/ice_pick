# Ice Pick

A Python library that allows easy access to AWS billing data collected by the Netflix OSS Ice tool.


## Installation

    pip install ice-pick

## Getting Started

Using ice_pick is simple.  Once you have an instance of the Netflix OSS Ice application configured for your AWS account, you can just import the APIRequest, point to your Ice url, and start querying.

### Getting the Summary Table Data

    from ice_pick.api import APIRequest
    
    ice_url = 'http://example.com/ice/'  # URL to your Ice instance
    api_request = APIRequest(ice_url)
    data = api_request.get_data()
    
    print data
    
    {
        'data': {
            'AWS Data Pipeline': [0.25148882999999966],
            'Alexa Web Information Service': [0.11130000000000001],
            'aggregated': [48884.90918908445],
            'cloudfront': [3241.575401989994],
            .
            .
            .
            'vpc': [296.7824844800026]
        },
        'groupBy': 'Product',
        'hours': [588],
        'start': 1391212800000,
        'stats': {
            'AWS Data Pipeline': {
                'average': 0.25148882999999966,
                'max': 0.25148882999999966,
                'total': 0.25148882999999966
            },
            'Alexa Web Information Service': {
                'average': 0.11130000000000001,
                'max': 0.11130000000000001,
                'total': 0.11130000000000001
            },
            'aggregated': {
                'average': 48884.90918908445,
                'max': 48884.90918908445,
                'total': 48884.90918908445
            },
            'cloudfront': {
                'average': 3241.575401989994,
                'max': 3241.575401989994,
                'total': 3241.575401989994
            },
            .
            .
            .
            'vpc': {
                'average': 296.7824844800026,
                'max': 296.7824844800026,
                'total': 296.7824844800026
                }
            },
        'status': 200,
        'time': [1391212800000]
    }

By default **ice-pick** uses the following filters:

    {
        'aggregate': 'data',
        'breakdown': True,
        'consolidate': 'monthly',
        'end': '2014-02-25 08PM',
        'factorsps': False,
        'groupBy': 'Product',
        'isCost': True,
        'showsps': False,
        'start': '2014-02-01 12AM'
    }
    
The *start* and *end* dates are based on current (UTC) time by default.

### Filtering by Products

    from ice_pick.filters import products as _products
    products = [_products.EC2, _products.EC2_INSTANCE]
    api_request.set_products(products)
    data = api_request.get_data()
    
    print data
    
    {
        'data': {
            'aggregated': [27643.726958229963],
            'ec2': [1663.472958229997],
            'ec2_instance': [25980.253999999964]
        },
        'groupBy': 'Product',
        'hours': [588],
        'start': 1391212800000,
        'stats': {
            'aggregated': {
                'average': 27643.726958229963,
                'max': 27643.726958229963,
                'total': 27643.726958229963
            },
            'ec2': {
                'average': 1663.472958229997,
                'max': 1663.472958229997,
                'total': 1663.472958229997
            },
            'ec2_instance': {
                'average': 25980.253999999964,
                'max': 25980.253999999964,
                'total': 25980.253999999964
            }
        },
        'status': 200,
        'time': [1391212800000]
    }

### Filtering by Regions

    from ice_pick.filters import regions as _regions
    regions = [_regions.US_WEST_1, _regions.US_WEST_2]
    api_request.set_products(regions)
    data = api_request.get_data()
    
    print data
    
    {
        'data': {
            'aggregated': [3901.7434038699694],
            'ec2': [100.57340387000029],
            'ec2_instance': [3801.169999999969]
        },
        'groupBy': 'Product',
        'hours': [588],
        'start': 1391212800000,
        'stats': {
            'aggregated': {
                'average': 3901.7434038699694,
                'max': 3901.7434038699694,
                'total': 3901.7434038699694
            },
            'ec2': {
                'average': 100.57340387000029,
                'max': 100.57340387000029,
               'total': 100.57340387000029
            },
            'ec2_instance': {
                'average': 3801.169999999969,
                'max': 3801.169999999969,
                'total': 3801.169999999969
            }
        },            
        'status': 200,
        'time': [1391212800000]
    }
    
    
    
### More Filters

    # Filtering by date time
    import datetime
    start = datetime.datetime(2014, 01, 01)
    end = datetime.datetime.now()
    
    api_request.set_start(start)
    api_request.set_end(start)
    
    
    # Filtering by Usage Type
    from ice_pick.filters import usage_types as _usage_types
    usage_types = [_usage_types.LOAD_BALANCER_USAGE, _usage_types.M1_XLARGE]
    
    api_request.set_usage_types(usage_types)
    

### Initializing And Overriding Default Filtering

You can pass all the filters you want to apply at the moment you initialize the APIRequest.

    from ice_pick.filters import consolidate as _consolidate
    from ice_pick.filters import group_by as _group_by
    from ice_pick.filters import operations as _operations

    filters = {
        APIFilters.ACCOUNTS: ['012345678900', '009876543210'],
        APIFilters.REGIONS: [_regions.US_WEST_1, _regions.US_WEST_2],
        APIFilters.BREAKDOWN: True,
        APIFilters.CONSOLIDATE: _consolidate.MONTHLY,
        APIFilters.FACTOR_SPS: False,
        APIFilters.GROUP_BY: _group_by.PRODUCT,
        APIFilters.IS_COST: True,
        APIFilters.OPERATIONS: [_operations.CREATE_BUCKET, _operations.CREATE_SNAPSHOT],
        APIFilters.SHOW_SPS: False,
        APIFilters.USAGE_TYPES: USAGE_TYPES
        .
        .
        .
    }

    api_request = APIRequest(ice_url, **filters)


### Getting The Current Filters

You can check which filters were active on the last request, and which filters will be used for the next request.

    api_request.get_filters()

    
## License

Copyright 2014 Demand Media

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
