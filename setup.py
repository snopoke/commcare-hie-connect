from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt')


setup(
    name='OpenHIE Connect CommCare',
    version='1.0',
    description='',
    author='Simon Kelly',
    author_email='simongdkelly@gmail.com',
    url='http://www.python.org/sigs/distutils-sig/',
    install_requires=[str(ir.req) for ir in install_reqs]
)
