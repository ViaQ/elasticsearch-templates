.PHONY: all clean docs

all: docs
	python ../../scripts/generate_template.py template-project.yml ../../namespaces/
	python ../../scripts/generate_template.py template-operations.yml ../../namespaces/

clean:
	rm *.json *.asciidoc

docs:
	python ../../scripts/generate_template.py template-project.yml ../../namespaces/ --docs
	python ../../scripts/generate_template.py template-operations.yml ../../namespaces/ --docs
