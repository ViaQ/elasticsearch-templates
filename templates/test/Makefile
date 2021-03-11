.PHONY: all clean docs

all: docs
	python3 ../../scripts/generate_template.py template-test.yml ../../namespaces/

clean:
	rm *.json *.adoc

docs:
	python3 ../../scripts/generate_template.py template-test.yml ../../namespaces/ --docs
