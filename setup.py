from setuptools import setup, find_packages

setup(
  name='capitains_nautilus',
  version="1.0.2",
  description='Resolver for Capitains Guidelines Repository',
  url='http://github.com/Capitains/nautilus',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='Mozilla Public License Version 2.0',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytain>=2.0.0",
    "tornado>=4.3",
    "Flask>=0.12",
    "Werkzeug>=0.11.3",
    "redis>=2.10.5",
    "Flask-Caching==1.2.0",
    "rdflib-sqlalchemy==0.3.8"
  ],
  test_requires=[
    "logassert",
    "mock",
    "nose"
  ],
  entry_points={
      'console_scripts': ['capitains-nautilus=capitains_nautilus.cmd:cmd'],
  },
  include_package_data=True,
  test_suite="nose.collector",
  zip_safe=False
)
