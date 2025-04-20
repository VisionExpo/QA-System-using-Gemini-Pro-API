from setuptools import setup, find_packages

setup(
    name="llm_monitor",
    version="0.1.0",
    description="A package for monitoring and fine-tuning LLM applications",
    author="Vishal",
    author_email="vishal@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "pyyaml>=6.0",
        "tqdm>=4.62.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "fine-tuning": [
            "torch>=1.10.0",
            "transformers>=4.20.0",
            "datasets>=2.0.0",
            "peft>=0.2.0",
            "accelerate>=0.12.0",
            "bitsandbytes>=0.35.0",
            "tensorboard>=2.8.0",
        ],
        "evaluation": [
            "sentence-transformers>=2.2.0",
            "scikit-learn>=1.0.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
