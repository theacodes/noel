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

COMPONENT=builder
export COMPONENT
LOGS_ARGS=-c builder
export LOGS_ARGS

.PHONY: all
all: deploy

.PHONY: copy-noel
copy-noel:
	$(MAKE) -C ../noel dist
	cp ../noel/dist/*.whl .

.PHONY: build
build: copy-noel
	docker build -t noel/builder .

.PHONY: push
push: build docker-push

.PHONY: deploy
deploy: push spec-template
	kubectl create -f spec.yaml

.PHONY: logs
logs: k8s-logs

.PHONY: kick
kick: push hack-kick
