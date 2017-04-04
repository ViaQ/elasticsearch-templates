#!/usr/bin/env python

"""
This script generates both the Elasticsearch template file (*.template.json)
and the Kibana index pattern setting file (*.index-pattern.json) from the
fields.yml file and skeleton.json.
The script is built upon the similar script from libbeats.

Example usage:

   python generate_template.py <template_definition> <namespaces_directory>
"""

import argparse
import yaml
import json


def object_types_to_template(template_definition, output, output_index_pattern, namespaces_dir):
    """
    Assemble objects for the particular template.
    """

    if template_definition is None:
        print "template.yml is empty. Cannot generate template."
        return

    if 'skeleton_path' not in template_definition or\
       'namespaces' not in template_definition:
        print "skeleton_path is not defined. Cannot generate template."
        return

    # Load skeleton of the template
    with open(template_definition['skeleton_path'], 'r') as f:
        skeleton = yaml.load(f)

    if 'skeleton_index_pattern_path' not in template_definition:
        print "skeleton_index_pattern_path is not defined. Cannot generate template."
        return

    # Load skeleton of the template
    with open(template_definition['skeleton_index_pattern_path'], 'r') as f:
        skeleton_index_pattern = yaml.load(f)

    # Load object_type files
    with open(namespaces_dir + '/_default_.yml', 'r') as f:
        default_mapping_yml = yaml.load(f)
    default_mapping = default_mapping_yml['_default_']

    for ns_file in template_definition['namespaces']:
        with open(namespaces_dir + ns_file, 'r') as f:
            cur_ns_yml = yaml.load(f)
        if 'namespace' not in cur_ns_yml:
            print("namespace section is absent in file {0}".format(ns_file))
            return

        default_mapping['fields'].append(cur_ns_yml['namespace'])

    skeleton['mappings']['_default_']['properties'] = (traverse_group_section(
        default_mapping, default_mapping_yml['field_defaults'], process_leaf))

    add_type_version(default_mapping_yml["version"],
                     skeleton['mappings']['_default_'])

    add_index_pattern(
        template_definition['elasticsearch_template']['index_pattern'],
        skeleton)
    add_index_order(template_definition['elasticsearch_template']['order'],
                    skeleton)

    json.dump(
        skeleton, output, indent=2, separators=(',', ': '), sort_keys=True)

    # index pattern stuff
    time_field_name = "time"
    for ii in default_mapping["fields"]:
        if ii['type'] == 'date':
            time_field_name = ii['name']
            break
    skeleton_index_pattern["timeFieldName"] = time_field_name
    skeleton_index_pattern["description"] = skeleton_index_pattern["description"].replace("<the_index_type>", template_definition['elasticsearch_template']['index_pattern'])
    # get fields
    index_pattern_fields = (traverse_group_section_index_pattern(
        default_mapping, default_mapping_yml['field_defaults'], process_leaf_index_pattern))
    skeleton_index_pattern["fields"] = json.dumps(index_pattern_fields)
    json.dump(
        skeleton_index_pattern, output_index_pattern, indent=2, separators=(',', ': '), sort_keys=True)

def add_mapping_to_skeleton(map_type, skeleton):
    """Add mapping type to the skeleton by cloning '_default_' section.
    Args:
        map_type(str): name of the document type to add
        skeleton(dict): skeleton to update
    """
    if map_type != '_default_':
        skeleton['mappings'][map_type] = skeleton['mappings'][
            '_default_'].copy()
        del skeleton['mappings'][map_type]['dynamic_templates']


def traverse_group_section(group, defaults, leaf_handler, groupname=None):
    """
    Traverse the sections tree and fill in the properties
    map.
    Args:
        group(dict): field of type group, that has multiple subfields under
    'fields' key.
        defaults(dict): dict with the defaults for all fields
    Returns:
        dict of individual members of the group.
    """
    properties = {}

    # print "Trying to fill section properties of section %s" % (group)
    try:
        for field in group["fields"]:
            if groupname:
                subgroupname = groupname + "." + group["name"]
            else:
                subgroupname = group.get("name", None)
            prop = traverse_field(field, defaults, leaf_handler, subgroupname)
            properties.update(prop)
    except KeyError:
        print "Skipping empty section %s" % (group)
    # print "Section filled with properties: %s" % (properties)
    return properties


def traverse_group_section_index_pattern(group, defaults, leaf_handler, groupname=None):
    """
    Traverse the sections tree and fill in the index pattern fields
    map.
    Args:
        group(dict): field of type group, that has multiple subfields under
    'fields' key.
        defaults(dict): dict with the defaults for all fields
    Returns:
        array of field definitions.
    """
    fields = []

    # print "Trying to fill section properties of section %s" % (group)
    try:
        for field in group["fields"]:
            if groupname:
                subgroupname = groupname + "." + group["name"]
            else:
                subgroupname = group.get("name", None)
            if field.get("type") == "group":
                more_fields = traverse_group_section_index_pattern(field, defaults, leaf_handler, subgroupname)
                fields.extend(more_fields)
            else:
                out_field = leaf_handler(field, defaults, subgroupname)
                fields.append(out_field)
    except KeyError:
        print "Skipping empty section %s" % (group)
    # print "Section filled with properties: %s" % (properties)
    return fields


