# elasticsearch-templates

The repository contains scripts and sources to generate Elasticsearch templates
that comply with Common Data Model.

[![Build Status](https://travis-ci.org/ViaQ/elasticsearch-templates.svg?branch=master)](https://travis-ci.org/ViaQ/elasticsearch-templates)

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

## Elasticsearch versions support

Support for multiple Elasticsearch versions has been added. Resulting files (ie. index-templates or index-patterns)
are generated for each supported version of Elasticsearch. Target version of ES is encoded into the file name.

List of currently supported ES versions can be find in [scripts/supported_versions.py](scripts/supported_versions.py).

The idea is that all the input file templates and data are formatted according to the latest supported ES version and
scripts handle backward data and format conversions for older ES versions. As part of unit testing the generated data
is compared to released common data files (automatically downloaded from GitHub during tests). 

# Generating documentation

Use the makefile in the [templates/](templates) folder.

Alternatively, run the following command: python ./scripts/generate_template.py (path to template in templates/) namespaces/ --doc.

The generated file looks like "xxx.asciidoc".

# Viewing the documentation

Install the asciidoc viewer in web browser.

Open the local path to the asciidoc file "xxx.asciidoc" in your browser.

# Releasing a new version of the data model

First, generate index templates (for Elasticsearch) and index patterns (for Kibana).
```shell script
$ cd <project_root>
$ make clean
$ make
```
Create a new release tag in repo and push it into GitHub.
```shell script
$ git tag -a 0.0.24 -m "Release 0.0.24"

# We can check the tag is attached to the latest commit now 
$ git log --oneline -n 2
c16dc2c (HEAD -> master, tag: 0.0.24, origin/master, origin/HEAD) Fix index patterns
39d0b71 (tag: 0.0.23) Update model & Bump to 2020.01.23

# Push tag into remote GitHub repo
$ git push origin --tags
Total 0 (delta 0), reused 0 (delta 0)
To github.com:ViaQ/elasticsearch-templates.git
 * [new tag]         0.0.24 -> 0.0.24 
```
Create a new release in GitHub project release.
- create a new release draft from newly created tag
- provide meaningful description and manually attach files belonging to the release
  - Usually the list of the files is the same as in the previous release except
  when it is not :-) (i.e. if there is any significant change)
- publish the release

Once a new release is published you can use [update-viaq-data-model.sh](https://github.com/openshift/origin-aggregated-logging/blob/master/hack/update-viaq-data-model.sh)
script to pull released files into AOL and prepare a new PR with updated data model.