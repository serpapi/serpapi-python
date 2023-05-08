# Automate pip package development
#
# Usage
# To release a package.
# - update version in serpapi/_version.py
# - review README version
# - run 
# $ make release

# current version
version=$(shell grep version setup.py | cut -d"'" -f2)
dist=dist/serpapi-$(version).tar.gz

.PHONY: build

all: clean install readme doc lint test build oobt check

clean:
	find . -name '*.pyc' -delete
	find . -type d -name "__pycache__" -delete
	python3 -m pip uninstall serpapi

# lint check
lint:
	python3 -m pylint serpapi

# test with Python 3
test:
	python3 -mpytest --cov=serpapi --cov-report html tests/*.py

# install dependencies
# 
# pytest-cov - code coverage extension for pytest
# sphinx - documentation
# twine - release automation
install:
	python3 -m pip install -U setuptools
	python3 -m pip install -r requirements.txt
	python3 -m pip install pylint
	python3 -m pip install pytest-cov
	python3 -m pip install twine
	python3 -m pip install sphinx

readme:
	erb -T '-' README.md.erb > README.md

doc: readme
	$(MAKE) -C docs/ html

# https://packaging.python.org/tutorials/packaging-projects/
build: 
	python3 setup.py sdist

# out of box testing / user acceptance before delivery
oobt: build
	python3 -m pip install ./${dist}
	python3 oobt/demo.py


check: oobt
	python3 -m twine check ${dist}

release: # check
	python3 -m twine upload ${dist}

# run example only 
#  and display output (-s)
example:
	python3 -m pytest -s "tests/test_example.py::TestExample::test_async"
