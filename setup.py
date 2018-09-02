from setuptools import setup, find_packages

setup(
  name='capitains_nautilus',
  version="1.0.3",
  description='Resolver for Capitains Guidelines Repository',
  url='http://github.com/Capitains/nautilus',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='Mozilla Public License Version 2.0',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytain>=2.0.0",
    "Flask>=0.12",
    "Werkzeug>=0.11.3",
    "Flask-Caching>=1.4.0,<2.0.0"
    "typing",
  ],
  test_requires=[
    "logassert",
    "mock",
    "nose",
    "typing",
    "urltools==0.3.2"
  ],
  extra_requires={
    "Berkeley": ["bsddb3==6.2.6"],
    "SQLAlchemy": ["rdflib-sqlalchemy>=0.3.8"]
  },
  entry_points={
      'console_scripts': ['capitains-nautilus=capitains_nautilus.cmd:cmd'],
  },
  include_package_data=True,
  test_suite="nose.collector",
  zip_safe=False
)
