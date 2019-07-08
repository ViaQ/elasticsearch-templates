#!/usr/bin/env python

""" This script creates one (cumulative) index pattern file per supported ES version.
See the parse_args() method for required arguments.

Notice, this script was called "concat-index-pattern-fields.py" in the past but it was not possible
to import this script into test due to use of dashes. Renaming this file to "concat_index_pattern_fields.py"
solved this issue.
"""

import argparse
import glob
import os
import io
import json
import supported_versions as supported


def removedupnames(fieldary, names):
    ret = []
    for field in fieldary:
        if not field['name'] in names:
            names[field['name']] = True
            ret.append(field)
    return ret


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('index_pattern_dirs',
                   help='Comma delimited names of folders containing index pattern files')
    p.add_argument('index_pattern',
                   help='Path used to filter index pattern file(s) (use quotes if expandable path expressions are used)')
    p.add_argument('output_file_name',
                   help='Name of the output file. First substring "<ES_VERSION>" is replaced with ES version. Use quotes. Eg. "com.redhat.viaq-openshift.<ES_VERSION>.index-pattern.json"')

    # Do not call parse_args() on parser yet so that we can use it in unittests
    return p


def filter_index_pattern_files(dirs, index_pattern, substr):
    """
    Return list of files from given dirs that match index_pattern and contain es_ver in its name.
    :param dirs: Comma delimited list of folder names
    :param index_pattern: expandable files name pattern (eg. "*.index_pattern.json")
    :param substr: substring that every file name must contain
    :return:
    """
    files = []
    for folder in dirs.split(','):
        for file in glob.glob(os.path.join(folder, index_pattern)):
            if substr in file:
                files.append(file)
    return files


def concatenate_index_pattern_files(files, output):
    """Read fields from all input files and write cumulative result into output.
    :param files: Individual index pattern files to concatenate
    :param output: Opened file for writing the result into
    """
    doc = {}
    names = {}
    for filename in files:
        with io.open(filename, "r") as ff:
            if doc:
                d2 = json.load(ff)
                d2fieldary = removedupnames(json.loads(d2['fields']), names)
                docfieldary = json.loads(doc['fields'])
                docfieldary.extend(d2fieldary)
                doc['fields'] = json.dumps(docfieldary)
            else:
                doc = json.load(ff)
                docfieldary = removedupnames(json.loads(doc['fields']), names)
                doc['fields'] = json.dumps(docfieldary)
    json_str = json.dumps(doc, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
    output.write(json_str)
    output.write(u'\n')


if __name__ == '__main__':
    args = parse_args().parse_args()

    for es_version in supported.elasticsearch:
        pattern_files = filter_index_pattern_files(args.index_pattern_dirs, args.index_pattern, es_version)
        print("Found index pattern files for ES version:", es_version, pattern_files)

        output_file = args.output_file_name.replace("<ES_VERSION>", es_version)
        print("Cumulative index pattern goes to file >", output_file)

        with io.open(output_file, mode='w', encoding='utf8') as output:
            concatenate_index_pattern_files(pattern_files, output)
