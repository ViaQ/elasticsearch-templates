import unittest
import generate_template
import pprint
import json
import sys
import io
import codecs
try:
    import urllib.request
except ImportError:
    import urllib3.request

_release_download_path = "https://github.com/ViaQ/elasticsearch-templates/releases/download/"
_v0_0_12 = "0.0.12"
_v0_0_19 = "0.0.19"

class CommonTestSupport(unittest.TestCase):
    """Class to be used as a parent for various tests. It provides useful methods."""

    def setUp(self):
        self.parser = generate_template.parse_args()

    def _pretty_print_json(self, json_data):
        """Pretty print of json to stdout"""
        json.dump(json_data, sys.stdout, indent=2, separators=(',', ': '), sort_keys=True)

    def _pretty_print_dict(self, dict_data):
        """Pretty print of dict to stdout"""
        pp = pprint.PrettyPrinter(indent=1)
        pp.pprint(dict_data)

    def _sort(self, json_data):
        """Sort json using json.dump() method. Useful for comparing json data."""
        _io = io.StringIO()
        json.dump(json_data, _io, separators=(',', ': '), sort_keys=True)
        out = _io.getvalue()
        _io.close()
        return out

    def _wget(self, url):
        """Download JSON data from given url and return as a json object."""
        print("wget", url)
        response = urllib.request.urlopen(url)
        print("\nHTTPResponse code:", response.getcode())
        print("HTTPResponse info:")
        print(response.info())
        reader = codecs.getreader("utf-8")
        return json.load(reader(response))

    def _from_string_to_json(self, value):
        return json.loads(value)

    def _json_from_file(self, path):
        _io = io.open(path)
        _json = json.load(_io)
        _io.close()
        return _json
