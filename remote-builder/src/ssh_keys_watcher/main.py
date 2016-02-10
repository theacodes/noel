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


"""Watches Kubernetes for SSH keys and writes them to an authorized_keys file.

The remote builder uses SSH keys for authorizing users. Users with access to
the cluster can use the noel client to create a secret in Kubernetes containing
their SSH public key. This watches that secret and puts their public key into
the git users' authorized_keys file. This allows them push access to the
remote builder.
"""


import argparse
import time

from noel.kubernetes import Kubernetes, KubernetesError
from noel.logger import logger, setup_logging


def write_authorized_keys_file(keys, destination):
    with open(destination, 'w') as f:
        for key in keys.values():
            f.write(key.strip() + '\n')


def run(args):
    k8s = Kubernetes(args.kubernetes_url, namespace='noel')
    resource_version = None

    try:
        secret = k8s.get_secret('ssh-keys')
        keys = secret['data']
        resource_version = secret['metadata']['resourceVersion']

        write_authorized_keys_file(keys, args.destination)

        logger.info('Wrote authorized keys. {} known keys.'.format(
            len(keys)))

    except KubernetesError as e:
        if e.httperror.response.status_code == 404:
            logger.warning('No ssh keys found, will watch for more.')
        else:
            logger.exception(
                'Unexpected error while retrieving initial ssh keys.')

    while True:
        try:
            params = {
                'labelSelector': 'type=ssh-keys',
                'resourceVersion': resource_version
            }

            for change in k8s.watch_secrets(params=params):
                if change['type'] not in ['CREATED', 'ADDED', 'MODIFIED']:
                    continue

                secret = change['object']
                if secret['metadata']['name'] != 'ssh-keys':
                    continue

                keys = k8s.decode_secret_data(secret['data'])
                write_authorized_keys_file(keys, args.destination)

                logger.info('Updated authorized keys. {} known keys.'.format(
                    len(keys)))

                # Set the resource version param, so that any exception occurs
                # we only get the changes since the last one we saw.
                resource_version = secret['metadata']['resourceVersion']

        except Exception:
            logger.exception(
                'Error while refreshing ssh keys, waiting 30 seconds.')
            time.sleep(30)


def main():
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--kubernetes-url',
        default='http://localhost:8001',
        help="The URL for the Kubernetes API.")
    parser.add_argument('destination')

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
