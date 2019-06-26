.PHONY: all clean docs

all: docs
	python ../../scripts/generate_template.py template-test.yml ../../namespaces/

clean:
	rm *.json *.asciidoc

docs:
	python ../../scripts/generate_template.py template-test.yml ../../namespaces/ --docs
