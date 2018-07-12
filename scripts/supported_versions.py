#!/usr/bin/env python

"""
Common data model supports the following versions of Elasticsearch.
"""

_es2x = "2.4.4"
_es5x = "5.5.2"

elasticsearch = [_es2x, _es5x]


def bw_mapping_compatibility(es_version, skeleton):
    """
    Convert mapping skeleton to earlier Elasticsearch version.
    See <https://github.com/ViaQ/elasticsearch-templates/issues/71> for follow up.
    """

    # Right now we handle only BW conversion from es5x to es2x
    if es_version == _es5x:
        # es5x is the latest and all templates should be already
        # formatted correctly
        return
    elif es_version == _es2x:

        # Convert mappings of dynamic templates
        for template in skeleton['mappings']['_default_']['dynamic_templates']:
            # json.dump(template, sys.stdout, indent=2, separators=(',', ': '), sort_keys=True)
            first_key = list(template.keys())[0]
            dynamic_mapping = template[first_key]['mapping']
            _transform_mapping_5x_to_2x(dynamic_mapping)

        # Convert mappings of properties
        # for properties in skeleton['mappings']['_default_']['properties']:
        #     p_mapping = skeleton['mappings']['_default_']['properties'][properties]
        #     _transform_mapping_5x_to_2x(p_mapping)
        default_mapping = skeleton['mappings']['_default_']
        _transform_mapping_5x_to_2x(default_mapping)

    else:
        print("Unsupported Elasticsearch version: {}".format(es_version))


def _transform_mapping_5x_to_2x(mapping):

    keys = list(mapping.keys())
    for key in keys:

        # Transform 'norms'.
        # See <https://github.com/ViaQ/elasticsearch-templates/issues/73>
        if key == "norms":
            # val = not mapping[key]
            val = mapping[key]
            mapping.pop(key, None)
            mapping[key] = { 'enabled': val }

        # TODO: Transform 'string' type and 'index'
        # See <https://github.com/ViaQ/elasticsearch-templates/issues/67>
        # See <https://github.com/ViaQ/elasticsearch-templates/issues/68>
        if key == "type":
            if mapping[key] == 'keyword':
                mapping[key] = 'string'
                mapping['index'] = 'not_analyzed'
            elif mapping[key] == 'text':
                mapping[key] = 'string'
                mapping['index'] = 'analyzed'
            elif mapping[key] in ['date', 'boolean', 'ip', 'long', 'integer', 'short', 'byte', 'double', 'float']:
                mapping['index'] = 'not_analyzed'

    if 'fields' in mapping:
        fields_keys = mapping['fields'].keys()
        for fields_key in fields_keys:
            _transform_mapping_5x_to_2x(mapping['fields'][fields_key])

    if 'properties' in mapping:
        properties_keys = mapping['properties'].keys()
        for property_key in properties_keys:
            # ES2.x did not support ipv6 type. ES5.x support both ipv4 and ipv6 as "ip" type.
            # Because of that we need to override ipv6 type to keyword type, which will be transformed to
            # the string type later.
            # The only way how we detect the ipv6 field type is by its name "ipaddr6"
            if property_key == 'ipaddr6':
                mapping['properties'][property_key]['type'] = 'keyword'
            # ... and follows recursive call to mapping transformation.
            _transform_mapping_5x_to_2x(mapping['properties'][property_key])


def bw_index_pattern_compatibility(es_version, res, field):
    """
    Convert index-pattern field to earlier Elasticsearch version.

    :param str es_version:
    :param dict res: Output
    :param dict field: Original field
    """

    # Right now we handle only BW conversion from es5x to es2x
    if es_version == _es5x:
        # es5x is the latest and all fields should be already
        # formatted correctly
        return
    elif es_version == _es2x:
        _transform_field_5x_to_2x(res, field)
    else:
        print("Unsupported Elasticsearch version: {}".format(es_version))


def _transform_field_5x_to_2x(res, field):
    res["indexed"] = res.pop("searchable")
    res["doc_values"] = res.pop("readFromDocValues")
    res.pop("aggregatable")
    res["analyzed"] = field.get("index", "") == True
    if res["type"] == "text":
        res["type"] = "string"
    elif res["type"] == "keyword":
        res["type"] = "string"
    # assuming convention ipv6 address is called (or ends with) "ipaddr6"
    # ES 2x did not support ipv6 types, we assume the same apply to Kibana 4.6.4 as well...
    elif res["type"] == "ip" and res["name"].endswith("ipaddr6"):
        res["type"] = "string"
    return field
