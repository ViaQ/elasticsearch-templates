com.redhat.viaq template
=================================

The template file com.redhat.viaq.template.json is automatically generated. Please *do not edit* the file directly.

In order to edit the template please modify fields.yml and skeleton.json files.

To rebuild the template, run:
> python ../scripts/generate_template.py . com.redhat.viaq-template

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

fields.yml
----------
This is the file that contains all the mappings information.  
`version`: version of the mapping  
`defaults`: default values. if a particular field is missing a parameter it'll be taken from the default values  
`_default_`: description of the fields used to populate `mappings -> _default_` in the generated template.  
`openstack`: spedial mapping for OpenStack. inherits all the fields from _default_  
`doc_sections`: used in the generation of the documentation to name the sections.  


