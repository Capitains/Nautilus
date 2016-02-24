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
    "MyCapytain>=0.1.0",
    "tornado==4.3",
    "Flask==0.10.1",
    "Werkzeug==0.11.3",
    "Flask-Compress==1.3.0",
    "redis==2.10.5",
    "Flask-Cache==0.13.1"
  ],
  dependency_links=[
    "https://github.com/Capitains/MyCapytain/tarball/0.1.0dev#egg=MyCapytain-0.1.0"
  ],
  entry_points={
      'console_scripts': ['capitains-nautilus=nautilus.cmd:cmd'],
  },
  test_suite="tests"#,
  # zip_safe=True
)
