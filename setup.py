from setuptools import setup, find_packages

setup(
    name="qa_system",
    version="0.1.0",
    description="A Question and Answer system using Gemini Pro API",
    author="Vishal Gorule",
    author_email="gorulevishal984@gmail.com",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=0.19.0",
        "pillow>=9.0.0",
        "requests>=2.25.0",
        "pymupdf>=1.19.0",
        "python-docx>=0.8.11",
        "sentence-transformers>=2.2.0",
        "astrapy>=0.5.0",
        "langsmith>=0.0.30"
    ],
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
