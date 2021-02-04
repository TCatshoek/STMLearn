import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stmlearn",
    version="0.0.2",
    author="T. Catshoek",
    author_email="tomcatshoek@zeelandnet.nl",
    description="Python state machine learning library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TCatshoek/STMLearn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'tabulate',
        'graphviz',
        'pygtrie',
    ]
)