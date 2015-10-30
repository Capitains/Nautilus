from setuptools import setup, find_packages

import lilacs

setup(
  name='lilacs',
  version=lilacs.__version__,
  description='MyCapytains CTS 5 Endpoint implementation for a xml / directory based system',
  url='http://github.com/Capitains/lilacs',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytains>=0.0.6"
  ],
  test_suite="tests",
  zip_safe=False
)
