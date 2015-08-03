import codecs
import os
import re
import setuptools


def local_file(file):
  return codecs.open(
    os.path.join(os.path.dirname(__file__), file), 'r', 'utf-8'
  )

install_reqs = [
  line.strip()
  for line in local_file('requirements.txt').readlines()
  if line.strip() != ''
]

setuptools.setup(
  name = "wikitable",
  description = "Wikipedia Wrapper for mining semantic data in Python",
  license = "MIT",
  keywords = "python wikipedia semantic-web",
  url = "https://github.com/AlexImmer/wiki-list_of-retrieval",
  install_requires = install_reqs,
  packages = ['wikitable'],
  long_description = local_file('README.md').read(),
  classifiers = [
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ]
)