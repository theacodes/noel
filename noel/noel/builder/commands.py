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

"""Command-line commands for noel under the 'build' group."""

from datetime import datetime
import os
import platform

from noel.builder import builder
from noel.builder import remote
from noel.builder import ssh_keys
from noel.logger import logger
from noel.kubernetes import Kubernetes


def build_command(args):
    """Builds an application image using Docker."""
    args.app = args.app.lower()

    if not args.version:
        args.version = datetime.utcnow().strftime('%m%d%y%H%M%S')

    return builder.build(
        args.dir,
        args.app,
        args.version)


def add_ssh_key_command(args):
    """Add an authorized SSH key to the remote builder."""
    with open(os.path.expanduser(args.ssh_key), 'r') as f:
        ssh_key = f.read()

    k8s = Kubernetes(args.kubernetes_url, namespace='noel')
    ssh_keys.add_key(k8s, args.hostname, ssh_key)

    logger.info(
        'SSH Key {} added for as {}'.format(args.ssh_key, args.hostname))


def add_git_remote_command(args):
    """Adds the remote builder as a git remote to the current repository."""

    k8s = Kubernetes(args.kubernetes_url, namespace='noel')
    remote.add_builder_git_remote(k8s, args.app, args.remote_name)

    logger.info(
        'Git remote added. Use `git push {} master` to deploy application {}.'
        .format(args.remote_name, args.app))


def register_commands(subparsers):
    app_args = ('--app',)
    app_kwargs = {
        'default': os.path.basename(os.getcwd()),
        'help': 'The application name. Defaults to the name of the directory.'
    }

    build = subparsers.add_parser(
        'build',
        help=build_command.__doc__)
    build.set_defaults(func=build_command)
    build.add_argument(
        '--dir',
        default=os.getcwd(),
        help='Directory containing application and Dockerfile. Defaults to the '
             'current directory.')
    build.add_argument(*app_args, **app_kwargs)
    build.add_argument(
        '--version',
        default=None,
        help='The image tag version. Defaults to the current date & time.')

    add_ssh_key = subparsers.add_parser(
        'add-ssh-key',
        help=add_ssh_key_command.__doc__)
    add_ssh_key.set_defaults(func=add_ssh_key_command)
    add_ssh_key.add_argument(
        '--hostname',
        default=platform.node(),
        help='The hostname to use.')
    add_ssh_key.add_argument(
        '--ssh-key',
        default='~/.ssh/id_rsa.pub',
        help='The SSH public key to add.')

    add_git_remote = subparsers.add_parser(
        'add-git-remote',
        help=add_git_remote_command.__doc__)
    add_git_remote.set_defaults(func=add_git_remote_command)
    add_git_remote.add_argument(*app_args, **app_kwargs)
    add_git_remote.add_argument(
        '--remote-name',
        default='noel',
        help='The name of the git remote to add. Defaults to "noel".')
