TEMPLATE_NAME = com.redhat.viaq-openshift

.PHONY: all templates index_pattern

INDEX_PATTERN_DIRS = openshift


all: templates index_pattern

# Clean all index templates and index patterns generated during 'make'
clean:
	for dir in {$(INDEX_PATTERN_DIRS)}; do \
		cd $$dir ; \
		make clean; \
		cd .. ; \
	done
	rm *.index-pattern.json

templates:
	for dir in {$(INDEX_PATTERN_DIRS)}; do \
		cd $$dir ; \
		make all; \
		cd .. ; \
	done

index_pattern:
	python3 ../scripts/concat_index_pattern_fields.py \
		"$(INDEX_PATTERN_DIRS)" "*.index-pattern.json" \
		"$(TEMPLATE_NAME).<ES_VERSION>.index-pattern.json"
