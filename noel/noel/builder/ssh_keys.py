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

"""Utilities for managing authorized SSH keys for the remote builder.

The remote builer uses SSH keys to identify authorized users. The keys are
stored in a Kubernetes secret.
"""

import yaml

from jinja2 import Template
from pkg_resources import resource_string

from noel.kubernetes import KubernetesError


SSH_KEY_SECRET_TMPL = Template(
    resource_string(__name__, 'resources/ssh-key-secret.tmpl.yaml'))


def ssh_key_secret_template(data, name='ssh-keys'):
    return yaml.load(SSH_KEY_SECRET_TMPL.render(data=data, name=name))


def add_key(k8s, name, key):
    """Creates or updates the Kubernetes secret for authorized SSH keys and
    adds the given key."""

    try:
        existing = k8s.get_secret('ssh-keys')
    except KubernetesError:
        existing = None

    if existing:
        keys = existing['data']
    else:
        keys = {}

    keys[name] = key

    secret = ssh_key_secret_template(keys)

    if existing:
        return k8s.replace_secret(secret)
    else:
        return k8s.create_secret(secret)
