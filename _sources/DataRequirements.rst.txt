********************
Data Requirements
********************

To calculate your temperature score and portfolio coverage, the tool
requires several types of data.

-  Portfolio data: information on a security level about your
   investments such as name, identifiers, and investment values.

-  Data about the investee companies

   -  Fundamental data

   -  Reported GHG emissions

   -  Target data: information about GHG emissions reduction targets set
      by individual companies.

-  SBTi status of the companies invested in (i.e. whether these
   companies have targets approved by the SBTi or not).

Portfolio data
--------------

When using the SBTi-Finance Tool for Temperature Scoring and Portfolio
Coverage, the user needs to supply information about the portfolio. This
must be a list of all investee companies on a security level, including
name, identifiers, ISIN codes, and the value invested in each individual
company. The company identifier is used to link the data from the
portfolio, the fundamental data and the reported targets to each other.
This can be any identifier the user wants to deploy, if the same
identifier is used in all files. The ISIN codes are required to
determine the SBTi status of the companies to calculate the Portfolio
Coverage.
See :download:`portfolio data template <PortfolioTemplate.xlsx>` for an example portfolio file.

For additional analyses, you can supplement this data with additional
fields, which are available for import. For example, you can add the
market cap buckets, investment strategies or asset classes of each
individual security and then analyze the aggregated temperature score
per these additional fields/categories.


Company data
------------

The tool needs information about each individual company in the
portfolio. We split this data in three categories: financial data,
emissions, and target data.

All three categories are available for import via a single Excel file.
Here is a template :download:`here <DataProviderTemplate.xlsx>`.

.. note :: Please note that the tool requires the data in a specific format. For more detail, see the data provider template and the Data Legends for the required data formats and expect values.

Fundamental data
~~~~~~~~~~~~~~~~~~~~

The fundamental data tab in Excel includes all company wide data
including GHG emissions per scope and ISIC codes. This open source
industry classification standard is used to map the targets to different
regression models. For more information, see
https://siccode.com/page/what-is-an-isic-code. Other financial data is
required in order to aggregate individual temperature scores to a
portfolio temperature score, which depends on the method you choose. The
table below outlines required data for all aggregation methods.

+----------------------------------+----------------------------------+
| **Aggregation Method**           | **Required Financial Data**      |
+==================================+==================================+
| Weighted average temperature     | None                             |
| score (WATS)                     |                                  |
+----------------------------------+----------------------------------+
| Total emissions weighted         | None                             |
| temperature score (TETS)         |                                  |
+----------------------------------+----------------------------------+
| Market Owned emissions weighted  | Company market cap               |
| temperature score (MOTS)         |                                  |
+----------------------------------+----------------------------------+
| Enterprise Owned emissions       | Company enterprise value         |
| weighted temperature score       |                                  |
| (EOTS).                          |                                  |
+----------------------------------+----------------------------------+
| EV + Cash emissions weighted     | Company enterprise value and     |
| temperature score (ECOTS)        | cash equivalents                 |
+----------------------------------+----------------------------------+
| Total Assets emissions weighted  | Company total assets             |
| temperature score (AOTS)         |                                  |
+----------------------------------+----------------------------------+
| Revenue emissions weighted       | Company revenues                 |
| temperature score (ROTS)         |                                  |
+----------------------------------+----------------------------------+

The financial data used should be regarding the same period as the
reported emissions. Preferably the latest reported. For more information
about the requirements, see the `guidance <https://sciencebasedtargets.org/wp-content/uploads/2020/10/Financial-Sector-Science-Based-Targets-Guidance-Pilot-Version.pdf>`__ documentation.

Target data
~~~~~~~~~~~

This should include all publicly announced GHG emissions reduction
targets for each company in the portfolio. For each target, information
is required on target type, currently we only score absolute or
intensity-based GHG emissions reduction targets. For intensity-based
targets, information is needed about the metric used. Additionally, for
each target, information on scope(s), level of coverage, level of
reduction ambition, and begin and end year of the target must be
included in the file.

The temperature score is calculated for Scopes 1 + 2 and 3. In order to
convert targets that only cover scope 1 or scope 2, additional
information is required on GHG emissions per scope at the base year for
scope 1 and 2 to convert such targets to targets.

Specific attention should be given to intensity metrics as there
currently lacks consensus in reporting method. For the tool, all
intensity metrics have to be mapped to one of eight categories. Please
refer to the **[link to guidance]** for more detail on how to do this.

SBTi status
-----------

The SBTi status of a company indicates whether or not the company has
set a science based target has been approved by the SBTi. This tool uses
the Excel file that is generated when pressing the download button
`here <http://ttps://sciencebasedtargets.org/companies-taking-action/>`__.
This list is updated weekly, to ensure your list is up to date, the user
can download the latest list from the SBTi site here:
https://sciencebasedtargets.org/companies-taking-action/ and replace the
Excel file in the tool with the downloaded file. To do this go to
..\\SBTi\\inputs directory and replace the
*current-Companies-Taking-Action-xxx.xslx* file with the newer file.


