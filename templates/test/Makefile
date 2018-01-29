.PHONY: all clean docs

all: docs
	python ../../scripts/generate_template.py template-test.yml ../../namespaces/

clean:
	rm *.template.json

docs:
	python ../../scripts/generate_template.py template-test.yml ../../namespaces/ --docs
