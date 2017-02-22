from setuptools import setup, find_packages

setup(
  name='capitains_nautilus',
  version="1.0.0b1",
  description='Resolver for Capitains Guidelines Repository',
  url='http://github.com/Capitains/nautilus',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytain>=2.0.0b13",
    "tornado>=4.3",
    "Flask>=0.12",
    "Werkzeug>=0.11.3",
    "redis>=2.10.5",
    "Flask-Caching>=1.2.0"
  ],
  test_requires=[
    "logassert"
  ],
  entry_points={
      'console_scripts': ['capitains-nautilus=capitains_nautilus.cmd:cmd'],
  },
  include_package_data=True,
  test_suite="tests",
  zip_safe=False
)
