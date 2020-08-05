from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='SBTi-Finance Temperature Alignment Tool',
    version='0.2',
    description='This package helps companies and financial institutions to assess the temperature alignment of current'
                'targets, commitments, and investment and lending portfolios, and to use this information to develop '
                'targets for official validation by the SBTi.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Ortec Finance',
    author_email='finance@sciencebasedtargets.org',
    packages=find_packages(),
    url = 'https://github.com/OFBDABV/SBTi',
    download_url = 'https://github.com/OFBDABV/SBTi/archive/v_02.tar.gz',
    keywords = ['Climate', 'SBTi', 'Finance'],
    package_data={
        'SBTi': ['inputs/sr15_mapping.xlsx', 'inputs/regression_model_summary.xlsx',
                 'inputs/current-Companies-Taking-Action-191.xlsx'],
    },
    include_package_data=True,
    install_requires=['pandas',
                      'xlrd'],
    python_requires='>=3.6',
    extras_require={
        'dev': [
            'nose2',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite='nose2.collector.collector',
)
