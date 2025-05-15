from setuptools import setup, find_packages

setup(
    name='cli_form',
    version='1.0.0',
    description='A Unified Command-Line Form Builder',
    author='Refactored Library',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    extras_require={
        'yaml': ['PyYAML'],
    },
)