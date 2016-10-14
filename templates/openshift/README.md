viaq openshift index templates for ElasticSearch
=================================

The template files are automatically generated.
Please _do not edit_ the files directly.

In order to edit the template please modify [objects.yml](objects.yml) and the respective object type files.

To rebuild the template, run:
> python ../scripts/generate_template.py . ../../objects_dir

For details about the mapping please see [ElasticSearch reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html)

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
`template`: indices that will be matched by this template  

objects.yml
----------
This is the file that contains all the settings information and pointers to the specific mappings.  
* `skeleton_path`: The path to the `skeleton.json` file that contain the initial JSON structure of the template.
* `elasticsearch_template`: This section defines the parameters common for the entire template, they are explicitly overwritten in the final template file.
** `name`: index pattern matched.
** `order`: template order. Lower order is applied first. [details](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html#multiple-templates)
* `types`: filenames of various document object types to be included in the template
