#!/usr/bin/env python

"""
This script generates the ES template file (*.template.json) from
the fields.yml file and skeleton.json.
The script is built upon the similar script from libbeats.

Example usage:

   python generate_template.py <template_definition> <template_name> <objects_folder>
"""

import sys
import yaml
import json


def object_types_to_template(template_definition, output, objects_dir):
    """
    Assemble objects for the particular template.
    """

    if template_definition is None:
        print "objects.yml is empty. Cannot generate template."
        return

    if 'skeleton_path' not in template_definition or\
       'types' not in template_definition:
        print "skeleton_path is not defined. Cannot generate template."
        return

    # Load skeleton of the template
    with open(template_definition['skeleton_path'], 'r') as f:
        skeleton = yaml.load(f)

    src_files = {}
    res = {}

    # Load object_type files
    with open(objects_dir + '/_default_.yml', 'r') as f:
        src_files['_default_'] = yaml.load(f)
    map_types = [('_default_', '_default_')]

    for type_file in template_definition['types']:
        with open(objects_dir + type_file, 'r') as f:
            src_files[type_file] = yaml.load(f)
        for section in src_files[type_file]:
            # Prepare skeleton adding empty sections for each mapping type
            if section not in ["version", "defaults", "doc_sections"]:
                map_types.append((section, type_file))

    for map_type, type_file in map_types:
        add_mapping_to_skeleton(map_type, skeleton)

        # Entry point to parsing of the source files.
        # Inserting parsed data into the skeleton.
        skeleton['mappings'][map_type]['properties'] =\
         fields_to_object_type(src_files[type_file], map_type)

        add_type_version(src_files[type_file]["version"],
                         skeleton['mappings'][map_type])

    add_index_pattern(template_definition['elasticsearch_template']['index_pattern'], skeleton)
    add_index_order(template_definition['elasticsearch_template']['order'], skeleton)

    json.dump(skeleton, output,
              indent=2, separators=(',', ': '),
              sort_keys=True)


def add_mapping_to_skeleton(map_type, skeleton):
    """Add mapping type to the skeleton by cloning '_default_' section.
    Args:
        map_type(str): name of the document type to add
        skeleton(dict): skeleton to update
    """
    if map_type != '_default_':
        skeleton['mappings'][map_type] = skeleton['mappings']['_default_'].copy()
        del skeleton['mappings'][map_type]['dynamic_templates']


def fields_to_object_type(obj_type, mapping_type):
    """
    Reads the YAML file from input and generates the JSON for
    the ES template in output. input and output are both file
    pointers.
    Args:
        obj_type(dict): dict definition loaded from object_type file
        mapping_type(string): what mapping type to parse
    Returns:
        dict of processed mapping type
    """

    # No fields defined, can't generate template
    if obj_type is None:
        print "object_type file is empty. Cannot generate template."
        return

    # Each template needs defaults
    if "defaults" not in obj_type.keys():
        print "No defaults are defined. Each type needs at least some defaults defined."
        return

    defaults = obj_type['defaults']
    return traverse_group_section(obj_type[mapping_type], defaults)


def traverse_group_section(group, defaults):
    """
    Traverse the sections tree and fill in the properties
    map.
    Args:
        group(dict): field of type group, that has mutiple subfields under
    'fields' key.
        defaults(dict): dict with the defaults for all fields
    Returns:
        dict of individual members of the group.
    """
    properties = {}

    # print "Trying to fill section properties of section %s" % (group)
    try:
        for field in group["fields"]:
            prop = traverse_field(field, defaults)
            properties.update(prop)
    except KeyError:
        print "Skipping empty section %s" % (group)
    # print "Section filled with properties: %s" % (properties)
    return properties


def traverse_field(field, defaults):
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

    # TODO: Make this more dyanmic

    if field.get("type") == "group":
        prop = traverse_group_section(field, defaults)

        # Only add properties if they have a content
        if len(prop) is not 0:
            properties[field.get("name")] = {"properties": {}}
            properties[field.get("name")]["properties"] = prop
    else:
        properties = process_leaf(field, defaults)

    # print "Result of traversing field is : %s" % (properties)
    return properties


def process_leaf(field, defaults):
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
                             "boolean", "nested"]:
        res[field["name"]] = working_field.copy()
        res[field.get("name")].update(process_subleaf(field, defaults))
    elif field.get("type") == "object":
        if "object_struct" in field:
            res[field["name"]] = working_field["object_struct"].copy()
        else:
            res[field["name"]] = {}
        res[field["name"]]["type"] = "object"
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
        prop = traverse_group_section(field, defaults)
        if len(prop) is not 0:
            properties["fields"] = prop
    return properties


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

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print "Usage: %s template_definition templatename objectsdir" % sys.argv[0]
        sys.exit(1)

    definition_path = sys.argv[1]
    objects_dir = sys.argv[2]

    input_template = open(definition_path, 'r')
    template_definition = yaml.load(input_template)
    try:
        output = open(template_definition['elasticsearch_template']['name'] + ".template.json",
                      'w')
        object_types_to_template(template_definition,  output, objects_dir)
    finally:
        input_template.close()
        output.close()
