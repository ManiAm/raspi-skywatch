
# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: Generic REST client

import os
import sys
import json
import logging
import requests
import inspect
from dotenv import load_dotenv
import models_redis

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

load_dotenv()


class REST_API_Client():

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=None):

        if not host:
            log.error("host is missing!")
            sys.exit(2)

        if not REST_API_Client.__with_http_prefix(host):
            host_address = f'https://{host}'
        else:
            host_address = host

        if port:
            host_address += f':{port}'

        self.baseurl = f'{host_address}'

        if api_ver:
            self.baseurl += f'/{api_ver}'

        if base:
            self.baseurl += f'/{base}'

        self.user = user

        self.headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }

        access_token = os.getenv('API_TOKEN', None)
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'


    @staticmethod
    def __with_http_prefix(host):

        if host.startswith("http://"):
            return True

        if host.startswith("https://"):
            return True

        return False


    def request(self, method, url, timeout=10, verify=True, stream=False, decode=True, backoff_ttl=30, **kwargs):

        frame = inspect.currentframe()
        key = models_redis.get_key(frame)
        key_error = f"error:{key}"

        cached = models_redis.get_from_cache(key)
        if cached:
            return True, cached

        cached = models_redis.get_from_cache(key_error)
        if cached:
            return False, cached

        status, output = self.__request(method, url, timeout, verify, stream, decode, **kwargs)
        if not status:
            models_redis.set_to_cache(key_error, f"Skipping request to '{url}' for {backoff_ttl} seconds due to recent failure.", ttl=backoff_ttl)
            return False, output

        # Terms of use: API responses must not be stored for more than 24 hours.
        if url.startswith("https://api.planespotters.net"):
            ttl = 86400
        else:
            ttl = None

        models_redis.set_to_cache(key, output, ttl=ttl)

        return True, output


    def __request(self, method, url, timeout, verify, stream, decode, **kwargs):

        try:
            response = requests.request(method,
                                        url,
                                        headers=self.headers,
                                        timeout=timeout,
                                        verify=verify,
                                        stream=stream,
                                        **kwargs)
        except Exception as E:
            return False, str(E)

        try:
            response.raise_for_status()
        except Exception as E:
            return False, f'Return code={response.status_code}, {E}\n{response.text}'

        if stream:
            return True, response

        if not decode:
            return True, response.content

        try:
            content_decoded = response.content.decode('utf-8')
            if not content_decoded:
                return True, {}

            data_dict = json.loads(content_decoded)
        except Exception as E:
            return False, f'Error while decoding content: {E}'

        return True, data_dict
