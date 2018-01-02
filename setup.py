from setuptools import setup

setup(
    name="pyvainglory",
    packages=['pyvainglory'],
    version="0.0.1a",
    description="A wrapper for the madglory Vainglory API, complete with synchronous and asynchronous client implementations.",
    author="xKynn",
    author_email="xkynn@github.com",
    url="https://github.com/xKynn/PyVainglory",
    download_url="https://github.com/xKynn/PyVainglory/archive/0.0.1a.tar.gz",
    keywords=['vainglory', 'asyncvainglory', 'async-vainglory', 'async_vainglory', 'pyvainglory'],
    classifiers=[],
    install_requires=[
        "aiohttp",
        "requests"
    ],
    python_requires='>=3.5',
    package_data={
        '': ['data/*.json', 'data/localization/*.ini']
    }
)
