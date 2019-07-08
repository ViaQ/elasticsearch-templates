Unit tests are implemented using Python [unittest library](https://docs.python.org/3/library/unittest.html) and are
located in files named `*_test.py`.

To run unit test manually you navigate to `scripts` folder and execute:

```bash
# Run all unit tests in specified python file
$ python -m unittest -v generate_template_test

# Run all test from specified class in the python file
$ python -m unittest -v generate_template_test.GenerateTemplateTestCase

# Run just individual unit test from the class in the python file
$ python -m unittest -v generate_template_test.GenerateTemplateTestCase.test_index_template
```

Unit tests are also run as part of Travis integration. See [`.travis.yml`](../.travis.yml) for details.