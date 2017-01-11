# elasticsearch-templates

The repository contains scripts and sources to generate Elasticsearch templates
that comply with Common Data Model.

# Problem Statement

We are trying to solve the problem of conflicts and inconsistencies in log data
as collected by, and from, different subsystems stored together as a unified
data set under one warehouse.

# Namespace hierarchy

Namespace hierarchy on the log metadata is the key concept.
We use the Elasticsearch index templates and document mapping to cast the common
metadata keys into usable documents.

Namespace corresponds to a top-level JSON key of Elasticsearch document.
Namespace is usually defined per individual app or subsystem, so that different
applications/subsystems not conflict in various metadata fields.

# Adding new namespace

Create a namespace definition file in [namespaces/](namespaces/) folder.

# Adding new Elasticsearch template

Create a sub-folder in [templates/](templates/) folder, named as the desired
template. (Alternatively copy/modify one of the existing template folders)

Add/modify `template.yml` definition file to include proper namespace
definitions. See for example [templates/openshift/README.md](templates/openshift/README.md)
for the details.

# Generating documentation

TODO
