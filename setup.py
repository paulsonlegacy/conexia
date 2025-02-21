from setuptools import setup, find_packages

# Read dependencies from requirements.txt
def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="conexia",  
    version="0.2.0", # Update this version on each release
    author="Paulson Bosah",
    author_email="paulsonbosah@gmail.com",
    description="A Python library for fetching real IP and Port using STUN servers and easily integratable with Python backend frameworks.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/paulsonlegacy/conexia",  # Replace with your GitHub repo URL
    packages=find_packages(exclude=["tests*", "examples*"]),  # Exclude test/example directories
    install_requires=read_requirements(),  # Install dependencies from requirements.txt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Specify the minimum Python version
    include_package_data=True,  # Include non-code files (like README.md)
    entry_points={
        "console_scripts": [
            "conexia = conexia.cli:cli_entry_point",  # CLI entry point (optional)
        ]
    },
)
