Introduction to temperature scoring and portfolio coverage methods
==================================================================

Three methods are currently supported by
the \ `SBTi <https://sciencebasedtargets.org/financial-institutions>`__ for
setting targets on scope 3 portfolio emissions: the Sectoral
Decarbonization Approach (SDA), the SBT Portfolio Coverage, and the SBT
Temperature Scoring. The latter two methods, Portfolio Coverage and
Temperature Scoring, require assessing the targets disclosed by the
companies within a financial institution’s portfolio.

Financial institutions may use the portfolio coverage
and/or \ `temperature scoring
methods <https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf>`__ to
set targets for their corporate instruments, including corporate debt,
listed equity and bonds, and private equity and debt (See relevant
“Required Activities” in Table 5-2 of the \ `SBTi
guidance <https://sciencebasedtargets.org/wp-content/uploads/2020/10/Financial-Sector-Science-Based-Targets-Guidance-Pilot-Version.pdf>`__ to
drive adoption of science-based targets).

To use the \ *portfolio coverage method*, financial institutions commit
to engaging with their investees to set their own approved science-based
targets, such that the financial institution is on a linear path to 100%
SBT portfolio coverage by 2040. As the fulfillment of portfolio coverage
targets mean that investees’ SBTs have been approved by SBTi, the 2040
timeline has been determined to allow companies enough time to implement
their target to ultimately achieve an economy-wide transition to net
zero by 2050.

To use the \ *temperature scoring method*, financial institutions
determine the current temperature score of their portfolio based on the
public GHG emission reduction targets of their investees (these targets
include SBTs and any other valid public GHG targets that meet the method
criteria). Financial institutions set targets to align their base year
portfolio temperature score to a long-term temperature goal (e.g. 2°C,
well-below 2°C, 1.5°C). The temperature scoring method is an open source
framework to enable the translation of corporate GHG emission reduction
targets into temperature scores at a target, company, and a portfolio
level. The method provides a protocol to enable the aggregation of
target level scores to generate a temperature rating for a company based
on the ambition of its targets. Finally, the method defines a series of
weighting options that can enable financial institutions and others to
produce portfolio level temperature ratings.

Why has SBTi built this tool?
-----------------------------

There has been a growing interest in methods to measure the alignment of
companies and investment portfolios with the Paris Agreement. The
success of the Science Based Targets initiative has seen a rapid growth
in the number of companies with emission reduction targets approved by
the SBTi, and therefore, a growing number of companies claiming
alignment to the long term temperature goals set out in the Paris
Agreement.   

The SBTi has developed a codebase to function as a calculator for the
portfolio coverage and temperature scoring methods. This tool is fed
with the necessary data to generate temperature scores at the company
and portfolio level, in addition to providing analytics on target
setting and company emission reduction ambitions. It also gives users
access to what-if analysis, to aid their decision-making process. The
code reflects the logical steps that are outlined in the publicly
available \ `*temperature scoring
methodology* <https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf>`__,
developed
by \ `*CDP* <https://www.cdp.net/>`__ and `*WWF* <https://wwf.panda.org/>`__.

The tool was created to enable the widespread implementation of the
method by data providers and financial institutions, to work with any
data source and in most IT environments. For each method, the tool
provides the following outputs:

-  Portfolio coverage: generate the % of the portfolio currently covered
   by SBTi-approved targets.

-  Temperature scoring: generate the current temperature score of the
   portfolio (in addition to the individual temperature scores of the
   portfolio companies). It also enables the generation of a series of
   what-if scenarios to showcase how this temperature score could be
   reduced.

Why have we built the SBTi-Finance tool in this way?
----------------------------------------------------

To help financial institutions fight climate change, SBTi wants the tool
to be accessible, useful, and used by as many finance professionals and
other users as possible. If it is easy to access, not seen as a
compliance tool only used once a year, but a tool to support the
investment process, it is more likely it will be utilized widely.
Therefore, when SBTi started the development process we set up a list of
requirements for the tool. Some of the high-level requirements were:

