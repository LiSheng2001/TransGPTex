import setuptools

from transgptex import __version__, __author__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="transgptex",
    version=__version__,
    author=__author__,
    author_email="lisheng@nuaa.edu.cn",
    description="Translate Latex articles through LLM and compile them into PDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LiSheng2001/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "openai", 
        "arxiv", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'tgtex=transgptex.command_line:main',
        ]
    },
)
