from setuptools import setup, find_packages

setup(
    name="earnings_options_strategy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
    ],
    python_requires=">=3.8",
) 