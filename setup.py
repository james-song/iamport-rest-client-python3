from setuptools import setup, find_packages
import codecs

install_requires = ['requests']


def readme():
    with codecs.open('README.rst', encoding='utf-8') as f:
        return f.read()


setup(
    name='iamport-rest-client2',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license='MIT License',
    description="REST client for I'mport;(http://www.iamport.kr)",
    long_description=readme(),
    url='https://github.com/james-song/iamport-rest-client-python3',
    author='RakGyu Song',
    author_email='reeoss@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
