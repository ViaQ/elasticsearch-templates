TEMPLATE_NAME = com.redhat.viaq-openshift

.PHONY: all templates index_pattern

INDEX_PATTERN_DIRS = openshift,collectd_metrics

all: templates index_pattern

templates:
	for dir in {$(INDEX_PATTERN_DIRS)}; do \
		cd $$dir ; \
		make ; \
		cd .. ; \
	done

index_pattern:
	python ../scripts/concat-index-pattern-fields.py \
		{$(INDEX_PATTERN_DIRS)}/*.index-pattern.json \
		> com.redhat.viaq-openshift.index-pattern.json
