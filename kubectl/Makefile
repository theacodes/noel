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

include ../common.mk

COMPONENT=kubectl
export COMPONENT

.PHONY: all
all: build push

.PHONY: build
build:
	wget -N https://storage.googleapis.com/kubernetes-release/release/v1.1.2/bin/linux/amd64/kubectl
	chmod +x kubectl
	docker build -t noel/kubectl .

.PHONY: push
push: build docker-push
