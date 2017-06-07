TEMPLATE_NAME = com.redhat.viaq-openshift

.PHONY: all clean

all:
	python ../../scripts/generate_template.py template.yml ../../namespaces/

clean:
	rm *.template.json

docs:
	python ../../scripts/generate_template.py template.yml ../../namespaces/ --docs

