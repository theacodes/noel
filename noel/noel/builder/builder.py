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

"""Builder handles running the commands to build an application image using
docker."""

from noel.builder import docker, gcp
from noel.logger import logger


def build(dir, app, version):
    project_id = gcp.get_project_id()
    logger.info('Using Google Cloud Project ID {}'.format(project_id))

    logger.info('Building app {} at {}'.format(app, dir))

    image = 'gcr.io/{}/noel-app-{}:{}'.format(project_id, app, version)

    docker.build(image, dir)

    logger.info('Finished building image, pushing image to registry.')

    docker_auth_token = gcp.get_gce_auth_token()

    if docker_auth_token:
        docker.login('https://gcr.io', docker_auth_token)

    docker.push(image, use_gcloud=True if not docker_auth_token else False)

    logger.info('Image {} successfully built and pushed.'.format(image))

    return image