-  Distribution – most investment professionals should have easy access
   to the tool

-  Transparent – with full output audit trail and open methodology

-  Data agnostic – to be used with any data provider or an institution’s
   own data lake

-  Any infrastructure – to be integrated with service providers’ or
   homegrown decision support solutions

-  Workflow tool – to be integrated in investment professionals’ daily
   workflow

-  Data security – to make sure financial portfolio data is not
   compromised

-  Scale – be able to use the tool at scale for many portfolios and
   aggregated on financial institution level

-  Continued development – ensure enhancement of the method and tool for
   future requirements

Given these requirements, the SBTi determined an open-source
Python-based solution to be most appropriate. Such tool can be
integrated into existing solutions, in many cases making use of the same
secure infrastructure as inhouse or commercial applications. As the tool
pulls data from existing integration of data providers and/or internal
data lakes, there is no need to go outside of this infrastructure to
access or deliver necessary data. Hence, no data that is not already
within the institution’s domain needs to enter or exit the institution
to use the tool. The approach brings the model to the data, rather than
the other way around.

SBTi-Finance launched an RfP for building the codebase to turn the
methodology into a calculation engine early 2020. The selected
SBTi-Finance tool development project partners are Ortec Finance and the
OS-Climate.

To make sure we built a tool that from the outset could work in as many
different environments and for as many different users as possible, we
reached out to users and data and service providers and invited them to
work with us in our project team. This gave both users and data
providers the opportunity to influence the development process and to
prepare and develop their own solutions, data, and processes to work
with the tool. This has been very helpful in getting their perspectives,
to make sure the tool work with as many data providers’ data as possible
and that it fits with many users’ existing workflow.

A strong confirmation of the various tool use cases is that fact that a
number of data/service providers have developed or are in the process of
developing various solutions based on the tool and the methodology, to
offer their clients. This collaboration also gives the SBTi-Finance tool
a wider reach than what the SBTi could have achieved otherwise and the
tool should be available natively in their existing infrastructure for a
significant proportion of the financial institutions globally. This
integration should also ensure that the tool can be used at scale, to
help large and small financial institutions alike to quickly analyze all
their portfolios’ and constituents’ temperature scores.

The open-source nature of the codebase means that any user, data- or
service provider can use the code to build their own applications around
the SBTi-Finance Tool. It also means that it is available for any user
to integrate into their own infrastructure, without any licensing cost.
This should also ensure that the code continues to be developed both by
the SBTi, data and service providers and the open source community.

The tool also provides full transparency with regards to how the tool
and methodology fit together through the open-source nature of both the
codebase and the methodology. We also have provided easy to use
functionality to extract every single data point generated by the tool,
to provide a full audit trail and transparency into how the temperature
score is calculated.

During Summer 2020 we ran a public beta-testing phase open to any
organization or individual. The beta-testing phase included more than
110 registered beta-testers. Users provided feedback on the tool’s
functionality, documentation requirements, performance, and usability.
This feedback has been incorporated in the final release version.

Altogether, our conversations with users and data providers and the
feedback from 110 beta testers indicates that the development process
and the structure of the SBTi-Finance Tool has the potential to become
an integrated experience and that it could become as natural for a
portfolio manager or analysts to use as their DCF model or attribution
report. In turn, this should ensure that portfolio and company
temperature scores stay top-of-mind for finance professionals and that
this ultimately leads to more efficient engagement processes and GHG
emissions reductions in the real economy.

What can I use the SBTi-Finance tool for?
-----------------------------------------

The SBTi-Finance Temperature Scoring and Portfolio Coverage tool enables
analysis of companies, sectors, countries, investment strategies and
portfolios to understand how they contribute to climate change. You can
for example:

-  Measure your portfolio's current temperature score

-  Identify the biggest contributors on an individual company, country,
   and sector basis

-  Use the tool as an aid for strategic allocation and securities
   selection decisions

-  Analyze what effect changes in your portfolio might have on the
   portfolio temperature score

