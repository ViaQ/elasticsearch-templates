import yaml
import sys


def document_fields(output, section, sections):

    if "anchor" in section:
        output.write("[[exported-fields-{}]]\n".format(section["anchor"]).encode('utf-8'))
    output.write("=== {} Fields\n\n".format(section["name"]).encode('utf-8'))

    if "description" in section:
        output.write("{}\n\n".format(section["description"]).encode('utf-8'))

    if "fields" not in section or not section["fields"]:
        return

    output.write("\n".encode('utf-8'))
    for field in section["fields"]:

        if "type" in field and field["type"] == "group":

            for value in sections:
                sec = value[0]
                name = value[1]
                if sec == field["name"]:
                    field["anchor"] = field["name"]
                    field["name"] = name
                    break
            document_fields(output, field, sections)
        else:
            document_field(output, field)


def document_field(output, field):

    if "path" not in field:
        field["path"] = field["name"]

    output.write("==== {}\n\n".format(field["path"]))

    if "type" in field:
        output.write("type: {}\n\n".format(field["type"]))
    if "example" in field:
        output.write("example: {}\n\n".format(field["example"]))
    if "format" in field:
        output.write("format: {}\n\n".format(field["format"].encode('utf-8')))
    if "required" in field:
        output.write("required: {}\n\n".format(field["required"].encode('utf-8')))

    if "description" in field:
        output.write("{}\n\n".format(field["description"].encode("utf-8")))


def fields_to_asciidoc(input, output, template_name):

    dict = {'product': template_name}

    output.write("""
////
This file is generated! See fields.yml and scripts/generate_field_docs.py
////

[[exported-fields]]
== Exported Fields

This document describes the fields that are exported by {product}. They are
grouped in the following categories:

""".encode("UTF-8").format(**dict))


    docs = yaml.load(input)

    # fields file is empty
    if docs is None:
        print("fields.yml file is empty. fields.adoc cannot be generated.")
        return

    # If no sections are defined, docs can't be generated
    if "doc_sections" not in docs.keys():
        print("doc_sections is not defined in fields.yml. fields.adoc cannot be generated.")
        return

    sections = docs["doc_sections"]

    # Check if sections is define
    if sections is None:
        print("No doc_sections are defined in fields.yml. fields.adoc cannot be generated.")
        return

    for doc, _ in sections:
        output.write("* <<exported-fields-{}>>\n".format(doc).encode('utf-8'))
    output.write("\n".encode('utf-8'))

    for value in sections:

        doc = value[0]
        name = value[1]

        if doc in docs:
            section = docs[doc]
            if "type" in section:
                if section["type"] == "group":
                    section["name"] = name
                    section["anchor"] = doc
                    document_fields(output, section, sections)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: %s path templatename" % sys.argv[0])
        sys.exit(1)

    template_path = sys.argv[1]
    template_name = sys.argv[2]

    f_input = open(template_path + "/fields.yml", 'r')
    f_output = open(template_path + "/" + template_name + ".adoc", 'wb')

    try:
        fields_to_asciidoc(f_input, f_output, template_name.title())
    finally:
        f_input.close()
        f_output.close()
