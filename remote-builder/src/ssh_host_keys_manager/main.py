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

"""Manages the SSH host keys for the remote builder.

Because the remote builder can run multiple instances but is behind a single
load balanced public IP, all of the instances need to share the same SSH
identity or git will cry foul when you try to push and get a different instance.

This program ensures that one set of SSH host keys are generated and that all
of the instances use those keys.
"""


import argparse
import os
import sys
from subprocess import check_call
import time

from jinja2 import Template
from noel.kubernetes import Kubernetes, KubernetesError
from noel.logger import logger, setup_logging
import requests
from pkg_resources import resource_string
import yaml


def wait_for_kubernetes(k8s):
    tries = 5
    sys.stdout.write('Waiting for kubeproxy.')
    while True:
        try:
            requests.get(k8s._api_root)
            sys.stdout.write(' done.\n')
            return
        except requests.exceptions.ConnectionError:
            if tries == 0:
                sys.stdout.write(' failed.\n')
                sys.exit(1)
            tries -= 1
            sys.stdout.write('.')
            time.sleep(5)


def get_host_keys(k8s):
    try:
        return k8s.get_secret('ssh-host-keys')['data']
    except KubernetesError:
        return None


SSH_HOST_KEY_SECRET_TMPL = Template(
    resource_string(__name__, 'resources/ssh-host-key-secret.tmpl.yaml'))


def ssh_host_key_secret_template(name='ssh-host-keys'):
    return yaml.load(SSH_HOST_KEY_SECRET_TMPL.render(name=name))


def put_host_keys(k8s, keys):
    spec = ssh_host_key_secret_template()
    spec['data'] = keys
    k8s.create_secret(spec)


def generate_ssh_host_keys(destination):
    dsa_key_path = os.path.join(destination, 'ssh_host_dsa_key')
    rsa_key_path = os.path.join(destination, 'ssh_host_rsa_key')
    ecdsa_key_path = os.path.join(destination, 'ssh_host_ecdsa_key')

    for path in [dsa_key_path, rsa_key_path, ecdsa_key_path]:
        if os.path.exists(path):
            os.unlink(path)

    check_call(['ssh-keygen', '-q', '-t', 'dsa', '-N', '', '-f', dsa_key_path])
    check_call(['ssh-keygen', '-q', '-t', 'rsa', '-N', '', '-f', rsa_key_path])
    check_call(
        ['ssh-keygen', '-q', '-t', 'ecdsa', '-N', '', '-f', ecdsa_key_path])

    for path in [dsa_key_path, rsa_key_path, ecdsa_key_path]:
        os.chmod(path, 0o600)

    return {
        'dsa': open(dsa_key_path, 'r').read(),
        'rsa': open(rsa_key_path, 'r').read(),
        'ecdsa': open(ecdsa_key_path, 'r').read()
    }


def write_ssh_host_keys(destination, keys):
    dsa_key_path = os.path.join(destination, 'ssh_host_dsa_key')
    rsa_key_path = os.path.join(destination, 'ssh_host_rsa_key')
    ecdsa_key_path = os.path.join(destination, 'ssh_host_ecdsa_key')

    for path in [dsa_key_path, rsa_key_path, ecdsa_key_path]:
        if os.path.exists(path):
            os.unlink(path)

    with open(dsa_key_path, 'w') as f:
        f.write(keys['dsa'])

    with open(rsa_key_path, 'w') as f:
        f.write(keys['rsa'])

    with open(ecdsa_key_path, 'w') as f:
        f.write(keys['ecdsa'])

    for path in [dsa_key_path, rsa_key_path, ecdsa_key_path]:
        os.chmod(path, 0o600)


def run(args):
    k8s = Kubernetes(args.kubernetes_url, namespace='noel')
    wait_for_kubernetes(k8s)

    keys = get_host_keys(k8s)

    if keys:
        logger.info('Existing ssh host keys found.')
        write_ssh_host_keys(args.destination, keys)
        return

    logger.warning('No existing ssh host keys. Generating keys.')
    keys = generate_ssh_host_keys(args.destination)

    try:
        put_host_keys(k8s, keys)
        logger.info('Host keys saved to Kubernetes.')
    except KubernetesError as e:
        if e.httperror.response.status_code == 409:
            logger.error(
                'Conflict while writing ssh keys to Kubernetes, retrying...')
            return run(args)
        else:
            logger.exception('Unexpected error while writing ssh host keys.')
            raise


def main():
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--kubernetes-url',
        default='http://localhost:8001',
        help='The URL for the Kubernetes API.')
    parser.add_argument('--destination', default='/etc/ssh')

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
