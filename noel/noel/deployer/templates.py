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

import yaml

from jinja2 import Template
from pkg_resources import resource_string

APP_SERVICE_TMPL = Template(
    resource_string(__name__, 'resources/app-service.tmpl.yaml'))
APP_RC_TMPL = Template(
    resource_string(__name__, 'resources/app-rc.tmpl.yaml'))
APP_SECRET_TMPL = Template(
    resource_string(__name__, 'resources/app-secret.tmpl.yaml'))


def app_service(name):
    return yaml.load(APP_SERVICE_TMPL.render(name=name))


def app_replicationcontroller(name, build_version, image, config):
    return yaml.load(APP_RC_TMPL.render(
        name=name,
        build_version=build_version,
        image=image,
        config=config))


def app_secret(name, data):
    return yaml.load(APP_SECRET_TMPL.render(name=name, data=data))
