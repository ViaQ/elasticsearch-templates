TEMPLATE_NAME = com.redhat.viaq-openstack

.PHONY: all clean

all:
	python ../../scripts/generate_template.py \
		template.yml ../../namespaces/

clean:
	rm $(TEMPLATE_NAME).template.json
