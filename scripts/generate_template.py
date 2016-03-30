#!/usr/bin/env python

"""
This script generates the ES template file (*.template.json) from
the fields.yml file and skeleton.json.
The script is built upon the similar script from libbeats.

Example usage:

   python generate_template.py viaq-template com.redhat.viaq-template
"""

import sys
import yaml
import json


def fields_to_es_template(input, skeleton, output):
    """
    Reads the YAML file from input and generates the JSON for
    the ES template in output. input and output are both file
    pointers.
    """

    # Custom properties
    docs = yaml.load(input)

    # No fields defined, can't generate template
    if docs is None:
        print "fields.yml is empty. Cannot generate template."
        return

    # Remove sections as only needed for docs
    if "doc_sections" in docs.keys():
        del docs["doc_sections"]

    # Each template needs defaults
    if "defaults" not in docs.keys():
        print "No defaults are defined. Each template needs at least defaults defined."
        return


    # Load skeleton
    template = json.load(skeleton)

    # Prepare skeleton adding empty sections for each mapping type
    for map_type in docs.keys():
        if map_type not in ["version", "defaults"]:
            if map_type != "_default_":
                template["mappings"][map_type] = template["mappings"]["_default_"].copy()
                del template["mappings"][map_type]["dynamic_templates"]

    for map_type in docs.keys():
        if map_type not in ["version", "defaults"]:
            fields_to_mappings(docs, template, map_type)

    add_template_version(docs["version"],template)

    json.dump(template, output,
              indent=2, separators=(',', ': '),
              sort_keys=True)

def fields_to_mappings(source, template, mapping_type):
    """ fill mapping 'properties' for the provided mapping_type"""
    defaults = source["defaults"]

    prop = fill_section_properties(source[mapping_type], defaults)
    template["mappings"][mapping_type]["properties"] = prop



def fill_section_properties(section, defaults):
    """
    Traverse the sections tree and fill in the properties
    map.
    """
    properties = {}

    #print "Trying to fill section properties of section %s"%(section)
    try:
        for field in section["fields"]:
            prop = fill_field_properties(field, defaults)
            properties.update(prop)
    except TypeError:
        print "Skipping empty section %s" % (section)
    return properties


def fill_field_properties(field, defaults):
    """
    Add data about a particular field in the properties
    map.
    """
    properties = {}
    #print "current field is %s"%(field)

    # working copy that actually will be used to enter data in template, "field" variable will stay unmodified
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

    # TODO: Make this more dyanmic
    if field.get("index") == "analyzed":
        properties[field["name"]] = {
            "type": working_field["type"],
            "index": "analyzed",
            "norms": {
                "enabled": False
            }
        }
    elif field.get("type") in ["string", "date", "ip", "integer", "long"]:
        properties[field["name"]] = working_field.copy()
        properties[field.get("name")].update(fill_subfields(field, defaults))
    elif field.get("type") == "object":
        if "object_struct" in field:
             properties[field["name"]] = working_field["object_struct"].copy()
        else:
            properties[field["name"]] = {}
        properties[field["name"]]["type"] = "object"
    elif field.get("type") == "float":
        properties[field["name"]] = {
            "type": "float",
            "doc_values": "true"
        }
    elif field.get("type") == "group":
        prop = fill_section_properties(field, defaults)

        # Only add properties if they have a content
        if len(prop) is not 0:
            properties[field.get("name")] = {"properties": {}}
            properties[field.get("name")]["properties"] = prop
    else:
        print "Skipped adding field %s"%(field)

    return properties

def fill_subfields(field, defaults):
    """returns dict with "field" subfields if "field" exists"""
    properties = {}
    if field.get("fields"):
        prop = fill_section_properties(field, defaults)
        if len(prop) is not 0:
            properties["fields"] = prop
    return properties

def add_template_version(version,template):
    """replaces <version> placeholder in the template(index name and _meta) with the actual version number"""
    template["mappings"]["_default_"]["_meta"]["version"] = version
    template["template"] = template["template"].replace("<version>", version) 

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print "Usage: %s templatepath templatename" % sys.argv[0]
        sys.exit(1)

    template_path = sys.argv[1]
    template_name = sys.argv[2]

    input = open(template_path + "/fields.yml", 'r')
    skeleton_template = open(template_path + "/skeleton.json", 'r')
    output = open(template_path + "/" + template_name + ".template.json", 'w')

    try:
        fields_to_es_template(input, skeleton_template, output)
    finally:
        input.close()
        output.close()
