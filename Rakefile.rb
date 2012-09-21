
ENV['PYTHONPATH'] = './src:' + (ENV['PYTHONPATH'] or '')

# Assign some test keys if they aren't already set.
ENV["DATADOG_API_KEY"] ||= '9775a026f1ca7d1c6c5af9d94d9595a4'
ENV["DATADOG_APP_KEY"] ||= '87ce4a24b5553d2e482ea8a8500e71b8ad4554ff'


task :default => [:clean, :test, :build]
task :clean => [:clean_pyc, :clean_build, :clean_dist]

task :clean_pyc do
  sh "find . -name '*.pyc' -exec rm {} \\;"
end

task :clean_build do
  sh "rm -rf build/*"
end

task :clean_dist do
  sh "rm -f dist/*.egg"
end

task :doc do
  sh "python setup.py build_sphinx"
end

task :build do
  sh "python setup.py egg_info -b '_#{build_number}' bdist_egg"
end

namespace :test do

  desc "Run integration tests."
  task :integration do
    sh 'nosetests --exclude ".*greenlet.*" tests/integration'
    # Testing greenlet flush requires another process, so run them seperately.
    sh "PYTHONPATH=src:$PYTHONPATH python tests/integration/test_stats_api_greenlet.py"
  end

  desc "Run unit tests."
  task :unit do
    sh 'nosetests tests/unit'
  end

  desc "Run perf tests."
  task :perf do
    sh 'python tests/performance/*.py'
  end

end

desc "Run all tests."
task :test => ['test:unit', 'test:integration']


def build_number
  ENV['BUILD_NUMBER'] || 'dev'
end
