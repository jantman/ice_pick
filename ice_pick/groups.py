"""
ice_pick.groups
~~~~~~~~~~~~~~~~

This module implements the Ice Pick API for managing Application Groups.
"""

import requests as _requests
import re
import json
import datetime
from collections import defaultdict
import urlparse as _urlparse
from exceptions import APIRequestException
from api import APIRequest
from filters import group_by as _group_by

# Set default logging handler to avoid "No handler found" warnings.
import logging
try: # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class Groups(object):
    """
    Class to manage Netflix Ice Application Groups.

    :param ice_host: hostname or IP address of Ice instance
    :type ice_host: string
    :param logger: the logger instance to log to
    :type logger: logging.Logger
    :param dry_run: if true, do not make any *changes* via API, only report on status
      and what would be done
    :type dry_run: boolean
    """

    url_re = re.compile(r'^https?://\S+/$')

    def __init__(self, ice_url, dry_run=False):
        """
        Query and manage Ice Application and Resource Groups.

        :param ice_url: base URL to your Ice instance. It must include\
        "http" or "https://" and end with "/".
        :type ice_url: str or unicode
        :param dry_run: if True, don't actually change anything in Ice,
        just log what would be done (default False).
        :type dry_run: boolean
        """
        self.dry_run = dry_run
        self.ice_url = ice_url
        self.auth = None
        if not self.url_re.match(ice_url):
            raise ValueError("ice_url must match {re}".format(re=self.url_re.pattern))
        if self.dry_run:
            logger.warning("DRY RUN only - will not make any changes")

    def set_http_auth(self, auth):
        """
        Set the value of the optional 'auth' parameter on
        requests.post calls to get data. See
        http://docs.python-requests.org/en/latest/user/authentication/
        for more information.

        :param auth: requests module auth parameter
        :type auth: mixed
        """
        self.auth = auth

    def _ice_get(self, path):
        """
        Perform a GET request against Ice, for the given path/URL.
        Return the decoded data.

        :param path: the path (relative to ice_url) to GET
        :type path: string
        :returns: decoded JSON data dict
        :rtype: dict
        :raises: exceptions.APIRequestException
        """
        url = _urlparse.urljoin(self.ice_url + 'dashboard/', path)
        logger.debug("GETing {u}".format(u=url))
        res = _requests.get(url, auth=self.auth)
        if res.status_code != 200:
            raise APIRequestException('GET', url, res.status_code)
        resp = res.json()
        if resp['status'] != 200:
            raise APIRequestException('GET', url, resp['status'])
        if 'data' in resp:
            return resp['data']
        return {}

    def _ice_post(self, path, params):
        """
        Perform a POST request against Ice, for the given path/URL, with the given params.
        Return the decoded data.

        :param path: the path (relative to ice_url) to POST to
        :type path: string
        :param params: dict of POST data
        :type params: dict
        :returns: decoded JSON response data dict
        :rtype: dict
        :raises: exceptions.APIRequestException
        """
        url = _urlparse.urljoin(self.ice_url + 'dashboard/', path)
        if self.dry_run:
            logger.warning("DRY RUN: Would POST to {u}: {p}".format(u=url, p=params))
            return
        logger.debug("POSTing to {u}: {p}".format(u=url, p=params))
        res = _requests.post(url, data=json.dumps(params), auth=self.auth)
        if res.status_code != 200:
            raise APIRequestException('POST', url, res.status_code)
        resp = res.json()
        if resp['status'] != 200:
            raise APIRequestException('POST', url, resp['status'])
        if 'data' in resp:
            return resp['data']
        return {}

    def get_account_names(self):
        """
        Get a list of all configured AWS account names

        :returns: list of account names
        :rtype: list of strings
        """
        return [x['name'] for x in self._ice_get('getAccounts?')]

    def get_regions_for_account(self, accounts):
        """
        Get a list of AWS region names for the given account.

        :param accounts: list of account names, as returned in ``get_account_names()``
        :type accounts: list of strings
        :returns: list of regions for the account
        :rtype: list of strings
        """
        if not isinstance(accounts, list):
            raise TypeError("accounts parameter must be a list of strings")
        return [r['name'] for r in self._ice_get('getRegions?account={acct}'.format(acct='%2C'.join(accounts)))]

    def get_all_resource_groups(self, accounts, regions, products):
        """
        Get all Resource Group names from Ice.
        This is a wrapper arouns 

        :param accounts: list of account names, as returned in ``get_account_names()``
        :type accounts: list of strings
        :param regions: list of regions to get resource groups for
        :type regions: list of strings
        :param products: list of product names to get resource groups for
        :type products: list of strings
        :returns: list of resource group names
        :rtype: list of strings
        """
        if not isinstance(accounts, list):
            raise TypeError("accounts parameter must be a list of strings")
        url = 'getResourceGroups?account={acct}&product={products}&region={regions}'.format(
            acct='%2C'.join(accounts),
            regions='%2C'.join(regions),
            products='%2C'.join(products)
        )
        return [g['name'] for g in self._ice_get(url)]

    def get_products(self, accounts, regions):
        """
        Get a list of product name strings for the given account and region.

        :param accounts: list of account names, as returned in ``get_account_names()``
        :type accounts: list of strings
        :param regions: regions to query data for
        :type regions: list of strings
        :returns: list of product names
        :rtype: list of strings
        """
        if not isinstance(accounts, list):
            raise TypeError("accounts parameter must be a list of strings")
        path = 'getProducts?account={acct}&region={regions}&showResourceGroups=true'.format(
            acct='%2C'.join(accounts),
            regions='%2C'.join(regions)
        )
        return [r['name'] for r in self._ice_get(path)]

    def get_resource_group_lists(self):
        """
        Return a dict of Ice products (string) to their possible resource groups (list of strings).

        :returns: dict of Ice products (string) to their possible resource groups (list of strings)
        :rtype: dict
        """
        resp = self._ice_get('getResourceGroupLists?')
        result = {}
        for item in resp:
            result[item['product']['name']] = [r['name'] for r in item['data']]
        return result

    def delete_application_group(self, name):
        """
        Delete the specified application group.

        :param name: name of the application group to delete
        :type name: string
        """
        url = 'deleteApplicationGroup?name={name}'.format(name=name)
        if self.dry_run:
            logger.warning("Would GET {u}".format(u=url))
            return
        self._ice_get(url)

    def get_application_group_names(self):
        """
        Return a list of the names of all current Application Groups.

        :rtype: list of strings
        """
        end_dt = datetime.datetime.utcnow()
        start_dt = end_dt - datetime.timedelta(weeks=4)
        req = APIRequest(self.ice_url)
        if self.auth:
            req.set_http_auth(self.auth)
        req.set_aggregate('stats')
        req.set_group_by(_group_by.APPLICATION_GROUP)
        req.set_end(end_dt)
        req.set_start(start_dt)
        result = req.get_data()
        names = [k for k in result['stats']]
        return names

    def get_application_group(self, group_name):
        """
        Get the configuration for the specified Application Group.

        Returns a dict with keys:
        'name' -> string name of group
        'owner' -> string email address of group owner/contact
        'products' -> dict of product name (string) to list of Resource Group names (string) for product

        :param group_name: name of the application group to get
        :type group_name: string
        :rtype: dict
        """
        res = self._ice_get('getApplicationGroup?name={name}'.format(name=group_name))
        group = {}
        group['name'] = res['name']
        group['owner'] = res['owner']
        group['products'] = {}
        for prodname, prodlist in res['data'].iteritems():
            group['products'][prodname] = [x['name'] for x in prodlist]
        return group

    def set_application_group(self, group_name, resource_groups, group_email):
        """
        Create or update an Application Group.

        :param group_name: the name of the group to update
        :type group_name: string
        :param group_email: the owner/contact email for the group
        :type group_email: string
        :param resource_groups: dict of product name to Resource Groups for the product, like the 'products' item in the ``get_application_group()`` return dict
        :type resource_groups: dict of string keys, list of string values
        :returns: Ice POST response data
        :rtype: dict
        """
        params = {"name":group_name, "owner":group_email, "data": resource_groups}
        if self.dry_run:
            logger.warning("DRY_RUN: would POST to /saveApplicationGroup with data: {d}".format(d=params))
            return
        logger.info("POSTing to /saveApplicationGroup with data: {d}".format(d=params))
        res = self._ice_post('saveApplicationGroup', params)
        return res
