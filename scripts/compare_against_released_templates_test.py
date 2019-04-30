import generate_template
import json
import yaml
import os
import io
import supported_versions as supported
import common_test_support as helper


class CompareAgainstReleasedTemplatesTestCase(helper.CommonTestSupport):

    _index_template_viaq_os_operations = helper._release_download_path + \
        helper._v0_0_12 + \
        "/com.redhat.viaq-openshift-operations.template.json"

    _index_template_viaq_os_project = helper._release_download_path + \
        helper._v0_0_12 + \
        "/com.redhat.viaq-openshift-project.template.json"

    _index_template_viaq_collectd = helper._release_download_path + \
        helper._v0_0_12 + \
        "/org.ovirt.viaq-collectd.template.json"

    def test_compare_index_template_viaq_os_operations(self):
        args = self.parser.parse_args(['../templates/openshift/template-operations.yml', '../namespaces/'])
        json_url = self._index_template_viaq_os_operations
        self._support_compare_index_templates(args, json_url)

    def test_compare_index_index_template_viaq_os_project(self):
        args = self.parser.parse_args(['../templates/openshift/template-project.yml', '../namespaces/'])
        json_url = self._index_template_viaq_os_project
        self._support_compare_index_templates(args, json_url)

    def test_compare_index_index_template_viaq_collectd(self):
        args = self.parser.parse_args(['../templates/collectd_metrics/template.yml', '../namespaces/'])
        json_url = self._index_template_viaq_collectd
        self._support_compare_index_templates(args, json_url)

    def _support_compare_index_templates(self, args, json_url):

        with open(args.template_definition, 'r') as input_template:
            template_definition = yaml.load(input_template, Loader=yaml.FullLoader)

        # We need to update paths 'cos this test is started from different folder
        template_definition['skeleton_path'] = '../templates/skeleton.json'
        template_definition['skeleton_index_pattern_path'] = '../templates/skeleton-index-pattern.json'

        output = io.StringIO()
        output_index_pattern = io.open(os.devnull, 'w')

        generate_template.object_types_to_template(template_definition,
                                                   output, output_index_pattern,
                                                   supported._es2x,
                                                   args.namespaces_dir)

        generated_json = json.loads(output.getvalue())
        output.close()
        output_index_pattern.close()

        # Mask version
        generated_json["mappings"]["_default_"]["_meta"]["version"] = "na"

        # Fix generated data:
        # ======================
        # VM Memory stats were added after 0.0.12 release
        # https://github.com/ViaQ/elasticsearch-templates/issues/85
        if "collectd" in generated_json["mappings"]["_default_"]["properties"]:
            vm_memory_keys = []
            for metric_key in generated_json["mappings"]["_default_"]["properties"]["collectd"]["properties"]["statsd"]["properties"].keys():
                if metric_key.startswith("vm_memory"):
                    vm_memory_keys.append(metric_key)
            for k in vm_memory_keys:
                del generated_json["mappings"]["_default_"]["properties"]["collectd"]["properties"]["statsd"]["properties"][k]
        # viaq_msg_id is a new field: https://github.com/ViaQ/elasticsearch-templates/pull/90
        if 'viaq_msg_id' in generated_json['mappings']['_default_']['properties']:
            del generated_json['mappings']['_default_']['properties']['viaq_msg_id']

        # https://github.com/ViaQ/elasticsearch-templates/issues/94
        if 'ovirt' in generated_json["mappings"]["_default_"]["properties"]:
            del generated_json["mappings"]["_default_"]["properties"]["ovirt"]["properties"]["class"]
            del generated_json["mappings"]["_default_"]["properties"]["ovirt"]["properties"]["module_lineno"]
            del generated_json["mappings"]["_default_"]["properties"]["ovirt"]["properties"]["thread"]
            del generated_json["mappings"]["_default_"]["properties"]["ovirt"]["properties"]["correlationid"]
        # ======================

        generated_index_template = self._sort(generated_json)
        # print(generated_index_template)

        # ---- wget
        released_data = self._wget(json_url)

        # Mask version
        released_data["mappings"]["_default_"]["_meta"]["version"] = "na"

        # Fix downloaded data:
        # ======================
        # We need to clean some diffs that we know exists today but they are either
        # fine to ignore or there is an open ticket that has fix pending.

        # https://github.com/ViaQ/elasticsearch-templates/issues/87
        released_data["aliases"] = { ".all": {} }
        # https://github.com/ViaQ/elasticsearch-templates/issues/69
        del released_data["mappings"]["_default_"]["dynamic_templates"][0]["message_field"]["mapping"]["omit_norms"]
        released_data["mappings"]["_default_"]["dynamic_templates"][0]["message_field"]["mapping"]["norms"] = { 'enabled' : False }
        #  - on top of #69 norms were enabled for general string fields
        del released_data["mappings"]["_default_"]["dynamic_templates"][1]["string_fields"]["mapping"]["omit_norms"]
        released_data["mappings"]["_default_"]["dynamic_templates"][1]["string_fields"]["mapping"]["norms"] = { 'enabled' : True }

        # https://github.com/ViaQ/elasticsearch-templates/issues/83
        new_order = [2, 3, 4, 0, 1]
        reordered_dynamic_templates = [ released_data["mappings"]["_default_"]["dynamic_templates"][i] for i in new_order ]
        released_data["mappings"]["_default_"]["dynamic_templates"] = reordered_dynamic_templates

        # https://github.com/ViaQ/elasticsearch-templates/issues/69#issuecomment-357276665
        del released_data["mappings"]["_default_"]["properties"]["ipaddr4"]["norms"]

        # https://github.com/ViaQ/elasticsearch-templates/issues/78
        released_data["mappings"]["_default_"]["properties"]["kubernetes"]["properties"]["container_name"]["index"] = "analyzed"
        released_data["mappings"]["_default_"]["properties"]["kubernetes"]["properties"]["container_name"]["doc_values"] = False

        # https://github.com/ViaQ/elasticsearch-templates/issues/79
        del released_data["mappings"]["_default_"]["properties"]["pipeline_metadata"]["properties"]["collector"]["properties"]["ipaddr4"]["norms"]
        released_data["mappings"]["_default_"]["properties"]["pipeline_metadata"]["properties"]["collector"]["properties"]["ipaddr4"]["type"] = "ip"

        # https://github.com/ViaQ/elasticsearch-templates/issues/82
        del released_data["mappings"]["_default_"]["properties"]["pipeline_metadata"]["properties"]["normalizer"]["properties"]["ipaddr4"]["norms"]

        # https://github.com/ViaQ/elasticsearch-templates/issues/80
        if 'aushape' in released_data["mappings"]["_default_"]["properties"]:
            released_data["mappings"]["_default_"]["properties"]["aushape"]["properties"]["error"]["index"] = "analyzed"
            released_data["mappings"]["_default_"]["properties"]["aushape"]["properties"]["error"]["doc_values"] = False
        # ======================

        released_index_template = self._sort(released_data)

        self.assertEqual(released_index_template, generated_index_template)
