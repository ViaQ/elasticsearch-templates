TEMPLATE_NAME = com.redhat.viaq-openshift

.PHONY: all templates index_pattern

INDEX_PATTERN_DIR = openshift

all: templates index_pattern

# Clean all index templates and index patterns generated during 'make'
clean:
	cd $(INDEX_PATTERN_DIR) ; \
	make clean; \
	cd .. ; \
	rm *.index-pattern.json

templates:
	cd $(INDEX_PATTERN_DIR) ; \
	make all; \
	cd .. ; \

index_pattern:
	python3 ../scripts/concat_index_pattern_fields.py \
		"$(INDEX_PATTERN_DIR)" "*.index-pattern.json" \
		"$(TEMPLATE_NAME).<ES_VERSION>.index-pattern.json"
