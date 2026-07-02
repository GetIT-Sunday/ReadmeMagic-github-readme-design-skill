from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ReadmeMagic",
    version="1.0.0",
    author="GetIT-Sunday",
    author_email="your-email@example.com",
    description="Create professional, beautiful, high-converting README.md files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GetIT-Sunday/ReadmeMagic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "jinja2>=3.1.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "readme-magic=readme_magic.cli:main",
        ],
    },
)

