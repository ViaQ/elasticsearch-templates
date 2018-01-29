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
