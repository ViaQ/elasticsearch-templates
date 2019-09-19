viaq openshift index templates for ElasticSearch and index patterns for Kibana
=================================

The template files are automatically generated.
Please _do not edit_ the files directly.

In order to edit the template please modify [objects.yml](objects.yml) and the respective object type files.

To rebuild the template, run:
> python ../scripts/generate_template.py . ../../objects_dir

For details about the mapping please see [ElasticSearch reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html) and [Kibana reference](https://www.elastic.co/guide/en/kibana/current/index-patterns.html)

skeleton.json
-------------
This file contains the skeleton of the template without the mappings section.

by sections:  
`aliases`: Aliases for the indices produces from the template. Aliases will be automatically generated along with the indices in future.  
`mappings`: mappings section  
  `_default_`: default mapping skeleton. It is the only mapping present in the skeleton. Other mappings from [fields.yml](fields.yml) will copy this skeleton.  
  `date_detection`: we force no date detection in the unknown fields.  
  `dynamic_templates`: describes the mapping for autocreated fields.  
  `properties`: empty section that is populated with the content from [fields.yml](fields.yml)  
`order`: order of the template. lower order templates are applied first.  
`settings`: various settings  
`index_patterns`: indices that will be matched by this template

skeleton-index-pattern.json
---------------------------
This file the skeleton of the index pattern file.

by sections:
`title`: Filled in by the openshift-elasticseach-plugin [index pattern loader](https://github.com/fabric8io/openshift-elasticsearch-plugin/blob/master/src/main/java/io/fabric8/elasticsearch/plugin/kibana/KibanaSeed.java#L371)
`timeFieldName`: Name of the time field - the script will look for the first field in the `default` namespace that has `type: date`
`fields`: The script will fill this in based on the namespace
* `name`: The name of the field from the namespace
* `type`: Field data type (string, date, etc.) - this is the `type` parameter from the namespace
* `count`: Always has value of 0
* `scripted`: `true` or `false` - all of our fields are not scripted, so `false`
* `indexed`: `true` or `false` - all of our fields are indexed, so `true`
* `analyzed`: `true` or `false` - `true` if the namespace field has `index: analyzed`, `false` otherwise
* `doc_values`: `true` or `false` - taken from the namespace `doc_values` field

template.yml
----------
This is the file that contains all the settings information and pointers to the specific mappings.  
* `skeleton_path`: The path to the `skeleton.json` file that contain the initial JSON structure of the template.
* `elasticsearch_template`: This section defines the parameters common for the entire template, they are explicitly overwritten in the final template file.
** `name`: index pattern matched.
** `order`: template order. Lower order is applied first. [details](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html#multiple-templates)
* `namespaces`: filenames of various namespace definitions to be included in the template
