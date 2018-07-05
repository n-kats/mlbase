from setuptools import setup, find_packages

setup(
  name='mlbase',
  version='0.0.0',
  description="""
  schedule
  """,
  url='http://github.com/n-kats',
  author='n-kats',
  author_email='',
  license='MIT',
  classifiers=[
    'Development Status :: 3 -Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6'
  ],
  packages=find_packages(exclude=['tests', 'sandbox']),
  install_requires=[],
  extras_require={
    'dev': [],
    'test': []
  },
  package_data={
    'sample': []
  },
  data_files=[],
  entry_points={
    'console_scripts': [
       'mlbase=mlbase.cli.main:run'
    ]
  }
)
