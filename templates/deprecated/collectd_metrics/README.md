# viaq collectd index templates for ElasticSearch

The template files are automatically generated.
Please _do not edit_ the files directly.

In order to edit the template please modify [template.yml](template.yml) and
the respective namespace files referenced there.

To rebuild the template, run:
> make

# Contents

The template contains mappings for `collectd` output.

`collectd` namespace is the reserved namespace for collectd metrics.

## Hierarchy structure

General rule-of-thumb hierarchy structure is to have collectd's `plugin` name
nested immediately within `collectd` top level namespace.
collectd's `type` is nested inside `plugin` group.

* `type` is a value if it corresponds to a single `dsnames`/`dsvalues`.
* `type` is a group if it contains several `dsnames`/`dsvalues`, the respective
`dsnames`/`dsvalues` pairs are then mapped as a hash.

For example
```
{"values":[0,0],"dstypes":["gauge","gauge"],"dsnames":["processes","threads"]}
```
Will translate to:
```
{"processes":0, "threads": 0}
```
