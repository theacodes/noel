# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is a barebones Kubernetes HTTP API client.

Alternatively, you could use subprocess.call to call out to kubectl.
"""

from base64 import b64decode, b64encode
import json

import requests


class KubernetesError(Exception):
    """Encapsulates an error from the Kubernetes API and allows it to be
    presented in a readable manner to the user."""
    def __init__(self, httperror):
        self.httperror = httperror
        try:
            self.json = httperror.response.json()
        except:
            self.json = {'error': httperror.response.text}
        super(KubernetesError, self).__init__(
            '{}'.format(self.json))


class Kubernetes(object):
    """Kubernetes HTTP API client."""

    def __init__(self, api_root, namespace='default'):
        self._api_root = api_root + '/api/v1'
        self._namespace = namespace

    def _url(self, resource, namespace=None, *args, **kwargs):
        return '{}/namespaces/{}/{}'.format(
            self._api_root,
            namespace or self._namespace,
            resource.format(*args, **kwargs))

    def _wrap_exception(self, r):
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            raise KubernetesError(e)

    def _get(self, resource, *args, **kwargs):
        url = self._url(resource)
        r = requests.get(url, *args, **kwargs)

        self._wrap_exception(r)

        return r.json()

    def _stream(self, resource, *args, **kwargs):
        url = self._url(resource)

        r = requests.get(url, *args, stream=True, **kwargs)

        for line in r.iter_lines():
            yield line

    def _watch(self, resource, *args, **kwargs):
        params = kwargs.pop('params', {})
        params['watch'] = 'true'

        for line in self._stream(resource, *args, params=params, **kwargs):
            yield json.loads(line)

    def _post(self, resource, data, *args, **kwargs):
        url = self._url(resource)
        r = requests.post(url, data=json.dumps(data), *args, **kwargs)

        self._wrap_exception(r)

        return r.json()

    def _put(self, resource, data, *args, **kwargs):
        url = self._url(resource)
        r = requests.put(url, data=json.dumps(data), *args, **kwargs)

        self._wrap_exception(r)

        return r.json()

    def _patch(self, resource, data, *args, **kwargs):
        url = self._url(resource)

        r = requests.patch(
            url,
            data=json.dumps(data),
            headers={'content-type': 'application/merge-patch+json'},
            *args,
            **kwargs)

        self._wrap_exception(r)

        return r.json()

    def _delete(self, resource, *args, **kwargs):
        url = self._url(resource)
        r = requests.delete(url, *args, **kwargs)

        self._wrap_exception(r)

        return r.json()

    def pods(self, *args, **kwargs):
        return self._get('pods', *args, **kwargs)

    def services(self, *args, **kwargs):
        return self._get('services', *args, **kwargs)

    def replicationcontrollers(self, *args, **kwargs):
        return self._get('replicationcontrollers', *args, **kwargs)

    def logs(
            self,
            name,
            container=None,
            follow=None,
            lines=None,
            *args, **kwargs):
        params = kwargs.pop('params', {})

        params.update({
            'container': container,
            'follow': follow,
            'tailLines': lines
        })

        return self._stream(
            'pods/{}/log'.format(name), *args, params=params, **kwargs)

    def get_service(self, name, *args, **kwargs):
        return self._get('services/' + name, *args, **kwargs)

    def create_service(self, spec, *args, **kwargs):
        return self._post('services', spec, *args, **kwargs)

    def create_replicationcontroller(self, spec, *args, **kwargs):
        return self._post('replicationcontrollers', spec, *args, **kwargs)

    def scale(self, name, replicas, *args, **kwargs):
        return self._patch(
            'replicationcontrollers/{}'.format(name),
            {"spec": {"replicas": 0}},
            *args,
            **kwargs)

    def delete_service(self, name, *args, **kwargs):
        return self._delete(
            'services/{}'.format(name),
            *args,
            **kwargs)

    def delete_replicationcontroller(self, name, *args, **kwargs):
        return self._delete(
            'replicationcontrollers/{}'.format(name),
            *args,
            **kwargs)

    def encode_secret_data(self, data):
        """Base64 encodes a dictionary's values.

        Kubernetes expects secret values to be base64 encoded within JSON.
        """
        return {
            k: b64encode(v)
            for k, v in data.iteritems()
        }

    def decode_secret_data(self, data):
        """Base64 decodes a dictionary's values.

        Kubernetes returns secret values encoded in base64.
        """
        return {
            k: b64decode(v)
            for k, v in data.iteritems()
        }

    def get_secret(self, name, *args, **kwargs):
        r = self._get('secrets/' + name, *args, **kwargs)
        r['data'] = self.decode_secret_data(r['data'])
        return r

    def create_secret(self, spec, *args, **kwargs):
        spec['data'] = self.encode_secret_data(spec['data'])
        return self._post('secrets', spec, *args, **kwargs)

    def replace_secret(self, spec, *args, **kwargs):
        name = spec['metadata']['name']
        spec['data'] = self.encode_secret_data(spec['data'])
        return self._put('secrets/{}'.format(name), spec, *args, **kwargs)

    def delete_secret(self, name, *args, **kwargs):
        return self._delete('secrets/{}'.format(name), *args, **kwargs)

    def watch_secrets(self, *args, **kwargs):
        return self._watch('secrets', *args, **kwargs)
