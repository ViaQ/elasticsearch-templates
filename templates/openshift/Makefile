TEMPLATE_NAME = com.redhat.viaq-openshift

.PHONY: all clean

all:
	python ../../scripts/generate_template.py template-operations.yml ../../object_types/
	python ../../scripts/generate_template.py template-project.yml ../../object_types/

clean:
	rm *.template.json
