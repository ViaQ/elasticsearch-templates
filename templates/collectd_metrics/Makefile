.PHONY: all clean docs

all: docs
	python ../../scripts/generate_template.py template.yml ../../namespaces/

clean:
	rm *.template.json

docs:
	python ../../scripts/generate_template.py template.yml ../../namespaces/ --docs
