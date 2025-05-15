from setuptools import setup, find_packages

setup(
    name='datapipe',
    version='1.0.0',
    description='Modular ETL pipeline framework using only built-in modules',
    author='Unified Team',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
)