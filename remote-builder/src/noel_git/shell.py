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

"""A limited unix shell suitable for use on a git remote.

This shell only allows the git-receive-pack and git-upload-pack commands to be
executed. It disallows interactive sessions.

Finally, it handles creating repositories on demand. This means when a user
pushes to a non-existent repository, this will handle creating an empty one.

This is useful because it allows Noel users to deploy applications with zero
configuration.
"""

import os
import re
import sys

from noel.utils import call
from pkg_resources import resource_string

RECEIVE_HOOK = resource_string(__name__, 'resources/post-receive-hook')
RECEIVE_RE = re.compile(r'^git-receive-pack \'/?([a-zA-Z0-9-]*)\'$')
UPLOAD_RE = re.compile(r'^git-upload-pack \'/?([a-zA-Z0-9-]*)\'$')


def create_repository(repo_root, name):
    path = os.path.join(repo_root, name)
    hook_path = os.path.join(path, 'hooks', 'post-receive')
    os.makedirs(path)
    call('git', 'init', '--bare', path, silent=True)

    with open(hook_path, 'w') as f:
        f.write(RECEIVE_HOOK)

    call('chmod', '+x', hook_path, silent=True)
    call('chown', '-R', 'git:git', path, silent=True)


def do_receive(path):
    adjusted_path = os.path.join('~', path)

    if not os.path.exists(path):
        create_repository(os.environ['HOME'], path)

    return call('/bin/bash', '-c', 'git-receive-pack \'{}\''.format(
        adjusted_path))


def do_upload(path):
    adjusted_path = os.path.join('~', path)
    return call('/bin/bash', '-c', 'git-upload-pack-pack \'{}\''.format(
        adjusted_path))


def main():
    if sys.argv < 3:
        print('Invalid arguments: {}'.format(' '.join(sys.argv)))
        sys.exit(1)

    if sys.argv[1] != '-c':
        print('Interactive session not allowed')
        sys.exit(1)

    with open('/tmp/sshlog', 'a') as f:
        f.write(str(sys.argv) + '\n')

    command = sys.argv[2]

    match = RECEIVE_RE.match(command)
    if match:
        sys.exit(do_receive(match.group(1)))

    match = UPLOAD_RE.match(command)
    if match:
        sys.exit(do_upload(match.group(1)))

    print('Command not allowed: {}'.format(command))
    sys.exit(1)
