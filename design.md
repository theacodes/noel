# Noel

Noel is an example Platform-as-a-Service workflow built on top of Kubernetes.

The intention is to show one way to compose the building blocks provided by Kubernetes to create an opinionated workflow for deploying stateless (12-factor) applications/microservices.

Noel is inspired by Dokku, Deis, and Google App Engine.

## Constraints

Because Noel is intended to be a barebones sample, it has a few constraints in its design:

* Applications are defined only by a Dockerfile.
* Applications should be stateless and horizontally scalable.
* Noel stores no state itself - it only creates resources on the Kubernetes cluster.

Noel is only one way to go about building opinionated deployment tools and there are all sorts of things that could be built from this idea. Some ideas for things you could build from here:

* Add an additional configuration file that's read by the Noel client to add volumes, secrets, sidecar containers, etc. to applications.
* Add system-wide "add-ons" that get exposed to every app. For example, a syslog collection container.
* Add a web-UI to manage application and configuration.

## Workflows

Noel presents two possible deployment workflows:

1. **Local build & deploy**: you run `noel build-and-deploy` locally. Noel uses docker to build the application then creates resources in your cluster. This requires you have both docker running locally and access to the Kubernetes API. This is similar to how App Engine deployments work.

2. **Git push-to-deploy**: you run `git push` to a special git remote. The remote builder receives your code and run `noel build-and-deploy` on the remote builder. This means you only need git to deploy applications. This is similar to how Heroku and Deis deployments work.

## Concepts / Terms

* **Application** - An individual application. Noel can host multiple applications. Each application is addressable as `app.noelapp.svc.cluster.local` internally and `app.example.com` externally. The application name is determined by the name of the build repository.
* **Build repository** - Applications are deployed by pushing code to a special git repository.
* **Docker image** - Application source code gets built into a single Docker image every time an update is pushed to the build repository.
* **Config** - Every application has an associated set of configuration values. Configuration is versioned, just like Docker images. Config values are set using the Noel client. These values are stored as a Kubernetes secret and are exposed to the application as files under `/var/noel/config`.
* **Version** - This is the deployment artifact for an application. This artifact consists of a Docker image *and* a configuration version. If either the image or the configuration changes, it constitutes a new version.

## Components

### Noel command line tool

The `noel` command-line application is responsible for building and deploying applications. It builds images using Docker. It handles configuration and deployment by creating and modifying resources in Kubernetes. `noel` can be run locally if you have Docker and Kubernetes API access or invoked via the remote builder.

In order to deploy an application it:
* Builds the application image via Docker, as needed.
* Gets or sets the configuration values, as needed.
* Creates a Kubernetes service for the application, if it doesn't already exist. The service is exposed as the DNS name `app.noelapp.svc.cluster.local`. This setup only happens the first time the application is deployed.
* Creates a new Kubernetes replication controller for the version. The controller is named `app-{image-tag}-{config-version}`.
* If there are any old versions, it immediately scales their replication controllers to `0`, then deletes them. In the future, this will use the Kubernetes Deployment API to do a rolling update.

### Remote builder

The remote builder is responsible for accepting a `git push` and running `noel build-and-deploy` to build the application's image and deploy it to the cluster.

The builder runs a standard OpenSSH server. Authorized SSH keys are stored as Kubernetes secrets and are periodically refreshed from the Kubernetes API.

You can run multiple builder instances running on the cluster depending on how frequently you deploy. The builder is exposed externally via a Kubernetes service.

### Nginx proxy

A single nginx proxy service is used to route HTTP request to applications. The proxy uses the simple redirect rule 
`{app}.example.com` -> `{app}.noelapp.svc.cluster.local` to send traffic to the appropriate application.

This service can be scaled to handle more traffic if needed.
