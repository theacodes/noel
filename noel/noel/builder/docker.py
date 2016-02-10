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

"""Handles talking to docker. This is done via subprocess.call for simplicity
sake, but could also be done via the docker API."""

from noel.utils import call


def build(tag_name, context_dir):
    call('docker', 'build', '-t', tag_name, context_dir)


def push(tag_name, use_gcloud=False):
    """Pushes an image to a repository.

    Because Noel uses Google Container Registry, this has logic to use the
    Google Cloud SDK to push the image. If you're not using GCR, you'll need
    to make sure login is called before calling this.
    """

    if not use_gcloud:
        call('docker', 'push', tag_name)
    else:
        # When not on GCE/GKE, use gcloud to push. gcloud will handle
        # authentication.
        call('gcloud', 'docker', 'push', tag_name)


def login(host, token):
    call('docker', 'login', '-e', 'not@val.id', '-u', '_token',
         '-p', token, host)