def traverse_field(field, defaults, leaf_handler, groupname):
    """
    Add data about a particular field in the properties
    map.
    Iteration entry point.
    Args:
        field(dict):
        defaults(dict): default values
    Returns:
        dict of filled properties.
    """
    properties = {}
    # print "current field is %s" % (field)

    # TODO: Make this more dynamic

    if field.get("type") == "group":
        prop = traverse_group_section(field, defaults, leaf_handler, groupname)

        # Only add properties if they have a content
        if len(prop) is not 0:
            properties[field.get("name")] = {"properties": {}}
            properties[field.get("name")]["properties"] = prop
    else:
        properties = leaf_handler(field, defaults, groupname)

    # print "Result of traversing field is : %s" % (properties)
    return properties


def process_leaf(field, defaults, groupname=None):
    """Process field that is not a group. Fill the template copy with the actual
    data.
    Args:
        field(dict): contents of the field.
        defaults(dict): default values.
    Returns:
        dict corresponding to the data in the particular field.
    """
    # working copy that actually will be used to enter data in template,
    # 'field' variable will stay unmodified
    working_field = field.copy()

    for key in defaults.keys():
        if key not in working_field:
            working_field[key] = defaults[key]

    # Drop documentation-related fields:
    doc_fields = ["description", "example", "path", "name"]
    for docfield in doc_fields:
        if docfield in working_field.keys():
            del working_field[docfield]

    # Fields will be added later after all other subfields are filled in
    if working_field.get("fields"):
        del working_field["fields"]

    res = {}
    if field.get("type") in ["string", "date", "ip", "integer", "long",
                             "short", "byte", "boolean"]:
        res[field["name"]] = working_field.copy()
        res[field.get("name")].update(process_subleaf(field, defaults))
    elif field.get("type") in ["object", "nested"]:
        if "object_struct" in field:
            res[field["name"]] = working_field["object_struct"].copy()
        else:
            res[field["name"]] = {}
        res[field["name"]]["type"] = field.get("type")
    elif field.get("type") == "float":
        res[field["name"]] = {
            "type": "float",
            "doc_values": "true"
        }
    else:
        print "Unknown field. Skipped adding field %s" % (field)
    return res


def process_subleaf(field, defaults):
    """
    Returns:
        dict with "field" subfields if "field" exists
    """
    properties = {}
    if field.get("fields"):
        prop = traverse_group_section(field, defaults, process_leaf)
        if len(prop) is not 0:
            properties["fields"] = prop
    return properties


def process_leaf_index_pattern(field, defaults, groupname):
    """Process field that is not a group. Fill the template copy with the actual
    data.
    Args:
        field(dict): contents of the field.
        defaults(dict): default values.
        groupname(string): name of group this field belongs to e.g. "systemd.u"
    Returns:
        dict corresponding to the data in the particular field.
    """
    if groupname:
        fieldname = groupname + "." + field["name"]
    else:
        fieldname = field["name"]
    # Kibana field types:
    # https://github.com/elastic/kibana/blob/master/src/ui/public/index_patterns/_field_types.js
    if field.get("type") in ["string", "date", "ip", "boolean"]:
        fieldtype = field.get("type")
    elif field.get("type") in ["integer", "long", "short", "byte", "float"]:
        fieldtype = "number"
    elif field.get("type") == "object":
        if "geo_point" == field.get("object_struct", {}).get("properties", {}).get("location", {}).get("type", ''):
            fieldtype = "geo_point"
        else:
            fieldtype = "string"
    elif field.get("type") == "nested":
        fieldtype = "string"
    else:
        print "Unknown field type. Skipped adding field %s" % (field)
    analyzed = field.get("index", "") == "analyzed"
    res = {
        "name": fieldname,
        "type": fieldtype,
        "count": 0,
        "scripted": False,
        "indexed": True,
        "analyzed": analyzed,
        "doc_values": field.get("doc_values", True)
    }
    return res


def add_type_version(version, obj_type):
    """replaces <version> placeholder in the template(index name and _meta)
    with the actual version number
    Args:
        version(str): version of the object
        obj_type(dict): dict of object_type where to replace the version
    """
    obj_type["_meta"]["version"] = version
    # template["template"] = template["template"].replace("<version>", version)


def add_index_pattern(pattern, template_skeleton):
    """Adds index pattern to the template, overwriting the previous index pattern
    Args:
        pattern(list): list of str, index patterns to be used in the template.
        template_skeleton(dict): template to operate upon.
    """
    template_skeleton['template'] = pattern


def add_index_order(order, template_skeleton):
    """Adds order to the template, overwriting the existing order value.
    Args:
        order(int): order value
        template_skeleton(dict): template to operate upon
    """
    template_skeleton['order'] = order


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('template_definition',
                   help='Path to input template')
    p.add_argument('namespaces_dir',
                   help='Path to directory with namespace definitions')

    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()

    with open(args.template_definition, 'r') as input_template:
        template_definition = yaml.load(input_template)

    with open('{0[elasticsearch_template][name]}.template.json'.format(
            template_definition), 'w') as output:
        with open('{0[elasticsearch_template][name]}.index-pattern.json'.format(
                template_definition), 'w') as output_index_pattern:
            object_types_to_template(template_definition, output, output_index_pattern, args.namespaces_dir)
