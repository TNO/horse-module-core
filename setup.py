from setuptools import setup, find_packages
from distutils.version import StrictVersion
from importlib import import_module


def readme():
    with open('README.md') as f:
        return f.read()

extras = {
    'jsonpickle': ('jsonpickle', '0.1'),
    'websocket-client': ('websocket', '0.1'),
}
extras_require = {k: '>='.join(v) for k, v in extras.items()}

print('packages found: %s' % (find_packages(), ))
setup(name='horseModuleCore',
      version='0.1.0',
      use_2to3=False,
      author='Pieter Eendebak',
      author_email='pieter.eendebak@tno.nl',
      maintainer='Wietse van Dijk',
      maintainer_email='wietse.vandijk@tno.nl',
      description='Python-based framework for Horse modules',
      long_description=readme(),
      url='http://tno.nl',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering'
      ],
      license='Private',
      # if we want to install without tests:
      # packages=find_packages(exclude=["*.tests", "tests"]),
      packages=find_packages(),
      requires=['zmq'],  # 'pandas', 'pyqt',

      install_requires=[],
      extras_require=extras_require,
      )

version_template = '''
*****
***** package {0} must be at least version {1}.
***** Please upgrade it (pip install -U {0}) in order to use {2}
*****
'''

missing_template = '''
*****
***** package {} not found
***** Please install it in order to use {}
*****
'''

# now test the versions of extras
for extra, (module_name, min_version) in extras.items():
    try:
        module = import_module(module_name)
        try:
            if StrictVersion(module.__version__) < StrictVersion(min_version):
                print(version_template.format(module_name, min_version, extra))
        except:
            pass
    except ImportError:
        print(missing_template.format(module_name, extra))
