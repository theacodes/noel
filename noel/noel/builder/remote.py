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

"""Utilities for working with the remote builder."""

from noel.kubernetes import KubernetesError
from noel.utils import call


def get_ingress_ip(k8s, service_name):
    """Gets the public IP address of the service that maps to the remote
    builder."""
    service = k8s.get_service(service_name)

    try:
        return service['status']['loadBalancer']['ingress'][0]['ip']
    except KeyError:
        raise KubernetesError(
            'Service {} does not have an external load balancer.'.format(
                service_name))


def add_git_remote(remote_name, remote_url):
    """Adds a given remote to the repository in the current directory."""
    call(
        'git',
        'remote',
        'add',
        remote_name,
        remote_url)


def add_builder_git_remote(k8s, app, remote_name):
    """Adds the remote builder as a git remote to the repository in the current
    directory."""
    ip = get_ingress_ip(k8s, 'builder')
    port = 2122
    user = 'git'
    url = 'ssh://{}@{}:{}/{}'.format(user, ip, port, app)
    add_git_remote(remote_name, url)
