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

"""Google Cloud Platform-specific helpers."""

import requests

from noel.utils import call


# Compute engine metadata service.
METADATA_ENDPOINT = 'http://metadata.google.internal/computeMetadata/v1'


def get_gce_auth_token():
    """Gets the service account auth token for the GCE instance."""
    try:
        r = requests.get(
            METADATA_ENDPOINT + '/instance/service-accounts/default/token',
            headers={'Metadata-Flavor': 'Google'},
            timeout=2)

        r.raise_for_status()

        return r.json()['access_token']

    except:
        return None


def get_gce_project_id():
    """Gets the google cloud project for the current GCE instance."""
    try:
        r = requests.get(
            METADATA_ENDPOINT + '/project/project-id',
            headers={'Metadata-Flavor': 'Google'},
            timeout=2)

        r.raise_for_status()

        return r.text

    except:
        return None


def get_project_id():
    """Gets the google cloud project either via the GCE metadata service or
    the Google Cloud SDK."""
    project_id = get_gce_project_id()

    if project_id:
        return project_id

    return call(
        'gcloud',
        'config',
        'list',
        'project',
        '--format=value(core.project)',
        silent=True).strip()
