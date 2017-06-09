#!/usr/bin/env python

import sys
import json

doc = {}
names = {}

def removedupnames(fieldary):
    ret = []
    for field in fieldary:
        if not field['name'] in names:
            names[field['name']] = True
            ret.append(field)
    return ret

for filename in sys.argv[1:]:
    with open(filename, "r") as ff:
        if doc:
            d2 = json.load(ff)
            d2fieldary = removedupnames(json.loads(d2['fields']))
            docfieldary = json.loads(doc['fields'])
            docfieldary.extend(d2fieldary)
            doc['fields'] = json.dumps(docfieldary)
        else:
            doc = json.load(ff)
            docfieldary = removedupnames(json.loads(doc['fields']))
            doc['fields'] = json.dumps(docfieldary)
sys.stdout.write(json.dumps(doc, indent=4, sort_keys=True, separators=(',', ': ')))
sys.stdout.write('\n')
