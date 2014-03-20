"""
ice_pick.utils
~~~~~~~~~~~~~~

This module implements contains utility funcitons used by Ice Pick API.

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


def format_datetime(datetime_value):
    date_format = '%Y-%m-%d %I%p'
    return datetime_value.strftime(date_format)
