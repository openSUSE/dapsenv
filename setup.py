#!/usr/bin/env python3
"""dapsenv Setup

See also:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages


def requires(filename):
    """Returns a list of all pip requirements

    :param filename: the Pip requirement file (usually 'requirements.txt')
    :return: list of modules
    :rtype: list
    """
    modules = []
    with open(filename, 'r') as pipreq:
        for line in pipreq:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            modules.append(line)
    return modules


# --------------------------------------------------
setupdict = dict(
    name='dapsenv',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.1',

    description='Manage Meta Information in DocBook5-XML Files',
    # long_description=long_description,

    # The project's main homepage.
    url='https://github.com/openSUSE/dapsenv',

    # Author details
    author='Manuel Schnitzer',
    author_email='webmaster@mschnitzer.de',

    # Choose your license
    license='GPL-3.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Supported Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords=['daps', 'build', 'XML'],

    # Includes data files from MANIFEST.in
    #
    # See also:
    # http://stackoverflow.com/a/16576850
    # https://pythonhosted.org/setuptools/setuptools.html#including-data-files
    include_package_data=True,

    install_requires=requires('requirements.txt'),

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages('source'),
    package_dir={'': 'source'},
    # include_package_data=True,
    # zip_safe=False,

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    #install_requires=['lxml'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': requires('devel_requirements.txt'),
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'dapsenv': ['template/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'dapsenv=dapsenv:main',
        ],
    },

    # Required packages for testing
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-catchlog'],
)

# Call it:
setup(**setupdict)
