# viaq common index templates for ElasticSearch

The template files are automatically generated.
Please _do not edit_ the files directly.

In order to edit the template please modify [template.yml](template.yml) and
the respective namespace files referenced there.

To rebuild the template, run:
> make

This is the generic default template for `logstash-*` type indices.

# Contents

The following sources are included in the template:

* rsyslog data;
* openshift/kubernetes/docker data;
* GlusterFS

TODO: OpenStack data
