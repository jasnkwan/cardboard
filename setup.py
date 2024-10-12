"""
Package configuration
"""

from setuptools import setup, find_packages

setup(
    name='cardboard',
    version='0.1.0',
    description='A React UI for data dash boards',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jason Kwan',
    author_email='jasnkwan@gmail.com',
    url='https://github.com/jasnkwan/cardboard',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
