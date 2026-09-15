Release History
===============

1.1.2 (2026-09-15)
------------------

- Fixed a bug in SerpResults.yield_pages to ensure it does not request more pages than specified by max_pages. The bug
  caused two network requests to be sent when max_pages was set to 1.
- Enhancements to test parameters and examples

1.1.1 (2026-09-08)
------------------

- Enhancements for SerpApi markdown output (`output=md`) support
- Enhancements for readthedocs documentation: Added user guide, examples, automated publishing to RTD on release.

1.1.0 (2026-08-14)
------------------

- Add PyPI trusted publishing. PYPI Key is no longer required for publishing the package.
- Add image upload support (`/image` API) for Google Lens
- Release workflow: Add an option to manually trigger the release workflow and skip live tests
- Add more test cases: Locations API, pagination, etc.

1.0.1 (2026-03-18)
------------------

- Fix release workflow: YAML syntax error in smoke test step and remove broken GitHub Packages publish.

1.0.0 (2026-03-18)
------------------

- Automated PyPI release pipeline via GitHub Actions (tag-triggered: test → build → publish → smoke test).
- Modernized packaging to PEP 621 (pyproject.toml), removing legacy setup.py and Pipfile.
- Added Python 3.13 support.

0.1.6 (2026-02-16)
------------------

- Add support for request timeouts.
- Add status and error codes support - https://serpapi.com/api-status-and-error-codes

0.1.5 (2023-11-01)
------------------

- Python 3.12 support.

0.1.4 (2023-10-11)
------------------

- Add README documentation for various engines.

0.1.3 (2023-10-06)
------------------

- Replace deprecated serpapi_pagination.next_link with 'next'.
- Improve documentation: how to use the client directly for pagination searches.

0.1.2 (2023-10-03)
------------------

- Update project status to Production/Stable.

0.1.1 (2023-10-03)
------------------

- Update documentation link to point to Read the Docs.

0.1.0 (2023-10-03)
------------------

- First release on PyPI.
