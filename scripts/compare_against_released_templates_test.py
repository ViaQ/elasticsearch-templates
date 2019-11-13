import generate_template
import json
import yaml
import os
import io
import sys
import supported_versions as supported
import common_test_support as helper


class CompareAgainstReleasedTemplatesTestCase(helper.CommonTestSupport):

    _0_12_download_prefix = helper._release_download_path + helper._v0_0_12
    _0_19_download_prefix = helper._release_download_path + helper._v0_0_19

    _testing_matrix = {
        supported._es2x: {
            "openshift-operations_from_rel_0_12": {
                "released_file_url": "/".join((_0_12_download_prefix, "com.redhat.viaq-openshift-operations.template.json")),
                "template_path": "../templates/openshift/template-operations.yml"
            },
            "openshift-project_from_rel_0_12": {
                "released_file_url": "/".join((_0_12_download_prefix, "com.redhat.viaq-openshift-project.template.json")),
                "template_path": "../templates/openshift/template-project.yml"
            },
            "collectd-metrics_from_rel_0_12": {
                "released_file_url": "/".join((_0_12_download_prefix, "org.ovirt.viaq-collectd.template.json")),
                "template_path": "../templates/collectd_metrics/template.yml"
            }
        },
        supported._es5x: {
            "openshift-operations": {
                "released_file_url": "/".join((_0_19_download_prefix,
                                               ".".join(("com.redhat.viaq-openshift-operations",
                                                         supported._es5x, "template.json"))
                                               )),
                "template_path": "../templates/openshift/template-operations.yml"
            },
            "openshift-project": {
                "released_file_url": "/".join((_0_19_download_prefix,
                                               ".".join(("com.redhat.viaq-openshift-project",
                                                         supported._es5x, "template.json"))
                                               )),
                "template_path": "../templates/openshift/template-project.yml"
            },
            "collectd-metrics": {
                "released_file_url": "/".join((_0_19_download_prefix,
                                               ".".join(("org.ovirt.viaq-collectd",
                                                         supported._es5x, "template.json"))
                                               )),
                "template_path": "../templates/collectd_metrics/template.yml"
            }
        }
    }

    def test_all_index_templates(self):
        for version in self._testing_matrix.keys():
            print()  # nice formatting
            print(' ~~~~~~~~~~~~~~~~~~ ')
            for test_conf in self._testing_matrix[version].keys():
                print('Running test from matrix. Model version: {}, test conf: {}'.format(version, test_conf))
                args = self.parser.parse_args(
                    [self._testing_matrix[version][test_conf]['template_path'], '../namespaces/']
                )
                json_url = self._testing_matrix[version][test_conf]['released_file_url']
                self._support_compare_index_templates(version, args, json_url)
                print()

    @staticmethod
    def _remove_include_in_all(released_data, es_version):
        # We need to remove the `include_in_all` from downloaded model because this setting was removed.
        # https://github.com/ViaQ/elasticsearch-templates/issues/102
        _idx_type = supported.index_type_name(es_version)
        if 'collectd' in released_data["mappings"][_idx_type]["properties"]:
            for metric_key in released_data["mappings"][_idx_type]["properties"]["collectd"]["properties"].keys():
                metric = released_data["mappings"][_idx_type]["properties"]["collectd"]["properties"][metric_key]
                if 'include_in_all' in metric:
                    metric.pop('include_in_all')

    @staticmethod
    def _remove_all_field(data, es_version):
        # We remove `_all` field in all models when rendering for ES 6.x and later.
        # We need to keep use of this field in templates for ES 5.x and earlier. We need to keep doing this as long
        # as we want to support older data models.
        # https://github.com/ViaQ/elasticsearch-templates/issues/46
        _idx_type = supported.index_type_name(es_version)
        if "_all" in data["mappings"][_idx_type]:
            del data["mappings"][_idx_type]["_all"]
        
    @staticmethod
    def _remove_viaq_index_name_field(generated_json, es_version):
        # Remove 'viaq_index_name' field. It was introduced after support for ES6.x was added.
        # https://github.com/ViaQ/elasticsearch-templates/pull/115
        _idx_type = supported.index_type_name(es_version)
        if "viaq_index_name" in generated_json["mappings"][_idx_type]["properties"]:
            del generated_json["mappings"][_idx_type]["properties"]["viaq_index_name"]

    @staticmethod
    def _generate_json_index_template(args, es_version):
        """
        :param args         An argument line to parse
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

    def _support_compare_index_templates(self, es_version, args, json_url):
        _idx_type = supported.index_type_name(es_version)
        # --- generate data
        generated_json = self._generate_json_index_template(args, es_version)

        # Mask version
        generated_json["mappings"][_idx_type]["_meta"]["version"] = "na"

        # Fix generated data:
        # ======================
        if es_version == supported._es2x:
            # VM Memory stats were added after 0.0.12 release
            # https://github.com/ViaQ/elasticsearch-templates/issues/85
            if "collectd" in generated_json["mappings"][_idx_type]["properties"]:
                vm_memory_keys = []
                for metric_key in generated_json["mappings"][_idx_type]["properties"]["collectd"]["properties"]["statsd"]["properties"].keys():
                    if metric_key.startswith("vm_memory"):
                        vm_memory_keys.append(metric_key)
                for k in vm_memory_keys:
                    del generated_json["mappings"][_idx_type]["properties"]["collectd"]["properties"]["statsd"]["properties"][k]
            # viaq_msg_id is a new field: https://github.com/ViaQ/elasticsearch-templates/pull/90
            if 'viaq_msg_id' in generated_json['mappings'][_idx_type]['properties']:
                del generated_json['mappings'][_idx_type]['properties']['viaq_msg_id']

            # https://github.com/ViaQ/elasticsearch-templates/issues/94
            if 'ovirt' in generated_json["mappings"][_idx_type]["properties"]:
                del generated_json["mappings"][_idx_type]["properties"]["ovirt"]["properties"]["class"]
                del generated_json["mappings"][_idx_type]["properties"]["ovirt"]["properties"]["module_lineno"]
                del generated_json["mappings"][_idx_type]["properties"]["ovirt"]["properties"]["thread"]
                del generated_json["mappings"][_idx_type]["properties"]["ovirt"]["properties"]["correlationid"]

            # https://github.com/ViaQ/elasticsearch-templates/commit/b3db410bc93144a94ac0acfa0312de4efc313973
            if 'docker' in generated_json["mappings"][_idx_type]["properties"]:
                del generated_json["mappings"][_idx_type]["properties"]["docker"]["properties"]["container_name"]

            # https://github.com/ViaQ/elasticsearch-templates/pull/106
            if 'systemd' in generated_json["mappings"][_idx_type]["properties"]:
                del generated_json["mappings"][_idx_type]["properties"]["systemd"]["properties"]["t"]["properties"]["LINE_BREAK"]
                del generated_json["mappings"][_idx_type]["properties"]["systemd"]["properties"]["t"]["properties"]["STREAM_ID"]
                del generated_json["mappings"][_idx_type]["properties"]["systemd"]["properties"]["t"]["properties"]["SYSTEMD_INVOCATION_ID"]

            self._remove_viaq_index_name_field(generated_json, es_version)

        elif es_version == supported._es5x:
            self._remove_viaq_index_name_field(generated_json, es_version)

        elif es_version == supported._es6x:
            self._remove_all_field(generated_json, es_version)
            self._remove_viaq_index_name_field(generated_json, es_version)
        # ======================

        generated_index_template = self._sort(generated_json)
        # print(generated_index_template)

        # ---- wget release data
        released_data = self._wget(json_url)

        # Mask version
        released_data["mappings"][_idx_type]["_meta"]["version"] = "na"

        # Fix downloaded data:
        # ======================
        if es_version == supported._es2x:
            # We need to clean some diffs that we know exists today but they are either
            # fine to ignore or there is an open ticket that has fix pending.

            # https://github.com/ViaQ/elasticsearch-templates/issues/87
            released_data["aliases"] = {".all": {}}
            # https://github.com/ViaQ/elasticsearch-templates/issues/69
            del released_data["mappings"][_idx_type]["dynamic_templates"][0]["message_field"]["mapping"]["omit_norms"]
            released_data["mappings"][_idx_type]["dynamic_templates"][0]["message_field"]["mapping"]["norms"] = {'enabled': False}
            #  - on top of #69 norms were enabled for general string fields
            del released_data["mappings"][_idx_type]["dynamic_templates"][1]["string_fields"]["mapping"]["omit_norms"]
            released_data["mappings"][_idx_type]["dynamic_templates"][1]["string_fields"]["mapping"]["norms"] = {'enabled': True}

            # https://github.com/ViaQ/elasticsearch-templates/issues/83
            new_order = [2, 3, 4, 0, 1]
            reordered_dynamic_templates = [released_data["mappings"][_idx_type]["dynamic_templates"][i] for i in new_order]
            released_data["mappings"][_idx_type]["dynamic_templates"] = reordered_dynamic_templates

            # https://github.com/ViaQ/elasticsearch-templates/issues/69#issuecomment-357276665
            del released_data["mappings"][_idx_type]["properties"]["ipaddr4"]["norms"]

            # https://github.com/ViaQ/elasticsearch-templates/issues/78
            released_data["mappings"][_idx_type]["properties"]["kubernetes"]["properties"]["container_name"]["index"] = "analyzed"
            released_data["mappings"][_idx_type]["properties"]["kubernetes"]["properties"]["container_name"]["doc_values"] = False

            # https://github.com/ViaQ/elasticsearch-templates/issues/79
            del released_data["mappings"][_idx_type]["properties"]["pipeline_metadata"]["properties"]["collector"]["properties"]["ipaddr4"]["norms"]
            released_data["mappings"][_idx_type]["properties"]["pipeline_metadata"]["properties"]["collector"]["properties"]["ipaddr4"]["type"] = "ip"

            # https://github.com/ViaQ/elasticsearch-templates/issues/82
            del released_data["mappings"][_idx_type]["properties"]["pipeline_metadata"]["properties"]["normalizer"]["properties"]["ipaddr4"]["norms"]

            # https://github.com/ViaQ/elasticsearch-templates/issues/80
            if 'aushape' in released_data["mappings"][_idx_type]["properties"]:
                released_data["mappings"][_idx_type]["properties"]["aushape"]["properties"]["error"]["index"] = "analyzed"
                released_data["mappings"][_idx_type]["properties"]["aushape"]["properties"]["error"]["doc_values"] = False

            self._remove_include_in_all(released_data, es_version)

        if es_version == supported._es5x:
            pass

        if es_version == supported._es6x:
            self._remove_all_field(released_data, es_version)
        # ======================

        released_index_template = self._sort(released_data)

        try:
            self.assertEqual(released_index_template, generated_index_template)
        except AssertionError as error:
            print("Test failed.", error)
            print("Output both index templates to stderr. "
                  "TIP: Use 2>file.log to redirect it to a file for detailed investigation.")
            print("\nReleased index template: ", file=sys.stderr)
            print(released_index_template, file=sys.stderr)
            print("\nGenerated index template: ", file=sys.stderr)
            print(generated_index_template, file=sys.stderr)
            raise
