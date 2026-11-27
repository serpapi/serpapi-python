# Contributing

Bug reports and pull requests are welcome on GitHub. Run commands from the repository root.

## Development setup

The SDK CI tests Python 3.8 through 3.15. Create a virtual environment and install the package with its test and documentation dependencies:

```sh
uv venv --python 3.13
uv pip install -e '.[test,docs]'
```

The editable install uses the Python files in your checkout, so source changes take effect without reinstalling the package.

Activate the environment on macOS or Linux:

```sh
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

The commands below use `python` from that environment.

## Testing

### Checks that need no API key

These tests cover response parsing, image uploads and extraction with simulated responses, timeouts, exceptions, the async client, documentation syntax, and the example runner:

```sh
python -m pytest tests/test_output_formats.py tests/test_image_upload.py tests/test_extract.py tests/test_timeout.py tests/test_exceptions.py tests/test_async_client.py tests/test_docs_examples.py tests/test_docs_example_runner.py -k 'not live' -q
```

The file list limits this command to tests that make no external requests. Applying `-k 'not live'` to the entire suite is not enough to run offline: some SDK integration tests do not have `live` in their names.

The async client tests need Python 3.11 or newer, where the `test` extra installs httpx2. On older versions, pytest skips them.

### SDK integration tests

Set `API_KEY` in your shell or editor's run configuration before running integration tests. Documentation examples also accept `SERPAPI_KEY`, but the shared SDK fixtures require `API_KEY`. If you already have `SERPAPI_KEY` set, copy it to `API_KEY` in the same shell:

```sh
export API_KEY="$SERPAPI_KEY"
```

In PowerShell, use `$env:API_KEY = $env:SERPAPI_KEY`. Keep real keys out of source files and commits.

To match the test selection in the SDK CI workflow:

```sh
python -m pytest tests --ignore-glob='tests/test_docs_*.py' -k 'not example' -q
```

This includes live account, location, search, and pagination checks. To run every discovered test, including the standalone engine examples and documentation examples:

```sh
python -m pytest -q
```

Both commands make real SerpApi requests. The full suite can use more searches than a test run limited to the files you changed. PR CI also runs the standalone engine examples on Python 3.15. Documentation tests run in the package and documentation release workflows on release tags, and in manual documentation runs on `master`.

### Testing documentation examples

The tests discover Python code blocks in the README and all Markdown pages under `docs/`. They run each page as a separate script against SerpApi, including the multiprocessing example's worker processes. The Lens upload examples use the repository's PNG icon as `image.png`. Each page has a five-minute limit, and HTTP errors or JSON responses containing an `error` fail the check even if the example catches the exception.

With `SERPAPI_KEY` or `API_KEY` set in your environment, run the following command with Python 3.11 or newer, because the README and the async client guide use `serpapi.AsyncClient`:

```sh
python -m pytest tests/test_docs_examples.py --require-docs-key -q
```

The `--require-docs-key` option fails if neither key is set. Without that option, local runs skip live tests when no key is available. To check syntax and the test runner without making API calls:

```sh
python -m pytest tests/test_docs_examples.py tests/test_docs_example_runner.py -k 'not live' -q
```

Code blocks marked with `docs-test: skip` are checked for syntax but not executed. These cover the old `google-search-results` package and examples that require private proxy or certificate settings, or disable TLS verification. Each marker includes its reason.

### Testing documentation publishing

Run the publishing tests locally with:

```sh
python -m pytest tests/test_docs_publishing.py -q
```

These tests use simulated RTD responses to check outgoing HTTP requests, CI event and commit checks, version selection, polling, and cleanup after failures. They need no API keys and do not publish documentation. In CI, they run only in the Documentation workflow on Python 3.13, before the documentation build and publication. The SDK and PyPI release workflows exclude this file. RTD checks the actual checkout with `scripts.check_docs_revision` before and after building, without rerunning the publishing tests.

### Running a single test or example

Run one test file while working on that part of the package:

```sh
python -m pytest tests/test_output_formats.py -q
```

To list documentation test IDs without running their examples:

```sh
python -m pytest tests/test_docs_examples.py --collect-only -q
```

For example, run only the Google Lens upload and search page with:

```sh
python -m pytest 'tests/test_docs_examples.py::test_documentation_examples_live[docs/examples/google-lens-image-upload.md]' --require-docs-key -q
```

Use `-x -vv` in place of `-q` to stop at the first failure and show more detail. A syntax failure points to a page and block number. A live failure can come from the example code, an invalid key, exhausted quota, or an upstream API error; inspect the reported engine and error before changing the example.

When adding a documentation example, use a fenced block labelled `python`. Blocks on the same page execute in order and share variables. Avoid hard-coded dates that expire. Use a `docs-test: skip` marker with a reason only when a block cannot run in the test environment, such as one requiring a user's proxy or certificate.

## Building the documentation locally

The documentation uses Sphinx with MyST for Markdown pages and the Read the Docs theme. The development setup above includes its dependencies. Build and serve the HTML site with:

```sh
python -m sphinx -M html docs docs/_build -W --keep-going
python -m http.server 8000 --bind 127.0.0.1 --directory docs/_build/html
```

Open [the local documentation](http://127.0.0.1:8000). After editing a page, rerun the Sphinx build command and refresh your browser. Check the affected page, its code blocks, and the sidebar links. Press Ctrl+C to stop the server.

Sphinx discovers public APIs with autodoc and reads their docstrings without running the search examples. Sidebar order comes from the toctrees in `docs/index.md`, so documentation filenames do not need numeric prefixes. The `-W` option makes warnings fail the build.

CI also builds EPUB. Check it locally with:

```sh
python -m sphinx -M epub docs docs/_build -W --keep-going
```

## Building the package

Build the source distribution and wheel with:

```sh
uv build
```

The files are written to `dist/`. Documentation sources, this guide, and the logo assets are included in the source distribution (`.tar.gz`) so contributors can build the docs from a source release. The wheel contains only the `serpapi` library and its package metadata. Generated docs and documentation dependencies are not part of a normal installation.

## Documentation publishing

The [documentation workflow](.github/workflows/docs.yml) runs the live examples before building HTML and EPUB when a `v*` release tag is pushed, or when `master` or a release tag is selected for a manual run. It does not run on branch pushes or pull requests.

After the live examples and documentation build pass, the same workflow publishes to Read the Docs for the selected ref. A manual run on `master` updates `latest` without triggering the package release workflow or changing the package version. The publishing job uses the `docs` GitHub environment and its `RTD_API_TOKEN` secret. The SerpApi key stays in GitHub as the existing `API_KEY` repository or organization secret.

The workflow syncs RTD versions, activates the requested version if needed, and waits for the build to finish. `latest` tracks `master`. A release tag has its own version and also rebuilds both `stable` and `latest` when RTD identifies it as the highest stable release. Both builds must use the release commit tested by CI. If `master` has advanced beyond that commit, the `latest` build fails the revision check; run the Documentation workflow on `master` to test and publish its current docs. Older releases and prereleases do not update either alias. RTD still builds the site from the repository using [.readthedocs.yaml](.readthedocs.yaml); it does not receive the HTML artifact from GitHub. Documentation publishing runs independently of the PyPI release workflow.

Before requesting a build, the workflow creates a temporary RTD environment variable named `DOCS_CI_REVISION`. It contains the tested commit, the permitted versions, and an expiration time. RTD checks this record against its checkout before and after the Sphinx build. A missing, expired, or different revision stops publication. RTD needs no SerpApi key. The workflow removes the temporary record after publishing, including when a build fails. Publishing jobs run one at a time so they cannot overwrite each other's revision record.

### Maintainer setup

Maintainers can configure the existing RTD project and GitHub environment with these steps:

1. In RTD **Settings**, set **Connected repository** to **No connected repository** and keep **Repository URL** set to `https://github.com/serpapi/serpapi-python.git`. Set **Default branch** to `master` and the configuration file path to `.readthedocs.yaml`. The public repository URL lets RTD clone the source without receiving GitHub push events through the GitHub App.
2. Under RTD **Integrations**, remove incoming GitHub webhook integrations for this project. If an older RTD webhook is also listed in the GitHub repository's **Settings > Webhooks**, disable or remove that webhook. Do not remove integrations for other projects.
3. Under RTD **Automation Rules**, remove rules that activate new versions or change the default version. The workflow handles release activation. Under **Settings > Pull request builds**, turn off **Build pull requests for this project**. GitHub Actions runs the existing SDK and engine example tests on PRs.
4. Under RTD **Environment Variables**, remove `API_KEY` or `SERPAPI_KEY` if you added either for docs tests. Do not add the RTD API token here. The workflow manages `DOCS_CI_REVISION` automatically.
5. Keep `latest` active in **Versions** and use it as the default documentation version during this migration. Existing release tags contain their original docs and build configuration. After the first release containing these changes builds successfully, you can choose `stable` as the default version.
6. Create an RTD API token in your [RTD profile settings](https://app.readthedocs.org/accounts/tokens/), using an account that maintains the `serpapi-python` project. In GitHub, open the repository's **Settings > Environments**, create an environment named `docs`, and add an environment secret named `RTD_API_TOKEN` with that value. Under **Deployment branches and tags**, select **Selected branches and tags** and add a Branch rule for `master` and a Tag rule for `v*`. Leave required reviewers and wait timers disabled if publishing should run without a manual approval.
7. Merge the changes to `master`, then push the version tag for the release. In GitHub **Actions > Documentation**, follow **Live documentation examples**, **Build Sphinx documentation**, and **Publish Read the Docs**. The publishing log links to the RTD build. To retry publishing, run the Documentation workflow on the intended release tag, or select `master` to publish updated `latest` docs without a new package release. A manual run on any other branch skips the documentation jobs.

Use GitHub Actions to request builds after this setup. A manual RTD build has no CI revision record and will fail the revision check. If a branch or tag moves between testing and the RTD checkout, rerun the workflow for its current commit. Pushing a `v*` tag also starts the PyPI release workflow, so use an actual package release to test release documentation.

See the [RTD build API](https://docs.readthedocs.com/platform/stable/api/v3.html#build-triggering), [Git integration settings](https://docs.readthedocs.com/platform/stable/reference/git-integration.html), and [GitHub environment settings](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) for the platform setup details.

## Type stubs

The `stubs/` directory builds `serpapi-stubs`, a separate PyPI distribution that users install with `pip install "serpapi[typing]"`. The SDK wheel and source distribution do not include it. See [stubs/README.md](stubs/README.md) for the layout and the commands that refresh and regenerate the stubs.

The [stubs workflow](.github/workflows/stubs.yml) runs on pull requests that change `serpapi/` or `stubs/`. To check the stubs against your local SDK checkout, use Python 3.13, install the stubs into your development environment, and type-check the samples:

```sh
cd stubs
python tools/generate_stubs.py --check
python -m pytest
python tools/release_version.py --offline
uv build --clear
uv pip install "../[async]" "mypy==2.4.1" "pyright==1.1.414" --reinstall-package serpapi-stubs dist/*.whl
python -m mypy.stubtest serpapi --allowlist tests/stubtest_allowlist.txt
mypy
pyright
```

The checker versions are the ones the workflow pins; change both together.

`release_version.py` writes the ignored `VERSION` file that the build reads. Stub versions are computed in CI, so never set them by hand. Stubtest fails when a public SDK function or class changes without a matching stub change, so update the handwritten stubs in `stubs/serpapi-stubs/` together with the SDK.

The SDK's `typing` extra requests stubs from its major version (`serpapi-stubs>=1,<2`). The dependency in `stubs/pyproject.toml` declares the oldest SDK the stubs describe (`serpapi>=1.3.0,<2`). Write the minimum as the full `X.Y.Z` tag version and keep it unchanged for engine-only refreshes. When a new runtime API requires a higher minimum, set the floor to the upcoming SDK version and update `serpapi/__version__.py` in the same change if it still names the previous release. In addition to the checkout check above, CI runs stubtest against the minimum SDK's tag once it exists.

### Stub releases

Both stub release workflows use PyPI trusted publishing from the `pypi-stubs` environment. Which workflow runs depends on what changed:

- **With an SDK release.** The release workflow publishes `serpapi-stubs` `<version>.<YYYYMMDD>` before it publishes the SDK, so `serpapi[typing]` resolves as soon as the SDK is available.
- **Between SDK releases.** When a push to `master` changes the shipped stub files, the [stub release workflow](.github/workflows/stubs-release.yml) publishes a new version for the current SDK release. The SDK version must have a non-yanked distribution on PyPI, and `serpapi/` must match its release tag. Changes for an unreleased SDK ship with its tag workflow instead.

The [refresh workflow](.github/workflows/stubs-refresh.yml) runs every Monday. It fetches the engine metadata, regenerates the stubs, and opens or updates a pull request from `bot/refresh-serpapi-stubs` when anything changed. If a later run finds that the stubs match `master` again, it closes that pull request only if the branch still points to the commit it inspected. A manual run also refreshes from `master`, whichever branch it is started on. Review the diff before merging: merging usually publishes a stub release. If you push your own commits to the refresh branch, later runs leave the branch and its pull request unchanged until it is merged or closed.

GitHub can refuse a push that carries workflow-file changes from `master` into an existing branch. The workflow avoids most of these pushes: it recreates a leftover refresh branch, and it updates an open refresh pull request only when the generated stubs changed. If a run still fails to push for that reason, merge or close the pull request and run the workflow again.

Before yanking a broken stub release, check that each affected supported SDK can resolve to a working wheel. If any cannot, publish a compatible replacement first. The SDK prefix sorts before the date: a hotfix built on an older SDK does not outrank a later compatible series.

The SDK-tag workflow does not supersede a series with any non-yanked files. Do not move a release tag to different SDK code after its stubs have been published; use a new SDK version. If the series has only yanked releases or no files left, the tag workflow publishes a replacement before the SDK. Yanked and file-less versions still reserve their version numbers. For an upload collision between simultaneous stub releases, choose **Re-run all jobs** on the latest compatible run of the stub-only release workflow. It chooses a suffix above the highest one listed for that SDK and date, whereas **Re-run failed jobs** reuses the colliding version.

The stub-only workflow queues up to 100 pending runs across release branches, rather than letting a hotfix or manual dispatch replace an already pending release. Before uploading, it checks every commit in the branch's first-parent history: a newer commit with different shipped stubs for the same SDK supersedes an older run only when that commit has a run of this workflow on the same branch. The head of a multi-commit push can carry an earlier stub fix even if its own change is documentation-only. An intermediate commit with no release run does not suppress the pending release, nor does a change targeting an unreleased SDK. Run-lookup errors fail the publishing job rather than assuming a replacement exists. A run whose commit was removed from the branch is also skipped. After a cancellation or a full queue, rerun all jobs on the newest compatible run, not an older superseded one.

Release tags publish only the files in the tagged commit. If a stub change landed after that commit and was skipped while waiting for the SDK release, manually run **Release serpapi-stubs** on `master` once the SDK is on PyPI, provided `serpapi/` still matches the tag. If SDK development has moved on, use the hotfix procedure below instead.

The stub version scheme currently supports final numeric SDK versions only, such as `1.2.3`. Prerelease, post-release, and development SDK versions cannot be used as the prefix for the `serpapi-stubs` date suffix. Do not set `serpapi/__version__.py` to one: the stub checks then fail on every pull request, and the release workflow stops before it publishes the SDK.

If a stub fix is needed after `serpapi/` has changed for an unreleased SDK version, the automatic workflow correctly skips it. To hotfix the released SDK, create a compatibility branch from its tag, bring over only the corrected `stubs/` content and the current `stubs.yml`, `stubs-build.yml`, `stubs-release.yml`, and `stubs-refresh.yml` workflows, and keep `serpapi/` unchanged from the tag. The refresh workflow is needed by the stub tests even when you do not run it. Push it as `stubs/hotfix-<sdk-version>` and manually run **Release serpapi-stubs** on that branch; the workflow only runs from `master` or from the hotfix branch named after the SDK version it contains. Add `stubs/hotfix-*` as an allowed branch for the `pypi-stubs` environment before dispatching.

## Publishing a new release

1. Update the version in `serpapi/__version__.py`. For a major release, update both dependency ranges in `pyproject.toml` and `stubs/pyproject.toml`. Minor and patch releases keep the SDK's `typing` extra unchanged; raise the stubs' minimum SDK only when needed.
2. Push a tag for that version. The release pipeline runs automatically:
   ```sh
   git tag v1.2.3
   git push origin v1.2.3
   ```
   This triggers the [release workflow](.github/workflows/release.yml), which tests and builds the SDK and stubs, publishes `serpapi-stubs` and then `serpapi` to PyPI, and smoke-tests the published package. If the stub checks or upload fail, the SDK is not published. The workflow also fails before publishing anything if the tag is not `v` followed by the version in `serpapi/__version__.py`.

> **Required secret:** `API_KEY` (used by the live documentation examples and the published-package smoke test).
