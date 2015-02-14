import os
import re
import sys
from setuptools import setup, find_packages

PYPINAME = 'pyramid-aiorest'
PKGNAME = PYPINAME.replace('-', '_')

py_version = sys.version_info[:2]
if py_version < (3, 3):
    raise Exception("{name} requires Python >= 3.3.".format(name=PYPINAME))

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, PKGNAME, '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)


requires = ['colander',
            'pyramid-asyncio',
            'pyramid-yards',
            ]

if py_version < (3, 4):
    requires.append('asyncio')


setup(name=PYPINAME,
      version=VERSION,
      description='Pyramid Rest Framework For Asyncio',
      # long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Intended Audience :: Developers",
        "License :: Repoze Public License",
        ],
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      url='https://github.com/mardiros/{name}'.format(name=PKGNAME),
      keywords='pyramid asyncio',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='{name}.tests'.format(name=PKGNAME),
      install_requires=requires,
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      )
