Functional Overview
================================================================

Temperature Score
-----------------

Portfolio temperature scores are calculated through an aggregation of
all companies’ temperature scores within your portfolio. For each
company, the score is calculated based on the publicly announced
targets, which are mapped to regression models based on IPCC climate
scenarios. The company is then awarded a score for each period and scope
based on the ambition and coverage of the relevant targets. For more
information, refer to the methodology `here <https://sciencebasedtargets.org/wp-content/uploads/2020/10/Financial-Sector-Science-Based-Targets-Guidance-Pilot-Version.pdf>`__\ .

Time Frames
~~~~~~~~~~~

By default, the SBTi temperature scoring tool reports temperature scores
on the mid-term time frames (i.e. based on emissions reduction targets
aimed at 5-15 years into the future). However, it is also possible to
inspect short (less than 5 years) and long-term time frames (15 to 30
years).

Scopes
~~~~~~

SBTi temperature scoring tool reports on the scores for Scope 1+2 and
Scope 1+2+3, however it is also possible to inspect the Scope 3 score
individually.

Aggregation methods
~~~~~~~~~~~~~~~~~~~

The portfolio temperature score can be calculated using different
aggregation methods based on emission and financial data of the
individual companies. The available options are:

-  Weighted average temperature score (WATS)

-  Total emissions weighted temperature score (TETS)

-  Market Owned emissions weighted temperature score (MOTS)

-  Enterprise Owned emissions weighted temperature score (EOTS).

-  EV + Cash emissions weighted temperature score (ECOTS)

-  Total Assets emissions weighted temperature score (AOTS)

-  Revenue emissions weighted temperature score (ROTS)

It is also possible to calculate scores of the individual companies
without aggregating to a portfolio score.

Grouping data 
~~~~~~~~~~~~~

This functionality enables the user to analyze (for examples see Jupyter
notebook
`analysis_example <https://github.com/OFBDABV/SBTi/blob/master/examples/1_analysis_example.ipynb>`__\ **)**
the temperature score of the portfolio in depth by slicing and dicing
through the portfolio. By choosing to “group by” a certain field (for
example region or sector), the user receives output of temperature
scores per category in the chosen field (so per region or sector). It is
possible to group over region, country, sector, and industry level 1-4.
Furthermore, it is also possible to add your own fields to group the
score over (e.g. investments strategies, market cap buckets) via the
portfolio data.

Choose fields to show
~~~~~~~~~~~~~~~~~~~~~

By default, the SBTi temperature scoring tool reports Company name,
Company ID, Scope, Time frame and Temperature score for each individual
combination. However, using this option allows the user to add
additional columns to the output. It is possible to add all fields
imported via either the portfolio data or the company data (fundamental
and target).

What-If Analyses
~~~~~~~~~~~~~~~~

To analyze the effect of engagement on your portfolio temperature score
it is possible to run “what-if” analyses. In these scenarios, the
temperature score is recalculated with the presumption that based on
various engagements some or all companies decided to set different (more
ambitious) targets.

The possible scenarios are:

-  Scenario 1: In this scenario, all companies in the portfolio that did
   not yet set a valid target have been persuaded to set 2.0\ :sup:`o`
   Celsius (C) targets. This is simulated by changing all scores that
   used the default score to a score of 2.0\ :sup:`o` C.

-  Scenario 2: In this scenario, all companies that already set targets
   are persuaded to set “Well Below 2.0\:sup:`o` C (WB2C) targets. This
   is simulated by setting all scores of the companies that have valid
   targets to at most 1.75\ :sup:`o` C.

-  Scenario 3: In these scenarios, the top 10 contributors to the
   portfolio temperature score are persuaded to set 2.0\ :sup:`o` C
   targets.

   -  Scenario 3a: All top 10 contributors set 2.0\ :sup:`o` C targets.

   -  Scenario 3b: All top 10 contributors set WB2C, i.e. 1.75\ :sup:`o` C targets.

-  Scenario 4: In this scenario, the user can specify which companies it
   wants to engage with to influence to set 2.0\ :sup:`o` C or WB2C
   targets. The user selects companies to engage with in the portfolio
   input file by settings the *engagement_target* field to TRUE for
   these companies.

   -  Scenario 4a: All companies that are marked as engagement targets
      set 2.0\ :sup:`o` C targets

   -  Scenario 4b: All companies that are marked as engagement targets
      set WB2C targets.

Portfolio coverage
------------------

The portfolio coverage calculates the percentage of the portfolio that
is covered by companies with an approved SBTi target. This coverage is
calculated using one of the aggregation methods above.

Output options
--------------

The temperature score can be requested for all time frames and scope
combinations on the following levels.

-  Portfolio temperature score: the aggregated score over all companies
   in the portfolio

-  Company temperature score: the temperature score of an individual
   company

-  Grouped temperature score: using the “group by” option, the user can
   get the aggregated temperature score per category in a chosen field
   (for example per region or per sector).

For the portfolio temperature score and the temperature score grouped by
some category, the following additional information is reported for the
composition of the score

-  Contributions: the level to which each company contributes to the
   total score based on the chosen aggregation method. This value is
   split into company temperature score and relative contribution.

-  The percentage of the score that is based on reported targets vs. the
   percentage based on the default score

-  For the grouped temperature scores: the percentage each group
   contributes to the portfolio temperature score. For example: how much
   each region or sector contributes to the total score.

For the company temperature scores it is possible to request all
underlying data.

-  Portfolio data

-  Financial data

-  GHG emissions

-  Used target and all its parameters

-  Values used during calculation such as the Linear annual reduction
   (LAR), mapped regression scenario, and parameters for the formula to
   calculate the temperature score.

Finally, it is possible to anonymize all names and identifiers, e.g. for
submission to the SBTi Target Validation Team for approval.
