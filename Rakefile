# Rakefile for serpapi-python
# This file provides a familiar interface for developers coming from the Ruby version.

require 'rake'

desc "Execute all the steps (default)"
task default: %i[check dependency version lint test coverage oobt]

desc "Run out of box testing using the local build"
task oobt: %i[check lint build coverage demo]

desc "Check if SERPAPI_KEY is set"
task :check do
  if ENV['SERPAPI_KEY']
    puts 'check: found $SERPAPI_KEY'
  else
    puts 'check: SERPAPI_KEY must be defined'
    exit 1
  end
end

desc "Install project dependencies"
task :dependency do
  sh 'uv sync --dev'
end

desc "Print current version"
task :version do
  sh 'uv run python -c "from serpapi.version import __version__; print(__version__)"'
end

desc "Lint code using black, isort, and mypy"
task :lint do
  puts "Running black..."
  sh 'uv run black --check .'
  puts "Running isort..."
  sh 'uv run isort --check .'
  puts "Running mypy..."
  sh 'uv run mypy serpapi/'
end

desc "Format code using black and isort"
task :format do
  sh 'uv run black .'
  sh 'uv run isort .'
end

desc "Run core tests using pytest"
task :test do
  sh 'uv run pytest tests/test_client.py'
end

desc "Run all tests including examples (regression)"
task :regression do
  sh 'uv run pytest tests/'
end

desc "Run tests with coverage"
task :coverage do
  sh 'uv run pytest --cov=serpapi tests/'
end

desc "Build the package (wheel and sdist)"
task :build do
  sh 'uv build'
end

desc "Install the package locally from the build"
task :install do
  sh 'uv pip install --force-reinstall dist/*.whl'
end

desc "Run demo examples"
task :demo do
  Dir.glob('examples/*.py').each do |file|
    puts "running demo: #{file}"
    sh "uv run python #{file}"
  end
end

desc "Run benchmark tests"
task :benchmark do
  sh 'uv run python examples/benchmark_serpapi.py'
end

desc "Create a git tag based on version.py"
task :tag do
  version = `uv run python -c "from serpapi.version import __version__; print(__version__)"`.strip
  puts "create git tag #{version}"
  sh "git tag #{version}"
  puts "now publish the tag:\n$ git push origin #{version}"
end

desc "Release the package (stub for uv publish)"
task release: [:oobt] do
  puts "Ready to release. Run: uv publish"
end

