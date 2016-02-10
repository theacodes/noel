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

"""Logic for creating the necessary resources in Kubernetes to deploy a given
application version."""

from noel.kubernetes import KubernetesError
from noel.deployer import templates


def deploy_app(k8s, app, image=None, config=None):
    """Deploys an application version.

    An application version consists of two parts: an image and a configuration.
    Both images and config have distinct, separate version identifiers.

    An image is a docker images, typically built by the noel builder but can
    just be any docker image. The tag is what identifies the image's version.

    A config is a per-application Kubernetes secret. The Kubernetes API resource
    generation determines a config's version.

    The application version is '{image-tag}-{config-version}'. A deployment is
    triggered whenever either the image or the config is updated. When one is
    updated, the other is implied to be the current version.

    In both cases, a new replication controller will be created for the app
    version and all existing replication controllers for the app will be turned
    down.
    """

    # Get the current version and image, if not specified.
    if not image:
        image = get_current_image(k8s, app)

    if not config:
        # Note: config can totally be None here. That's fine.
        config = get_config(k8s, app)

    image_tag = image.rsplit(':').pop()
    config_version = config['metadata']['resourceVersion'] if config else '0'
    build_version = '{}-{}'.format(image_tag, config_version)

    app_svc = create_service(k8s, app)
    app_rc = create_replication_controller(
        k8s, app, build_version, image, config)
    turndown_old_replication_controllers(k8s, app, build_version)

    return app_rc, app_svc


def delete_app(k8s, app):
    delete_config(k8s, app)
    delete_service(k8s, app)
    turndown_old_replication_controllers(k8s, app, 'delete')


def get_current_image(k8s, app):
    rc = get_replication_controller(k8s, app)

    if not rc:
        raise ValueError("No replication controller found for {}".format(app))

    return rc['spec']['template']['spec']['containers'][0]['image']


def get_replication_controller(k8s, app):
    # TODO: It's possible for this to get multiple RCs.
    # Think of a way to deal with that.
    results = k8s.replicationcontrollers(params={
        'labelSelector': 'noel-app={}'.format(app)
    })

    if results.get('items'):
        return results['items'].pop()

    return None


def create_replication_controller(k8s, app, build_version, image, config):
    rc_spec = templates.app_replicationcontroller(
        name=app,
        build_version=build_version,
        image=image,
        config=config)
    return k8s.create_replicationcontroller(rc_spec)


def turndown_old_replication_controllers(k8s, app, build_version):
    rcs = get_old_replication_controllers(k8s, app, build_version)

    for rc in rcs:
        turndown_replication_controller(k8s, rc)


def turndown_replication_controller(k8s, rc):
    # NOTE: Presently this just scales to zero and then deletes. In the future
    # the Kubernetes deployment API can handle doing a rolling update for us.
    if rc['status']['replicas'] != 0:
        k8s.scale(rc['metadata']['name'], 0)
    k8s.delete_replicationcontroller(rc['metadata']['name'])


def get_old_replication_controllers(k8s, app, build_version):
    rcs = k8s.replicationcontrollers(params={
        'labelSelector': 'noel-app={},build-version!={}'.format(
            app, build_version)
    }).get('items', [])

    return rcs


def create_service(k8s, app):
    """Creates a service for the application, if needed.

    Every app needs a service so that traffic can be routed to it, both inside
    and outside of the cluster. Typically, the app service is not directly
    exposed outside of the cluster, instead, the http-frontend service handles
    proxying outside traffic.
    """
    try:
        return k8s.get_service(app)
    except KubernetesError:
        pass

    service_spec = templates.app_service(name=app)
    return k8s.create_service(service_spec)


def delete_service(k8s, app):
    try:
        k8s.delete_service(app)
    except KubernetesError:
        pass


def get_config(k8s, app):
    try:
        return k8s.get_secret(app)
    except KubernetesError:
        return None


def update_config(k8s, app, config):
    try:
        existing = k8s.get_secret(app)
    except KubernetesError:
        existing = None

    if existing:
        current_config = existing['data']
        current_config.update(config)
        config = current_config

    secret = templates.app_secret(app, config)

    if existing:
        return k8s.replace_secret(secret)
    else:
        return k8s.create_secret(secret)


def delete_config(k8s, app):
    try:
        k8s.delete_secret(app)
    except KubernetesError:
        pass
