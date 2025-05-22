from setuptools import find_packages, setup

setup(
    name="automotive_hardware",
    version="0.1.0",
    packages=find_packages(include=['hardware*']),
    install_requires=[
        'pydantic>=1.10.0',
        'numpy>=1.21.0',
        'pyserial>=3.5',
        'pyserial-asyncio>=0.6',
        'pyyaml>=6.0',
    ],
    extras_require={
        'test': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.20.0',
            'pytest-cov>=3.0.0',
        ],
        'dev': [
            'black>=22.0.0',
            'isort>=5.10.0',
            'mypy>=0.910',
            'flake8>=4.0.0',
        ],
    },
    python_requires='>=3.8',
    author="Jonathan Marien",
    author_email="jon@chron0.tech",
    description="Hardware abstraction layer for automotive security testing",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jondmarien/automotive-security-capstone",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
