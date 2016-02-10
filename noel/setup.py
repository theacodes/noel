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

from setuptools import setup, find_packages


setup(
    name='noel',

    version='0.0.1',

    description='noel',
    long_description='',

    author='Jon Wayne Parrott',
    author_email='jonwayne@google.com',

    license='Apache Software License',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Linux',
    ],

    package_data={
        'noel.builder': ['resources/*'],
        'noel.deployer': ['resources/*']},
    packages=find_packages(),

    install_requires=['requests', 'colorlog', 'pyyaml', 'jinja2'],

    entry_points={
        'console_scripts': [
            'noel=noel.main:main',
        ],
    },
)
