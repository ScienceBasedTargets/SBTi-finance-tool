from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="SBTi",
    version="1.0",
    description="This package helps companies and financial institutions to assess the temperature alignment of current"
    "targets, commitments, and investment and lending portfolios, and to use this information to develop "
    "targets for official validation by the SBTi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ortec Finance",
    author_email="finance@sciencebasedtargets.org",
    packages=find_packages(),
    download_url="https://pypi.org/project/SBTi-Finance-Temperature-Alignment-Tool/",
    url="https://ofbdabv.github.io/SBTi/",
    project_urls={
        "Bug Tracker": "https://github.com/ScienceBasedTargets/SBTi-finance-tool/issues",
        "Documentation": "https://ofbdabv.github.io/SBTi/",
        "Source Code": "https://github.com/ScienceBasedTargets/SBTi-finance-tool/",
    },
    keywords=["Climate", "SBTi", "Finance"],
    package_data={
        "SBTi": [
            "inputs/sr15_mapping.xlsx",
            "inputs/regression_model_summary.xlsx",
            "inputs/current-Companies-Taking-Action-191.xlsx",
        ],
    },
    include_package_data=True,
    install_requires=["pandas", "xlrd", "pydantic"],
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "nose2",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
    ],
    test_suite="nose2.collector.collector",
)
