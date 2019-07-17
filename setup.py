import setuptools

setuptools.setup(
    name='mergedb',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='Grayson Head',
    author_email='grayson@graysonhead.net',
    url='https://github.com/graysonhead/mergedb',
    packages=setuptools.find_packages(),
    install_requires=[
        'pyyaml>=5.1.0',
        'colorama>=0.4.1',
        'jinja2>=2.10.1',
        'pprint>=0.1'
    ],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'mergedb = mergedb.__main__:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
)
