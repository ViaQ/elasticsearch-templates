TEMPLATE_NAME = com.redhat.viaq-ci

all: $(TEMPLATE_NAME).template.json $(TEMPLATE_NAME).asciidoc
.PHONY: all clean

$(TEMPLATE_NAME).template.json:
	python ../scripts/generate_template.py . $(TEMPLATE_NAME)

$(TEMPLATE_NAME).asciidoc:
	python ../scripts/generate_field_docs.py . $(TEMPLATE_NAME)

clean:
	rm $(TEMPLATE_NAME).template.json $(TEMPLATE_NAME).asciidoc

