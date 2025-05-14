from setuptools import setup, find_packages

setup(
    name="creative_vault",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow",        # For image processing
        "numpy",         # For numerical operations
        "pytest",        # For testing
        "pydantic",      # For data validation and settings management
        "trimesh",       # For 3D model handling
        "matplotlib",    # For visualization
        "psutil",        # For system resource monitoring
    ],
    python_requires=">=3.8",
    description="Incremental backup system for digital artists with visual diff, timeline browsing, selective restoration, and asset deduplication",
    author="CreativeVault Team",
)