# Ice Pick

A Python library that allows easy access to AWS billing data collected by the Netflix OSS Ice tool.


## Installation

**TODO**


## Getting Started

Using ice_pick is simple.  Once you have an instance of the Netflix OSS Ice application configured for your AWS account, you can just import the APIRequest, point to your Ice url, and start querying.

### Getting the Summary Table Data

	from ice_pick.api import APIRequest
	
	ice_url = 'http://example.com/ice/'  # URL to your Ice instance
	api_request = APIRequest(ice_url)
	data = api_request.get_data()
	
	print data
	
	{
		u'data': {
			u'AWS Data Pipeline': [0.25148882999999966],
	  		u'Alexa Web Information Service': [0.11130000000000001],
	  		u'aggregated': [48884.90918908445],
	  		u'cloudfront': [3241.575401989994],
			.
			.
			.
	  		u'vpc': [296.7824844800026]
	  	},
	  	u'groupBy': u'Product',
		u'hours': [588],
		u'start': 1391212800000,
	 	u'stats': {
	 		u'AWS Data Pipeline': {
	 			u'average': 0.25148882999999966,
	   			u'max': 0.25148882999999966,
	   			u'total': 0.25148882999999966
	   		},
	   		u'Alexa Web Information Service': {
	   			u'average': 0.11130000000000001,
				u'max': 0.11130000000000001,
				u'total': 0.11130000000000001
			},
			u'aggregated': {
				u'average': 48884.90918908445,
				u'max': 48884.90918908445,
				u'total': 48884.90918908445
			},
			u'cloudfront': {
				u'average': 3241.575401989994,
				u'max': 3241.575401989994,
				u'total': 3241.575401989994
			},
			.
			.
			.
			u'vpc': {
				u'average': 296.7824844800026,
				u'max': 296.7824844800026,
	   			u'total': 296.7824844800026
	   		}
	   	},
		u'status': 200,
		u'time': [1391212800000]
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
		u'data': {
			u'aggregated': [27643.726958229963],
			u'ec2': [1663.472958229997],
			u'ec2_instance': [25980.253999999964]
		},
		u'groupBy': u'Product',
		u'hours': [588],
		u'start': 1391212800000,
		u'stats': {
			u'aggregated': {
				u'average': 27643.726958229963,
				u'max': 27643.726958229963,
				u'total': 27643.726958229963
			},
			u'ec2': {
				u'average': 1663.472958229997,
				u'max': 1663.472958229997,
				u'total': 1663.472958229997
			},
			u'ec2_instance': {
				u'average': 25980.253999999964,
				u'max': 25980.253999999964,
				u'total': 25980.253999999964
			}
		},
		u'status': 200,
		u'time': [1391212800000]
	}

### Filtering by Regions

	from ice_pick.filters import regions as _regions
	regions = [_regions.US_WEST_1, _regions.US_WEST_2]
	api_request.set_products(regions)
	data = api_request.get_data()
	
	print data
	
	{
		u'data': {
			u'aggregated': [3901.7434038699694],
			u'ec2': [100.57340387000029],
			u'ec2_instance': [3801.169999999969]
		},
		u'groupBy': u'Product',
		u'hours': [588],
		u'start': 1391212800000,
		u'stats': {
			u'aggregated': {
				u'average': 3901.7434038699694,
				u'max': 3901.7434038699694,
				u'total': 3901.7434038699694
			},
			u'ec2': {
				u'average': 100.57340387000029,
				u'max': 100.57340387000029,
			   u'total': 100.57340387000029
			},
			u'ec2_instance': {
				u'average': 3801.169999999969,
				u'max': 3801.169999999969,
				u'total': 3801.169999999969
			}
		},			
		u'status': 200,
		u'time': [1391212800000]
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

	