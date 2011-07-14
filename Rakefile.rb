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

task :build do  
  sh "python setup.py egg_info -b '_#{build_number}' bdist_egg"
end

task :test do
  sh "nosetests"
end

def build_number
  ENV['BUILD_NUMBER'] || 'dev'
end
