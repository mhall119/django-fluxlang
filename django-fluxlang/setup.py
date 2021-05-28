import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-fluxlang',  
    version='0.1',
    author="Michael Hall",
    author_email="mhall119@gmail.com",
    description="A Django ORM-like way to build Flux queries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhall119/django-fluxlang",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'Django>=3.0.0',
        'influxdb-client'
    ],
)