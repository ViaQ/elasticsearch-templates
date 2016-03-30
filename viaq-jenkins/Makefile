TEMPLATE_NAME = com.redhat.viaq-ci

all: $(TEMPLATE_NAME).template.json $(TEMPLATE_NAME).asciidoc
.PHONY: all clean

# Generates the final template ready for importing in ElasticSearch
$(TEMPLATE_NAME).template.json:
	python ../scripts/generate_template.py . $(TEMPLATE_NAME)

# Generates the ascii documentation of the fields
$(TEMPLATE_NAME).asciidoc:
	python ../scripts/generate_field_docs.py . $(TEMPLATE_NAME)

clean:
	rm $(TEMPLATE_NAME).template.json $(TEMPLATE_NAME).asciidoc

