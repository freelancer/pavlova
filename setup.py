from setuptools import find_packages, setup

setup(
    name='pavlova',
    version='0.1',
    description='Pavlova',
    author='Escrow Team',
    author_email='eng@escrow.com',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=[
        'dateparser',
    ],
    include_package_data=True,
    zip_safe=False,
)