-  Model impact of engagement on your temperature score, that is, how
   your score can improve if you are able to convince an investee
   company to set or improve GHG emissions reduction targets

-  Identify which company engagements would have the biggest impact on
   your portfolio's temperature score

-  Plan engagement strategies based on your modelling

-  Fulfil regulatory reporting criteria, e.g. Article 173 in France and
   the EU Disclosure regulation, regarding current portfolio alignment
   with Paris Agreement

-  Help you to create an action plan for reaching your emission
   reduction target

Given these possible insights, as confirmed by our beta testing survey,
the tool is relevant for a wide range of stakeholders. For instance:

-  Portfolio managers - to support strategic allocation decisions and
   input into ESG discussions with corporate management

-  Financial analysts - to use the temperature score as an input into
   the cost of capital for valuation modelling

-  ESG analysts - to plan and execute corporate engagement strategies

-  Risk managers – for input into climate related risk models

-  Compliance officers – for EU Disclosure regulation and Article 173
   reporting

-  Data and service providers – to provide company temperature scores
   and portfolio analytics for their users

-  CIOs – to help to understand the portfolios’ ESG position

-  NGOs – for further research to enhance climate related methodologies

What data do I need to use the tool?
------------------------------------

The tool itself is data agnostic and has no built-in databases. This
means that users need to import all needed data to perform the analysis
and can use any data source with the necessary data available. This data
can come from a variety of sources but must be inputted in the required
formats. The data providers that we have worked with during the
development, have built or are in the process of building solutions to
help with this process. Four types of data are needed to run the tool.
These are described in the table below.

+--------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Portfolio holdings             | -  Company name                                                                                                                                                                      |
|                                |                                                                                                                                                                                      |
|                                | -  ISIC (International Standard Industrial Classification) sector classification, and                                                                                                |
|                                |                                                                                                                                                                                      |
|                                | -  ISIN and/or FIGI, if available. Other company identifier can also be used together with ISINs or FIGIs and are required to match identifiers from the three data sources below.   |
|                                |                                                                                                                                                                                      |
|                                | -  Market value of portfolio position for each company, using one common portfolio currency                                                                                          |
+--------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Corporate GHG Targets          | This refers to the data required to analyze a corporate GHG emissions reduction targets, including:                                                                                  |
|                                |                                                                                                                                                                                      |
|                                | -  Target types (absolute/intensity)                                                                                                                                                 |
|                                |                                                                                                                                                                                      |
|                                | -  Base year                                                                                                                                                                         |
|                                |                                                                                                                                                                                      |
|                                | -  Target year                                                                                                                                                                       |
|                                |                                                                                                                                                                                      |
|                                | -  Scope coverage                                                                                                                                                                    |
|                                |                                                                                                                                                                                      |
|                                | -  Boundary coverage within scope                                                                                                                                                    |
|                                |                                                                                                                                                                                      |
|                                | -  % achieved                                                                                                                                                                        |
|                                |                                                                                                                                                                                      |
|                                | -  Intensity activity (if appliable)                                                                                                                                                 |
+--------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Corporate GHG Emissions Data   | Scope 1+2 and scope 3 emissions data, reported or modelled.                                                                                                                          |
+--------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Corporate Financial data       | Seven weighting option are currently available to aggregate company scores to produce portfolio scores. Depending on the option chosen, the following data may be required:          |
|                                |                                                                                                                                                                                      |
|                                | a. Invested value (holdings)                                                                                                                                                         |
|                                |                                                                                                                                                                                      |
|                                | b. Market capitalization                                                                                                                                                             |
|                                |                                                                                                                                                                                      |
|                                | c. Enterprise value                                                                                                                                                                  |
|                                |                                                                                                                                                                                      |
|                                | d. Cash and equivalents                                                                                                                                                              |
|                                |                                                                                                                                                                                      |
|                                | e. Total assets                                                                                                                                                                      |
|                                |                                                                                                                                                                                      |
|                                | f. Revenue                                                                                                                                                                           |
+--------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

