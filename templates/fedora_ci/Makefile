TEMPLATE_NAME = com.redhat.fedora-ci

.PHONY: all clean

all:
	python3 ../../scripts/generate_template.py template.yml ../../namespaces/

clean:
	rm *.json *.adoc
