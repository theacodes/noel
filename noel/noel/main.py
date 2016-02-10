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

"""The entrypoint for the noel command line tool."""

import argparse
import os

import noel.builder.commands
import noel.deployer.commands
from noel.utils import run_command


def build_and_deploy_command(args):
    """Build an application image and deploy it to the cluster. This
    essentially runs build and then deploy-image."""
    image = noel.builder.commands.build_command(args)
    args.image = image
    noel.deployer.commands.deploy_image_command(args)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument(
        '--kubernetes-url',
        default='http://localhost:8001',
        help="The URL for the Kubernetes API.")

    noel.builder.commands.register_commands(subparsers)
    noel.deployer.commands.register_commands(subparsers)

    build_and_deploy = subparsers.add_parser(
        'build-and-deploy',
        help=build_and_deploy_command.__doc__)

    build_and_deploy.set_defaults(func=build_and_deploy_command)
    build_and_deploy.add_argument(
        '--project-id',
        default=None,
        help='Google Cloud Project ID, if not specified, it will use gcloud\'s '
             'currently configured project.')
    build_and_deploy.add_argument(
        '--dir',
        default=os.getcwd(),
        help='Directory containing application and Dockerfile. Defaults to the '
             'current directory.')
    build_and_deploy.add_argument(
        '--app',
        default=os.path.basename(os.getcwd()),
        help='The application name. Defaults to the name of the directory.')
    build_and_deploy.add_argument(
        '--version',
        default=None,
        help='The image tag version. Defaults to the current date & time.')

    run_command(parser)
