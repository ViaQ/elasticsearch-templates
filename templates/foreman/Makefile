.PHONY: all clean docs

all: docs
	python3 ../../scripts/generate_template.py template.yml ../../namespaces/

clean:
	rm *.json *.asciidoc

docs:
	python3 ../../scripts/generate_template.py template.yml ../../namespaces/ --docs
