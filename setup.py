from setuptools import setup, find_packages

setup(
  name='nautilus',
  version="0.0.1",
  description='Resolver for Capitains Guidelines Repository',
  url='http://github.com/Capitains/nautilus',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytain>=0.1.0"
  ],
  dependency_links=[
    "https://github.com/Capitains/MyCapytain/tarball/0.1.0dev#egg=MyCapytain-0.1.0"
  ],
  test_suite="tests"#,
  # zip_safe=True
)
