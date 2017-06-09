.PHONY: all clean

all:
	python ../../scripts/generate_template.py template-project.yml ../../namespaces/
	python ../../scripts/generate_template.py template-operations.yml ../../namespaces/

clean:
	rm *.template.json

docs:
	python ../../scripts/generate_template.py template.yml ../../namespaces/ --docs

