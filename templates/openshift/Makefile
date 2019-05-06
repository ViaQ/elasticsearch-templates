.PHONY: all clean docs

all: docs
	python ../../scripts/generate_template.py template-project.yml ../../namespaces/
	python ../../scripts/generate_template.py template-operations.yml ../../namespaces/

clean:
	rm *.template.json
	rm *.index-pattern.json
	rm *.asciidoc

docs:
	python ../../scripts/generate_template.py template-project.yml ../../namespaces/ --docs
	python ../../scripts/generate_template.py template-operations.yml ../../namespaces/ --docs
