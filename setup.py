from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    REQUIRED = f.read().splitlines()

setup(
  name='capitains_nautilus',
  version="2.0.0",
  description='Resolver for Capitains Guidelines Repository',
  url='http://github.com/Capitains/nautilus',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='Mozilla Public License Version 2.0',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=REQUIRED,
  tests_require=[
    "logassert",
    "mock",
    "nose",
    "typing",
    "urltools>=0.3.2"
  ],
  entry_points={
      'console_scripts': ['capitains-nautilus=capitains_nautilus.cmd:cmd'],
  },
  include_package_data=True,
  test_suite="nose.collector",
  zip_safe=False
)
