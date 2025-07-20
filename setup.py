from setuptools import find_packages, setup

setup(
    name="bgh-gender-counterfactuals",
    version="0.1.0",
    description="BGH civil appeals dataset with gender counterfactuals for bias analysis",
    author="nlietzow",
    python_requires=">=3.13",
    packages=find_packages(),
    install_requires=[
        "httpx==0.28.1",
        "tqdm==4.67.1",
        "pydantic==2.11.7",
        "openai==1.95.1",
        "tenacity==9.1.2",
        "python-dotenv==1.1.1",
        "lxml==6.0.0",
        "pymupdf==1.26.3",
        "pandas==2.3.1",
        "scikit-learn==1.7.0",
        "datasets==4.0.0",
        "jupyter==1.1.1",
        "spacy==3.8.7",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13",
    ],
)
