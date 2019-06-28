import generate_template
import json
import yaml
import os
import io
import supported_versions as supported
import common_test_support as helper


class CompareAgainstReleasedTemplatesTestCase(helper.CommonTestSupport):

    _index_template_viaq_os_operations_v0018_2x = helper._release_download_path + \
        helper._v0_0_18 + \
        "/com.redhat.viaq-openshift-operations." + supported._es2x + \
        ".template.json"

    _index_template_viaq_os_project_v0018_2x = helper._release_download_path + \
        helper._v0_0_18 + \
        "/com.redhat.viaq-openshift-project." + supported._es2x + \
        ".template.json"

    _index_template_viaq_collectd_v0018_2x = helper._release_download_path + \
        helper._v0_0_18 + \
        "/org.ovirt.viaq-collectd." + supported._es2x + \
        ".template.json"

    _index_template_viaq_os_operations_v0018_5x = helper._release_download_path + \
        helper._v0_0_18 + \
        "/com.redhat.viaq-openshift-operations." + supported._es5x + \
        ".template.json"

    _index_template_viaq_os_project_v0018_5x = helper._release_download_path + \
        helper._v0_0_18 + \
        "/com.redhat.viaq-openshift-project." + supported._es5x + \
        ".template.json"

    _index_template_viaq_collectd_v0018_5x = helper._release_download_path + \
        helper._v0_0_18 + \
        "/org.ovirt.viaq-collectd." + supported._es5x + \
        ".template.json"

    _index_template_viaq_os_operations_v0012 = helper._release_download_path + \
        helper._v0_0_12 + \
        "/com.redhat.viaq-openshift-operations.template.json"

    _index_template_viaq_os_project_v0012 = helper._release_download_path + \
        helper._v0_0_12 + \
        "/com.redhat.viaq-openshift-project.template.json"

    _index_template_viaq_collectd_v0012 = helper._release_download_path + \
        helper._v0_0_12 + \
        "/org.ovirt.viaq-collectd.template.json"

    def test_compare_index_template_viaq_os_operations(self):
        args = self.parser.parse_args(['../templates/openshift/template-operations.yml', '../namespaces/'])
        json_url = self._index_template_viaq_os_operations_v0018_2x
        self._support_compare_index_templates(args, json_url, supported._es2x)
        json_url = self._index_template_viaq_os_operations_v0018_5x
        self._support_compare_index_templates(args, json_url, supported._es5x)

    def test_compare_index_index_template_viaq_os_project(self):
        args = self.parser.parse_args(['../templates/openshift/template-project.yml', '../namespaces/'])
        json_url = self._index_template_viaq_os_project_v0018_2x
        self._support_compare_index_templates(args, json_url, supported._es2x)
        json_url = self._index_template_viaq_os_project_v0018_5x
        self._support_compare_index_templates(args, json_url, supported._es5x)

    def test_compare_index_index_template_viaq_collectd(self):
        args = self.parser.parse_args(['../templates/collectd_metrics/template.yml', '../namespaces/'])
        json_url = self._index_template_viaq_collectd_v0018_2x
        self._support_compare_index_templates(args, json_url, supported._es2x)
        json_url = self._index_template_viaq_collectd_v0018_5x
        self._support_compare_index_templates(args, json_url, supported._es5x)

    def test_compare_index_template_viaq_os_operations_v0012(self):
        args = self.parser.parse_args(['../templates/openshift/template-operations.yml', '../namespaces/'])
        json_url = self._index_template_viaq_os_operations_v0012
        self._support_compare_index_templates_v0012(args, json_url)

    def test_compare_index_index_template_viaq_os_project_v0012(self):
        args = self.parser.parse_args(['../templates/openshift/template-project.yml', '../namespaces/'])
        json_url = self._index_template_viaq_os_project_v0012
        self._support_compare_index_templates_v0012(args, json_url)

    def test_compare_index_index_template_viaq_collectd_v0012(self):
        args = self.parser.parse_args(['../templates/collectd_metrics/template.yml', '../namespaces/'])
        json_url = self._index_template_viaq_collectd_v0012
        self._support_compare_index_templates_v0012(args, json_url)

    def _generate_json_index_template(self, args, json_url, es_version):
        """

        :param self
        :param args         An argument line to parse
        :param json_url     URL of released JSON file to download
        :param es_version   Version of supported ES to generate index template for
        """
        with open(args.template_definition, 'r') as input_template:
            template_definition = yaml.load(input_template, Loader=yaml.FullLoader)

        # We need to update paths 'cos this test is started from different folder
        template_definition['skeleton_path'] = '../templates/skeleton.json'
        template_definition['skeleton_index_pattern_path'] = '../templates/skeleton-index-pattern.json'

        output = io.StringIO()
        output_index_pattern = io.open(os.devnull, 'w')

        generate_template.object_types_to_template(template_definition,
                                                   output, output_index_pattern,
                                                   es_version,
                                                   args.namespaces_dir)

        generated_json = json.loads(output.getvalue())
        output.close()
        output_index_pattern.close()

        return generated_json

    def _support_compare_index_templates(self, args, json_url, es_version):
        # --- generate data
        generated_json = self._generate_json_index_template(args, json_url, es_version)

        # Mask version
        generated_json["mappings"]["_default_"]["_meta"]["version"] = "na"
        generated_index_template = self._sort(generated_json)
        # print(generated_index_template)

        # ---- wget release data
        released_data = self._wget(json_url)

        # Mask version
        released_data["mappings"]["_default_"]["_meta"]["version"] = "na"
        released_index_template = self._sort(released_data)

        self.assertEqual(released_index_template, generated_index_template)

    def _support_compare_index_templates_v0012(self, args, json_url):
        """
        THE LEGACY METHOD
        Compares the generated model against released model 0.0.12.
        The model 0.0.12 was the last one before we started supporting multiple ES versions.
        Once we upgrade logging to model 0.0.18 or higher consider getting rid of this method.
        """
        generated_json = self._generate_json_index_template(args, json_url, supported._es2x)

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

        # https://github.com/ViaQ/elasticsearch-templates/commit/b3db410bc93144a94ac0acfa0312de4efc313973
        if 'docker' in generated_json["mappings"]["_default_"]["properties"]:
            del generated_json["mappings"]["_default_"]["properties"]["docker"]["properties"]["container_name"]

        # https://github.com/ViaQ/elasticsearch-templates/pull/106
        if 'systemd' in generated_json["mappings"]["_default_"]["properties"]:
            del generated_json["mappings"]["_default_"]["properties"]["systemd"]["properties"]["t"]["properties"]["LINE_BREAK"]
            del generated_json["mappings"]["_default_"]["properties"]["systemd"]["properties"]["t"]["properties"]["STREAM_ID"]
            del generated_json["mappings"]["_default_"]["properties"]["systemd"]["properties"]["t"]["properties"]["SYSTEMD_INVOCATION_ID"]
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

        # We need to remove the `include_in_all` from downloaded model because this setting has been removed.
        # https://github.com/ViaQ/elasticsearch-templates/issues/102
        if 'collectd' in released_data["mappings"]["_default_"]["properties"]:
            for metric_key in released_data["mappings"]["_default_"]["properties"]["collectd"]["properties"].keys():
                metric = released_data["mappings"]["_default_"]["properties"]["collectd"]["properties"][metric_key]
                if 'include_in_all' in metric:
                    metric.pop('include_in_all')
        # ======================

        released_index_template = self._sort(released_data)

        self.assertEqual(released_index_template, generated_index_template)
