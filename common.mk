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

GCLOUD_PROJECT:=$(shell gcloud config list project --format="value(core.project)")
export GCLOUD_PROJECT

.PHONY: docker-push
docker-push:
	docker tag -f noel/$(COMPONENT) gcr.io/$(GCLOUD_PROJECT)/noel-$(COMPONENT)
	gcloud docker push gcr.io/$(GCLOUD_PROJECT)/noel-$(COMPONENT)

.PHONY: k8s-logs
k8s-logs:
	POD=$$(kubectl \
		--namespace noel \
		get pods \
		-o template --template="{{range .items}}{{.metadata.name}}{{end}}" \
		-l component=$(COMPONENT)) && \
	kubectl \
		--namespace noel \
		logs \
		$$POD \
		$$LOGS_ARGS

.PHONY: hack-kick
hack-kick:
	POD=$$(kubectl \
		--namespace noel \
		get pods \
		-o template --template="{{range .items}}{{.metadata.name}}{{end}}" \
		-l component=$(COMPONENT)) && \
	kubectl \
		--namespace noel \
		delete pod \
		$$POD

.PHONY: hack-bash
hack-bash:
	POD=$$(kubectl \
		--namespace noel \
		get pods \
		-o template --template="{{range .items}}{{.metadata.name}}{{end}}" \
		-l component=$(COMPONENT)) && \
	kubectl \
		--namespace noel \
		exec \
		$$POD \
		$$LOGS_ARGS \
		-it \
		-- /bin/bash

.PHONY: spec-template
spec-template:
	sed "s/\$$GCLOUD_PROJECT/$(GCLOUD_PROJECT)/g" spec.tmpl.yaml > spec.yaml
