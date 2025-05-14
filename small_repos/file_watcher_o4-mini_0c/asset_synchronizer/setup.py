from setuptools import setup, find_packages

setup(
    name='sync_tool',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'toml',
        'flask',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'sync-tool=sync_tool.cli:main'
        ]
    }
)
