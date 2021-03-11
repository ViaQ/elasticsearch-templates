.PHONY: all clean docs

all: docs
	python3 ../../scripts/generate_template.py template-project.yml ../../namespaces/
	python3 ../../scripts/generate_template.py template-operations.yml ../../namespaces/

clean:
	rm *.json *.adoc

docs:
	python3 ../../scripts/generate_template.py template-project.yml ../../namespaces/ --docs
	python3 ../../scripts/generate_template.py template-operations.yml ../../namespaces/ --docs
