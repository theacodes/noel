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

"""Command-line commands for noel under the 'deploy' group."""

import os

from noel.deployer import deployer
from noel.kubernetes import Kubernetes
from noel.logger import logger


def deploy_image_command(args):
    """Updates an application with the given docker image."""
    args.app = args.app.lower()

    k8s = Kubernetes(args.kubernetes_url, namespace='noelapp')
    deployer.deploy_app(k8s, args.app, image=args.image)

    logger.info(
        'Application {} updated with image {}'.format(args.app, args.image))


def delete_app_command(args):
    """Deletes an app and all cluster resources associated with it."""
    args.app = args.app.lower()

    k8s = Kubernetes(args.kubernetes_url, namespace='noelapp')
    deployer.delete_app(k8s, args.app)

    logger.info('Application {} deleted'.format(args.app))


def get_config_command(args):
    """Gets the current configuration values for an application."""
    args.app = args.app.lower()

    k8s = Kubernetes(args.kubernetes_url, namespace='noelapp')
    config = deployer.get_config(k8s, args.app)

    if not config:
        logger.error('No config for app {}'.format(args.app))
        return False

    for k, v in config['data'].iteritems():
        print('{}: {}'.format(k, v))


def set_config_command(args):
    """Sets the current configuration values for an application."""
    args.app = args.app.lower()

    data = {pair[0]: pair[1] for pair in [x.split('=', 1) for x in args.pairs]}

    k8s = Kubernetes(args.kubernetes_url, namespace='noelapp')
    config = deployer.update_config(k8s, args.app, data)
    deployer.deploy_app(k8s, args.app, config=config)

    logger.info('Config updated for app {}'.format(args.app))


def logs_command(args):
    """Gets (or streams) the logs for an application."""
    args.app = args.app.lower()

    k8s = Kubernetes(args.kubernetes_url, namespace='noelapp')
    pods = k8s.pods(params={
        'labelSelector': 'noel-app={}'.format(args.app)})

    if not pods['items']:
        logger.error('No running pods found for app {}'.format(args.app))
        return False

    pod = pods['items'].pop()
    logger.info('Using pod {}'.format(pod['metadata']['name']))

    if args.follow:
        logger.warning('Streaming logs. Press ctrl+c to quit.')

    try:
        it = k8s.logs(
            pod['metadata']['name'],
            container='noel-app',
            lines=args.lines,
            follow=args.follow)

        for log in it:
            print(log)

    except KeyboardInterrupt:
        pass


def scale_command(args):
    """Scales the number of replicas for an application."""
    args.app = args.app.lower()

    k8s = Kubernetes(args.kubernetes_url, namespace='noelapp')

    rc = deployer.get_replication_controller(k8s, args.app)

    if not rc:
        logger.error(
            'No replication controller found for app {}.'.format(args.app))
        return False

    k8s.scale(rc['metadata']['name'], replicas=args.replicas)

    logger.info(
        'Scaled app {} to {} replicas.'.format(args.app, args.replicas))


def register_commands(subparsers):
    app_args = ('--app',)
    app_kwargs = {
        'default': os.path.basename(os.getcwd()),
        'help': 'The application name. Defaults to the name of the directory.'
    }

    deploy_image = subparsers.add_parser(
        'deploy-image',
        help=deploy_image_command.__doc__)
    deploy_image.set_defaults(func=deploy_image_command)
    deploy_image.add_argument(*app_args, **app_kwargs)
    deploy_image.add_argument(
        'image',
        help='The docker image and tag to deploy, for example:'
             ' gcr.io/project-id/name:tag')

    delete_app = subparsers.add_parser(
        'delete-app',
        help=delete_app_command.__doc__)
    delete_app.set_defaults(func=delete_app_command)
    delete_app.add_argument(*app_args, **app_kwargs)

    get_config = subparsers.add_parser(
        'get-config',
        help=get_config_command.__doc__)
    get_config.set_defaults(func=get_config_command)
    get_config.add_argument(*app_args, **app_kwargs)

    set_config = subparsers.add_parser(
        'set-config',
        help=set_config_command.__doc__)
    set_config.set_defaults(func=set_config_command)
    set_config.add_argument(*app_args, **app_kwargs)
    set_config.add_argument(
        'pairs',
        nargs='+',
        help='key=value pairs of config to set.')

    logs = subparsers.add_parser(
        'logs',
        help=logs_command.__doc__)
    logs.set_defaults(func=logs_command)
    logs.add_argument(*app_args, **app_kwargs)
    logs.add_argument(
        '--lines',
        default=50,
        help='The number of lines to output.')
    logs.add_argument(
        '--follow',
        default=False,
        action='store_true',
        help='Whether or not to follow the application logs.')

    scale = subparsers.add_parser(
        'scale',
        help=scale_command.__doc__)
    scale.set_defaults(func=scale_command)
    scale.add_argument(*app_args, **app_kwargs)
    scale.add_argument(
        'replicas',
        help='The number of replicas.')
