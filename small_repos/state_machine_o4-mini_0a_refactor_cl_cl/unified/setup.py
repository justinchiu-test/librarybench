from setuptools import setup, find_packages

setup(
    name="unified_statemachine",
    version="1.0.0",
    description="Unified State Machine Library",
    author="Unified Team",
    include_package_data=True,
    package_dir={"": "."},
    # Include both the original modules and the new src package
    py_modules=[
        "business_process_analyst", 
        "game_developer", 
        "robotics_engineer", 
        "ux_prototyper"
    ],
    # Make sure the src package is included
    packages=[
        "src", 
        "src.statemachine", 
        "src.api",
        "src.interfaces",
        "src.interfaces.business_process_analyst",
        "src.interfaces.game_developer",
        "src.interfaces.robotics_engineer",
        "src.interfaces.ux_prototyper",
        "src.utils"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)