from setuptools import find_packages, setup
import sys

requirements = [
    'dateparser',
]

if sys.version_info < (3, 7):
    requirements.append('dataclasses')

setup(
    name='pavlova',
    version='0.1.3',
    description='Simplified deserialization using dataclasses',
    long_description=open('README.rst').read(),
    author='Freelancer.com',
    author_email='chris@freelancer.com',
    url='https://github.com/freelancer/pavlova',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Lesser '
        'General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3.7',
    ]
)
