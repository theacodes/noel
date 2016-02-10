# Noel

*Noel* is an **example** Platform-as-a-Service-like workflow built on top of Kubernetes.

The intention is to show one way to compose the building blocks provided by Kubernetes to create an opinionated workflow for deploying stateless ([12-factor](http://12factor.net/)) applications/microservices.

Noel provides two example workflows:

1. **Local build and deploy**. The application's Docker image is built locally and resources are created on the cluster. This is similar to how [Google App Engine](https://cloud.google.com/appengine) works.
2. **Remote build and deploy**. The application code is pushed to a special git repository, and a builder service handles creating the Docker image and creating resources on the cluster. This is similar to how [Deis](https://deis.io) and [Heroku](http://heroku.com) works.

Noel is designed to be as simple as possible to illustrate how to achieve these workflows. For a more detailed look at how all of the components of Noel and Kubernetes work together, see [design.md](design.md). If you want a more complete Platform-as-a-Service on Kubernetes, look for [Deis v2](https://deis.io).

## Deploying Noel

These instructions are for [Google Container Engine](https://cloud.google.com/container-engine). It's possible to use Noel on other Kubernetes hosts, but there are dependencies in the remote builder on [Google Container Registry](https://cloud.google.com/container-registry).

### Prerequisites

1. Create a project in the [Google Cloud Platform Console](https://console.cloud.google.com).

2. [Enable billing](https://console.cloud.google.com/project/_/settings) for your project.

3. Install the [Google Cloud SDK](https://cloud.google.com/sdk)

        $ curl https://sdk.cloud.google.com | bash 
        $ gcloud init

4. Install [Docker](https://www.docker.com/).

### Create a cluster

1. Create a cluster, you can specify as many nodes as you want but you need at least one. The `storage-rw` scope is needed by the remote builder to push images to Google Container Registry.

        gcloud container clusters create noel \
            --num-nodes 2 \
            --scopes storage-rw

2. Setup `kubectl` to use the container's credentials.

        gcloud container clusters get-credentials noel

3. Verify everything is working:

        kubectl cluster-info

### Deploying Noel cluster components

1. Deploy Noel's cluster-level components (the HTTP frontend and the remote builder) with `make`.

        make all

2. Verify that Noel's pods have started:

        kubectl --namespace noel get pods

## Using Noel

### Installing the Noel client

You can install the Noel client using `pip` (recommended that you do this in a virtualenv):

    pip install ./noel

### Running the Kubernetes proxy

Noel requires access to the Kubernetes API, the easiest way to do this is to just run a proxy:

    kubectl proxy &

### Defining an application

A Noel app only needs a `Dockerfile` in the root of the repository. The Dockerfile should start a web server on port `8080`. Everything else is up to you. There's a [simple Python/Flask example app](https://github.com/jonparrott/noel-example-app) that you can use to start with.

### Deploying locally

To deploy locally:

    noel build-and-deploy

This command will build a docker image locally and push it to Google Container Registry. It will then create the necessary Kubernetes resources to run the application on the cluster.

### Remote deploy

Before you can use remote deployment you'll need to tell the builder about your SSH public key:

    noel add-ssh-key

To deploy remotely you must do a `git push` to a special git remote. To add the remote to the current git repository:

    noel add-git-remote

Then you can push to the remote to deploy:

    git push noel master

## Making requests to your applications

### Internal requests

Within the cluster you can send requests to `appname.noelapp.svc.cluster.local` or `appname.noelapp`. This is the preferred way when designing applications as microservices.

### External requests

Noel's `http-frontend` service handles proxying external traffic to a given noel application. You can get the external, internet-accessible IP address of this service using `kubectl`:

        kubectl --namespace noel get svc http-frontend

You have two options for using this IP address to access your applications.

1. You can point a wildcard top-level domain to this IP address. For example, if you map `*.example.com` to the IP address, you can access your application at `appname.example.com`.

2. You can manually specify a host header when testing requests to applications, for example using `curl`:

    curl -H "Host: app.example.com" external-ip

# Disclaimer

This is not an official Google product, experimental or otherwise. It's just code that happens to be owned by Google. This is for education purposes, it's not intended to be production-ready.

# Contributing changes

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions are more than welcome, but remember, Noel is intended to be simple and educational.

# Licensing

Noel is made available under the Apache License, Version 2.0. See [LICENSE](LICENSE).
