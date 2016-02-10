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

"""Script executed by git after receiving a push.

This script:
* Checks out the repository into the build staging directory.
* Runs the Noel build and deploy command.
"""

import argparse
import os
import sys

from noel.utils import call
from noel.logger import logger, setup_logging
from noel.main import build_and_deploy_command

STAGING_ROOT = os.environ.get('STAGING_ROOT', '/var/build')


def post_receive_hook_command():
    repo_name = os.path.basename(os.getcwd())
    _, sha, ref = read_push_info_from_stdin()

    if ref != 'refs/heads/master':
        logger.error('Received ref {}, not deploying. \n'
                     'Please push master to deploy.'.format(ref))
        return False

    logger.info('Got request to build project {}.'.format(repo_name))

    staging_dir = os.path.join(STAGING_ROOT, repo_name)

    logger.info('Staging code at {}'.format(staging_dir))

    checkout_repo(staging_dir)

    args = argparse.Namespace(
        dir=staging_dir,
        app=repo_name,
        version=sha[:6],
        kubernetes_url='http://localhost:8001')

    return build_and_deploy_command(args)


def read_push_info_from_stdin():
    prev_sha, current_sha, ref = sys.stdin.readline().strip().split(' ')
    return prev_sha, current_sha, ref


def checkout_repo(staging_dir):
    if not os.path.exists(staging_dir):
        os.makedirs(staging_dir)

    call('git', '--work-tree', staging_dir, 'checkout', '-f')


def main():
    setup_logging()

    try:
        if post_receive_hook_command() is False:
            sys.exit(1)
    except Exception:
        logger.exception('Deploy failed')
        sys.exit(1)