See `Data Requirements <https://sciencebasedtargets.github.io/SBTi-finance-tool/DataRequirements.html>`__ section for more detailed information.

Also refer to the full methodology for \ `temperature
scoring <https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf>`__.

Where can I find the data?
--------------------------

Commercial data providers such as Bloomberg, CDP, ISS, MSCI, TruCost and
Urgentem can provide some or all the data needed for the SBTi-Finance
Tool.

There is also a free data set available with corporate GHG targets data
on SBTi's website. This includes data of all the companies that have set
emissions reduction targets that have been approved by SBTi and is
updated on a weekly basis. You can download an Excel-file with the data
here: \ `*https://sciencebasedtargets.org/companies-taking-action/* <https://sciencebasedtargets.org/companies-taking-action/>`__.

It is likely that your portfolio includes companies that are not in the
list of companies with SBTi-approved targets, but that have publicly
announced targets. Commercial data providers such as those listed above
can provide target data for these companies.

Overview of how the tool works
------------------------------

The calculation methodology consists of four key steps, each requiring
specific data points that are inputted at the beginning of the process.
These data points are then used to convert the corporate GHG emission
reduction targets into temperature scores at the company and the
portfolio level.

|image3|

**Step 1:** **Converting publicly stated targets to temperature
scores**. The targets are first filtered and are - if valid - translated
to a specific temperature score, based on the relevant regression model
[Section 1.3 in the
`methodology <https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf>`__].
The sector classification of the company is used to ensure that the
target is correctly mapped to the appropriate regression model e.g. a
target for power generation must be mapped to the power sector pathway
and corresponding regression model. This process enables the translation
of target ambition over a certain target time period into a temperature
score. For example, a 30% reduction target in absolute GHG emissions
over 10 years can be converted into a temperature score of 1.76°C. It
should be noted that those companies without a valid target are assigned
a default temperature score [Section 1.4 in the
`methodology <https://sciencebasedtargets.org/wp-content/uploads/2020/09/Temperature-Rating-Methodology-V1.pdf>`__],
rather than being excluded from the analysis.

**Step 2:** **Aggregate across targets (if applicable) to a company
level temperature score**. Reported corporate GHG emission data is
employed to aggregate company level temperature scores.

**Step 3:** **Aggregate individual company temperature scores to
portfolio level scores.** All the individual temperature scores per
company in a portfolio are then combined with portfolio financial data
to generate scores at the portfolio level.

**Step 4:** **Run what-if analysis via the scenario generator**. After
the initial score calculations, a scenario generator can be used to
determine how certain actions, e.g. engagement, can change the portfolio
temperature score over time. When running these what-if scenarios, the
temperature score is recalculated with the assumption that, based on
various engagements, some or all the companies in the portfolio decided
to set (more ambitious) targets. The following what-if analyses are
included in the tool:

+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Scenario 1   | In this scenario all companies in the portfolio that did not yet set a valid target have been persuaded to set 2.0 Celsius (C) targets. This is simulated by changing all scores that used the default score to a score of 2.0C.    |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Scenario 2   | In this scenario all companies that already set targets are persuaded to set “Well Below 2.0C (WB2C) targets. This is simulated by setting all scores of the companies that have valid targets to at most 1.75C.                    |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Scenario 3   | In these scenarios the top 10 contributors to the portfolio temperature score are persuaded to set 2.0C targets.                                                                                                                    |
|              |                                                                                                                                                                                                                                     |
|              | -  Scenario 3a: All top 10 contributors set 2.0C targets.                                                                                                                                                                           |
|              |                                                                                                                                                                                                                                     |
|              | -  Scenario 3b: All top 10 contributors set WB2C, i.e. 1.75C targets.                                                                                                                                                               |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Scenario 4   | In this scenario the user can specify (by adding “TRUE” in the engagement\_targets-column in the portfolio data file) which companies it wants to engage with to set 2.0C or WB2C targets.                                          |
|              |                                                                                                                                                                                                                                     |
|              | -  Scenario 4a: All companies that are marked as engagement targets set 2.0C targets                                                                                                                                                |
|              |                                                                                                                                                                                                                                     |
|              | -  Scenario 4b: All companies that are marked as engagement targets set WB2C targets.                                                                                                                                               |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

