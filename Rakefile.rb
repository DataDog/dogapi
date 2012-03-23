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

task :test do
  # Testing greenlet flush requires another process, so run them seperately.
  #sh 'nosetests --exclude ".*greenlet.*"'
  sh "PYTHONPATH=src:$PYTHONPATH python src/dogapi/stats/test_stats_api_greenlet.py"
end

def build_number
  ENV['BUILD_NUMBER'] || 'dev'
end
