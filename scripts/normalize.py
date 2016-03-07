#!/usr/bin/env python

import sys
import json
import re

r = re.compile(r"\s+$", re.MULTILINE)

with open(sys.argv[1], "r") as inf:
    doc = json.load(inf)
txt = json.dumps(doc, indent=4, sort_keys=True)
txt = r.sub("", txt)
if txt[-1] != '\n':
    txt = txt + '\n'
sys.stdout.write(txt)
