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
  name = "wikitables",
  description = "Extractor for structured knowledge from Wikipedia's tables written in python",
  license = "MIT",
  keywords = "python wikipedia semantic-web dbpedia",
  url = "https://github.com/AlexImmer/wiki-list_of-retrieval",
  install_requires = install_reqs,
  packages = ['wikitables'],
  long_description = local_file('README.md').read(),
  classifiers = [
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ]
)
