# Automate pip package development
#
# current version
version=$(shell grep version setup.py | cut -d"'" -f2)
dist=dist/serpapi-$(version).tar.gz

.PHONY: build

all: clean install readme doc lint test build

clean:
	find . -name '*.pyc' -delete
	find . -type d -name "__pycache__" -delete
	pip3 uninstall serpapi

# lint check
lint:
	pylint serpapi

# test with Python 3
test:
	pytest --cov=serpapi --cov-report html tests/*.py

# pytest-cov - code coverage extension for pytest
# sphinx - documentation
install:
	pip3 install -U setuptools
	pip3 install -r requirements.txt
	pip3 install pytest-cov
	pip3 install sphinx

readme:
	erb -T '-' README.md.erb > README.md

doc: readme
	$(MAKE) -C docs/ html

# https://packaging.python.org/tutorials/packaging-projects/
build: doc test
	python3 setup.py sdist

# out of box testing / user acceptance before delivery
oobt: build
	pip3 install ./${dist}
	python3 oobt/oobt.py

check: oobt
	twine check ${dist}

release: # check
	twine upload ${dist}

# run example only 
#  and display output (-s)
example:
	pytest -s "tests/test_example.py::TestExample::test_async"
