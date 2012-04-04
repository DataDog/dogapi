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
    sh "PYTHONPATH=src:$PYTHONPATH python tests/integration/test_stats_api_greenlet.py"
  end

  desc "Run unit tests."
  task :unit do
    # Testing greenlet flush requires another process, so run them seperately.
    sh 'nosetests tests/unit'
  end

end

desc "Run all tests."
task :test => ['test:unit', 'test:integration']


def build_number
  ENV['BUILD_NUMBER'] || 'dev'
end
