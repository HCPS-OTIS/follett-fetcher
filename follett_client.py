#!/usr/bin/env python

import json, requests, time

class DestinyClient(object):
    access_token = {'expires': 0}

    def __init__(self, config):
        self.BASE_URL = config.BASE_URL
        self.CLIENT_ID = config.CLIENT_ID
        self.CLIENT_SECRET = config.CLIENT_SECRET

    def _get_access_token(self):
        """
        Gets a new access token using credentials from initial config
        """
        req = requests.request('POST', self.BASE_URL + 'auth/accessToken', data={
            'grant_type': 'client_credentials',
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        })

        req_body = json.loads(req.content)
        req_body['expires'] = time.time() + req_body['expires_in']

        return req_body

    def _refresh_access_token(self):
        """
        Checks to see if credentials are expired and refreshes them if so
        """
        if self.access_token['expires'] < time.time() + 10:
            self.access_token = self._get_access_token()

    def _valid_access_headers(self):
        """
        Returns valid headers for an authenticated request
        """
        self._refresh_access_token()
        return { 'Authorization': 'Bearer ' + self.access_token['access_token'] }

    def _make_api_call(self, path):
        """
        Makes an API call using valid headers, parses the output JSON, and throws errors
        """
        r = requests.get(self.BASE_URL + path, headers=self._valid_access_headers())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            r.raise_for_status()

    def get_fines(self):
        """
        Get all fines from Destiny
        """
        return self._make_api_call('fines')

    def get_items(self):
        """
        Get the first page of items from Destiny
        """
        return self._make_api_call('materials/resources/items')

    def get_next_page(self, previous_page):
        """
        Get the page after the provided page from Destiny
        """
        return self._make_api_call('materials' + previous_page['@nextLink'])