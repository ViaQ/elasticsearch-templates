import supported_versions as supported
import common_test_support


class GenerateTemplateTestCase(common_test_support.CommonTestSupport):

    def test_arguments(self):
        args = self.parser.parse_args(['template-test.yml', '../../namespaces/', '--docs'])
        self.assertEqual(args.template_definition, 'template-test.yml')
        self.assertEqual(args.namespaces_dir, '../../namespaces/')
        self.assertEqual(args.docs, True)

    def test_basic_transform_mapping_5x_to_2x(self):
        mapping1 = {
            'type': 'keyword'
        }
        supported._transform_mapping_5x_to_2x(mapping1)
        self.assertEqual('string', mapping1['type'])
        self.assertEqual('not_analyzed', mapping1['index'])

        mapping2 = {
            'type': 'text'
        }
        supported._transform_mapping_5x_to_2x(mapping2)
        self.assertEqual('string', mapping2['type'])
        self.assertEqual('analyzed', mapping2['index'])

        mapping3 = {
            'norms': True
        }
        supported._transform_mapping_5x_to_2x(mapping3)
        self.assertEqual(True, mapping3['norms']['enabled'])

        mapping4 = {
            'type': 'date',
            'index': True
        }
        supported._transform_mapping_5x_to_2x(mapping4)
        self.assertEqual('not_analyzed', mapping4['index'])

    def test_basic_transform_field_5x_to_2x(self):
        field = {
            "index": True
        }

        res5x = {
            "name": "foo",
            "type": "text",
            "count": 0,
            "scripted": False,
            "searchable": True,
            "aggregatable": True,
            "readFromDocValues": True
        }
        supported._transform_field_5x_to_2x(res5x, field)
        self.assertEqual(7, len(res5x.keys()))
        self.assertEqual(True, res5x["indexed"])
        self.assertEqual(True, res5x["doc_values"])
        self.assertEqual(True, res5x["analyzed"])
        self.assertEqual("string", res5x["type"])

        res5x = {
            "name": "foo",
            "type": "keyword",
            "count": 0,
            "scripted": False,
            "searchable": True,
            "aggregatable": True,
            "readFromDocValues": True
        }
        supported._transform_field_5x_to_2x(res5x, field)
        self.assertEqual("string", res5x["type"])

        res5x = {
            "name": "ipaddr4",
            "type": "ip",
            "count": 0,
            "scripted": False,
            "searchable": True,
            "aggregatable": True,
            "readFromDocValues": True
        }
        supported._transform_field_5x_to_2x(res5x, field)
        self.assertEqual("ip", res5x["type"])

        res5x = {
            "name": "ipaddr6",
            "type": "ip",
            "count": 0,
            "scripted": False,
            "searchable": True,
            "aggregatable": True,
            "readFromDocValues": True
        }
        supported._transform_field_5x_to_2x(res5x, field)
        self.assertEqual("string", res5x["type"])

        res5x = {
            "name": "foo.bar.ipaddr6",
            "type": "ip",
            "count": 0,
            "scripted": False,
            "searchable": True,
            "aggregatable": True,
            "readFromDocValues": True
        }
        supported._transform_field_5x_to_2x(res5x, field)
        self.assertEqual("string", res5x["type"])

    def test_basic_transform_skeleton_6x_to_5x(self):
        skeleton = {
            "index_patterns": "foo",
            "template": "noop"
        }
        supported._transform_skeleton_6x_to_5x(skeleton)
        self.assertEqual("foo", skeleton["template"])
        try:
            skeleton["index_patterns"]
        except KeyError:
            True
        except Exception:
            raise

    def test_index_type_name(self):
        self.assertEqual(supported._default_, supported.index_type_name(supported._es2x))
        self.assertEqual(supported._default_, supported.index_type_name(supported._es5x))
        self.assertEqual(supported._doc, supported.index_type_name(supported._es6x))
        self.assertRaises(Exception, supported.index_type_name, "foo")
