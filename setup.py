from setuptools import setup

setup(
    name='SBTi-Finance Temperature Alignment Tool',
    version='0.1',
    description='This package helps companies and financial institutions to assess the temperature alignment of current'
                'targets, commitments, and investment and lending portfolios, and to use this information to develop '
                'targets for official validation by the SBTi.',
    author='Ortec Finance',
    author_email='sbti@ortec-finance.com',
    packages=['SBTi'],
    install_requires=[],
    test_suite='nose2.collector.collector',
)
