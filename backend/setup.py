#!/usr/bin/env python3
"""
Setup configuration for NoteBook backend package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "NoteBook - GraphQL Learning Project with Distributed Replication"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="notebook-backend",
    version="1.0.0",
    author="Arison99",
    description="GraphQL learning project with CouchDB distributed replication",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Arison99/NoteBook",
    
    # Package configuration
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Entry points
    entry_points={
        'console_scripts': [
            'notebook-server=notebook.api.app:main',
            'notebook-monitor=scripts.monitor_cluster:main',
        ],
    },
    
    # Classifiers
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    
    # Additional metadata
    keywords="graphql flask couchdb replication distributed-systems",
    project_urls={
        "Bug Reports": "https://github.com/Arison99/NoteBook/issues",
        "Source": "https://github.com/Arison99/NoteBook",
        "Documentation": "https://github.com/Arison99/NoteBook/blob/main/README.md",
    },
)