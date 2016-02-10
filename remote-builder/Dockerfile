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

FROM debian:jessie

# Install packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl python python-pip git openssh-server

# Install honcho, a python-based process manager. We need this because we
# run multiple processes in this container.
RUN pip install honcho

#
# Docker
#

# Download the docker client.
ENV DOCKER_BUCKET get.docker.com
ENV DOCKER_VERSION 1.8.0
ENV DOCKER_SHA256 729dc544c23c8a079beb67b72d69fa0cf145fed640ef2e3d847ab711d6354662

RUN curl -fSL "https://${DOCKER_BUCKET}/builds/Linux/x86_64/docker-$DOCKER_VERSION" -o /usr/local/bin/docker \
    && echo "${DOCKER_SHA256}  /usr/local/bin/docker" | sha256sum -c - \
    && chmod +x /usr/local/bin/docker

# Docker group is required for the git user to be able to access docker.
RUN addgroup docker

#
# Git
#

# Configure the git user.
ENV GITHOME /home/git
ENV GITUSER git
# Note that we use a custom shell here. This shell only allows git commands
# and creates repositories on demand.
RUN adduser \
    --quiet \
    --disabled-password \
    --geco '' \
    --shell "/usr/local/bin/noel-git-shell" \
    --home \
    $GITHOME \
    $GITUSER
RUN addgroup $GITUSER docker
RUN mkdir -p $GITHOME/.ssh && chown git:git $GITHOME/.ssh
RUN chown -R $GITUSER:$GITUSER $GITHOME

# Configure build directory. This is where code will be staged after being
# pushed so that docker build can be performed.
RUN mkdir -p /var/build
RUN chown -R $GITUSER:$GITUSER /var/build

#
# SSH
#

# Make SSH's run dir.
RUN mkdir -p /var/run/sshd

# Link SSH server config.
RUN rm /etc/ssh/sshd_config
RUN ln -s /src/sshd_config /etc/ssh/sshd_config

#
# Noel
#

# Add & install noel client wheel.
ADD *.whl /
RUN pip install /*.whl

# Copy src code.
ADD src /src

# Install
RUN pip install /src

EXPOSE 22

ENTRYPOINT /src/entrypoint.sh
