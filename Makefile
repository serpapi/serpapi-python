# Automate pip package development
#
# current version
version=$(shell grep version setup.py | cut -d"'" -f2)

.PHONY: build

all: clean install test test2

clean:
	find . -name '*.pyc' -delete
	find . -type d -name "__pycache__" -delete
	pip3 uninstall google_search_results

install:
	pip3 install -r requirements.txt

lint:
	pylint serpapi

# Test with Python 3
test: lint
	pytest --cov=serpapi tests/

# run example only 
#  and display output (-s)
example:
	pytest -s "tests/test_example.py::TestExample::test_async"

install:
	pip3 install -U setuptools
	pip install pytest-cov

doc:
	pydoc

# https://packaging.python.org/tutorials/packaging-projects/
build: doc
	python3 setup.py sdist

oobt: build
	pip3 install ./dist/google_search_results-$(version).tar.gz
	python3 oobt/oobt.py

check: oobt
	twine check dist/google_search_results-$(version).tar.gz

release: # check
	twine upload dist/google_search_results-$(version).tar.gz