What are the outputs the tool generates?
----------------------------------------

The temperature score can be calculated for all time frames (short,
medium, long term) and scope (Scope 1, 2, 3) combinations covered by the
SBTi methodology. The table below provides an overview of these:

|image4|

The temperature score calculation is available for the following levels:

-  Portfolio temperature score: the aggregated score over all companies
   in the portfolio

-  Grouped temperature score: using the “group by” option, the user can
   get the aggregated temperature score per category in a chosen field
   (e.g. per region or per sector). 

-  Company temperature score: the temperature score of an individual
   company 

The figure below provides illustrative outputs for grouped temperature
scores by region and sector. These insights help inform use cases such
as more targeted engagement strategies, aiding securities selection
decisions, etc.

***Illustrative output of the temperature score on portfolio level,
grouped by region and sector***

|image5|

The next figure provides a visualization of the outputs when looking at
the temperature score per company. This level of granularity of the tool
enables users to zoom in on individual scores for, e.g. informing
engagement and/or monitoring temperature score progress of investees.

***Illustrative visualization of the temperature score outputs per
company***

|image6|

For the portfolio temperature score and the grouped temperature score,
additional more granular information is reported about the composition
of the score:

-  Contributions: the level to which each company contributes to the
   total temperature score based on the chosen aggregation method. This
   value is split up into company temperature score and relative
   contribution (for example the weight of the investment in the company
   relative to the total portfolio when using the WATS aggregation
   method). 

-  The percentage of the score that is based on targets vs. the
   percentage based on the default score 

-  For the grouped temperature scores: the percentage each group
   contributes to the portfolio temperature score. For example: how much
   each region or sector contributes to the total score. 

The table below, taken from a Jupyter Notebook implementation of the
tool (see ,http://getting-started.sbti-tool.org/ for executing your own
rungs of the Jupyter Notebook), highlights the companies with the
highest contribution to the portfolio temperature score and at the same
time displays ownership and portfolio weight to give the user an
indication of where an engagement may be more successful, purely from a
quantitative perspective.

***Illustrative output table of the temperature score and contribution
analysis on company level***

|image7|

The figure below depicts similar analysis in a more visual format. What
can be seen in the figure is the relative contributions to the sector
temperature scores.

***Illustrative visualization of the temperature score outputs and
contribution results grouped per sector***

|image8|

For the company temperature scores, you can let the tool generate all
underlying data, which provides full transparency and gives the user the
full audit trail for how the final temperature score has been
calculated. This data output provides:

-  Portfolio data 

-  Financial data 

-  GHG emissions 

-  Used target and all its parameters 

-  Values used during calculation such as the Linear annual reduction
   (LAR), mapped regression scenario, and parameters for the formula to
   calculate the temperature score. 

You can also anonymize the output data, which removes all names and
identifiers. This is particularly useful for sharing results of your
temperature score without having to reveal your holdings, for example
for submitting your temperature score to the Target Validation Team
(TVT) at SBTi to get your own GHG emissions reduction target approved. At
the same time, it provides the opportunity to audit the scores during
the validation process.

For a more detail please see Jupyter notebook examples found
`here <https://sciencebasedtargets.github.io/SBTi-finance-tool/getting_started.html#google-colab>`__.


.. |image3| image:: image3.png
   :width: 6.50000in
   :height: 2.02222in
.. |image4| image:: image4.png
   :width: 5.54166in
   :height: 1.20675in
.. |image5| image:: image5.png
   :width: 6.30297in
   :height: 3.79220in
.. |image6| image:: image6.png
   :width: 6.17708in
   :height: 3.20436in
.. |image7| image:: image7.png
   :width: 6.68123in
   :height: 3.61035in
.. |image8| image:: image8.png
   :width: 6.50000in
   :height: 5.61875in
