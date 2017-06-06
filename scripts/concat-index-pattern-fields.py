#!/usr/bin/env python

import sys
import json

doc = {}
for filename in sys.argv[1:]:
    with open(filename, "r") as ff:
        if doc:
            d2 = json.load(ff)
            d2fieldary = json.loads(d2['fields'])
            docfieldary = json.loads(doc['fields'])
            docfieldary.extend(d2fieldary)
            doc['fields'] = json.dumps(docfieldary)
        else:
            doc = json.load(ff)
sys.stdout.write(json.dumps(doc, indent=4, sort_keys=True))
