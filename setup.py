from setuptools import find_packages, setup

from fantail import __version__

setup(
    name='fantail',
    version=__version__,
    license='BSD',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    description='fantail is (yet another) static site generator written in Python',
    #long_description=open('README.rst', 'r').read(),
    url='https://github.com/sjkingo/fantail',
    install_requires=['jinja2',],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fantail=fantail.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
    ],
)
