from setuptools import setup, find_packages

setup(
    name="slips-sdk",
    version="0.1.0",
    author="Jenil Vekariya",
    author_email="vekariyajenil888@gmail.com",
    description="SDK for interacting with slips IDS components",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["slips", "slips.*"]),
    include_package_data=True,  # Include files specified in MANIFEST.in
    install_requires=[
        # Add your package dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Ubuntu22.04",
    ],
    python_requires='>=3.10',
)
