from setuptools import setup, find_packages

setup(
    name='SBTi-Finance Temperature Alignment Tool',
    version='0.1',
    description='This package helps companies and financial institutions to assess the temperature alignment of current'
                'targets, commitments, and investment and lending portfolios, and to use this information to develop '
                'targets for official validation by the SBTi.',
    author='Ortec Finance',
    author_email='sbti@ortec-finance.com',
    packages=find_packages(),
    package_data={
        'SBTi': ['inputs/sr15_mapping.xlsx', 'inputs/regression_model_summary.xlsx',
                 'inputs/current-Companies-Taking-Action-191.xlsx'],
    },
    include_package_data=True,
    install_requires=[],
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
