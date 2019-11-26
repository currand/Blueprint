from setuptools import setup, find_packages

setup(
	name="blueprint",
	packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
	install_requires=[
	'Jinja2>=2.10.3',
	'jinja2schema>=0.1.4',
	'PyYAML>=5.1.2',
	'jinja2-time>=0.2.0',
	],
	python_requires='>=3.6'

)
