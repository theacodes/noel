#!/bin/bash

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

export PYTHONIOENCODING="utf-8"
export PYTHONUNBUFFERED=true

# Chmod the docker socket so that git can talk to it.
chown root:docker /var/run/docker.sock

# Generate or get existing ssh host keys. This ensures that every remote
# builder has the same SSH identity, so that when the external Kubernetes
# service load balances to multiple instances, users do not get a warning.
noel-ssh-host-keys-manager

# Launch processes
honcho -f /src/Procfile start
