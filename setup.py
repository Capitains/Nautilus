from setuptools import setup, find_packages

# import lilacs

setup(
  name='lilacs',
  version="0.0.1",
  description='MyCapytains CTS 5 Endpoint implementation for a xml / directory based system',
  url='http://github.com/Capitains/lilacs',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytain>=0.0.9"
  ],
  test_suite="tests"#,
  # zip_safe=True
)
