from setuptools import setup

version = '0.0.1'

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name="pyc2e",
    packages=["pyc2e"],
    entry_points={
        "console_scripts": ['pyc2e=pyc2e.__main__:main']
    },
    version=version,
    description="Script injection for the Creatures Evolution Engine",
    long_description=long_descr,
    long_description_content_type="text/x-rst",
    author="pushfoo",
    author_email="pushfoo@gmail.com",
    url="https://github.com/pushfoo/pyc2e",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.7",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities"
    ],
    keywords=[
        "modding",
        "tools",
        "creatures",
        "script injection",
        "caos"
    ],
    python_requires='>=3.7'
)
