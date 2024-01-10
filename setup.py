from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Yandex Cloud driver for the libCloud'
LONG_DESCRIPTION = 'Yandex cloud external driver for the libCloud'


setup(
    name="libcloud_yandex",
    version=VERSION,
    author="Dmitrii Maevskii",
    author_email="<dsmaevskii@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests>=2.30','grpcio>=1.59.2','yandexcloud>=0.252.0'],


    keywords=['python', 'libcloud_yandex'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
