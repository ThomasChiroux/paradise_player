"""setuptools installer for paradise player."""

import os
import uuid

from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py

# local imports
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='UTF-8').read()
NEWS = open(os.path.join(here, 'NEWS.md'), encoding='UTF-8').read()

version = "0.1"

dev_reqs = []
reqs = ["requests"]


setup(name='paradise_player',
      version=version,
      description="CLI Player and notifier for radio paradise",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Operating System :: POSIX :: Linux", ],
      keywords='test',
      author='Thomas Chiroux',
      author_email='',
      license='LICENSE',
      packages=find_packages(exclude=['ez_setup']),
      package_data={'': ['*.md', '*.rst', '*.yaml', '*.cfg'], },
      include_package_data=True,
      zip_safe=False,
      tests_require=dev_reqs,
      install_requires=reqs,
      entry_points={
          'console_scripts':
          ['paradise_player=paradise.rpplayer:main',
           'rpp=paradise.rpplayer:main', ]})
