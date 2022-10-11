from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fual_doc/__init__.py
from fual_doc import __version__ as version

setup(
	name="fual_doc",
	version=version,
	description="doc for files",
	author="malnoziliye@gmail.com	",
	author_email=" malnoziliye@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
