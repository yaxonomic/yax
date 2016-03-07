from setuptools import find_packages, setup

with open("README.rst") as fh:
    long_description = fh.read()

setup(
    name='yax',
    version='0.0.1dev',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['click'],
    scripts=['scripts/yax']
)
