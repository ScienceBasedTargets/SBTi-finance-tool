********************
Data Requirements
********************

To calculate the temperature score and portfolio coverage the tool
requires different types of data.

-  Portfolio data: information on a security level about your
   investments such as name, identifiers, and investment values.

-  Data about the invested companies

   -  Financial data

   -  reported GHG emissions

   -  Target data: information about targets set by individual
      companies.

-  The SBTi status of the companies invested in (i.e. whether or not
   these companies have targets approved by the SBTi).

Portfolio data
--------------

When using the SBTi-Finance Tool for Temperature Scoring and Portfolio
Coverage, the user needs to supply information about the portfolio. This
must be a list of all companies invested in on a security level
including name, identifiers, ISIN codes and the value invested in each
individual company. The company identifier is used to link the data from
the portfolio, the company itself and the reported targets to each
other. This can be any code the user wants to deploy, as long as the
same code is used in all files. The ISIN codes are required to determine
the SBTi status of the companies (i.e. whether or not they have a
reduction target approved by the SBTi) in order to calculate the
Portfolio Coverage.
See :download:`portfolio data template <PortfolioTemplate.xlsx>` for an example portfolio file.

This data can be supplemented with extra fields that can be imported for
additional analysis purposes. For example you can add the market cap
buckets, investment strategies or asset class of each individual
security and examine the aggregated temperature score per asset class.


Company data
------------

For each company in the portfolio the tool needs information about each
individual company in the portfolio. We split this data in three
categories: financial data, emissions and target data.

These three categories can be imported via a single Excel file. For a
template and example file see :download:`here <DataProviderTemplate.xlsx>`



Fundamental data includes all company wide data. This includes GHG
emissions per scope as well as ISIC codes. These classifications are
used to map the targets to different regression models. For more
information, see https://siccode.com/page/what-is-an-isic-code. Based on
the chosen method to aggregate the temperature scores per company to a
portfolio score different types of financial data are also required.
Below table outlines required data for all aggregation methods.

+----------------------------------+----------------------------------+
| **Aggregation method**           | **Required financial data**      |
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
about the requirements, go to **[link to guidance doc]**

Target data
~~~~~~~~~~~

The target data should include all publicly announced GHG emissions
reduction targets for each company in the portfolio. For each target,
information is required about target type. Absolute or intensity based
GHG emissions reduction targets are currently the only types scored. For
intensity based targets, additional information is needed about the
metric used. Additionally, for each target information about the covered
scope(s), the level of coverage, the level of reduction ambition and
begin and end year of the target must be disclosed.

The temperature score is calculated for scope 1 + 2 and scope 3,
therefore in order to convert targets that only cover scope 1 or scope 2
additional information is required about the GHG emissions per scope at
the base year for scope 1 and 2 to convert such targets to scope 1 + 2
targets.

This data is available by most data providers such as CDP or Urgentem.

Please note that the tool requires the data in a specific format. For
more detail, see the :download:`data provider template <DataProviderTemplate.xlsx>` and the `Data Legends <Legends.html#input-data>`_ for the required
data formats and expect values.



Specific attention should be given to the intensity metrics. There is no
general consensus on how these are reported. For the tool all different
intensity metrics have to be mapped to 8 categories. Please refer to the
**[link to guidance]** for more detail on how to do this.

SBTi status
-----------

The SBTi status of a company indicates whether or not the company has
set a science based target that meets all criteria and is approved by
the SBTi. The tool uses the Excel file that is generated when pressing
the download button
`here <ttps://sciencebasedtargets.org/companies-taking-action/>`__. This
list is updated weekly by the SBTi. To ensure this list is up to date,
the user can download the latest list from the SBTi site here:
https://sciencebasedtargets.org/companies-taking-action/ and replace the
Excel file in the tool with the downloaded file. To do this go to
..\\SBTi\\inputs and replace the
*current-Companies-Taking-Action-xxx.xslx* file with the newer file.


