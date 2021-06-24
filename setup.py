from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="workmaster",
    version="0.0.2",
    author="trez",
    author_email="tobias.vehkajarvi@gmail.com",
    description="Work manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trez/pyworkmaster",
    project_urls={
        "Bug Tracker": "https://github.com/trez/pyworkmaster/issues",
    },
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[
        "pyclicommander @ git+https://git.cs.kau.se/tobivehk/pyclicommander.git@ab51cec4",
    ],
    entry_points={
        "console_scripts": [
            "workmaster=pyworkmaster.__main__:main",
        ]
    },
    packages=["pyworkmaster"],
    python_requires=">=3.8.5",
)
