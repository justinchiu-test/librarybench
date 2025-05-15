from setuptools import setup, find_packages

setup(
    name='clitools',
    version='1.0.0',
    description='Unified CLI tools with multiple personas',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'toml',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)