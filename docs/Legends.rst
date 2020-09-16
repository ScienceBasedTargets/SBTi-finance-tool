********************
Legend
********************

Portfolio data 
--------------
.. tabularcolumns:: |p{5cm}|p{5cm}|p{5cm}|p{5cm}|p{5cm}|
+-------------+-------------+-------------+-------------+-------------+
| **Data      | **Expected  | **Ex        | **Optional  | **comment** |
| field**     | value**     | planation** | /           |             |
|             |             |             | required**  |             |
+=============+=============+=============+=============+=============+
| company_name| Text        | Name of the | Required    | Used for    |
|             |             | company in  |             | output      |
|             |             | your        |             | purposes    |
|             |             | portfolio   |             | only        |
+-------------+-------------+-------------+-------------+-------------+
| company_id  | Text        | Identifier  | Required    | You can use |
|             |             | for the     |             | any unique  |
|             |             | company in  |             | company     |
|             |             | your        |             | identifier, |
|             |             | portfolio,  |             | but must    |
|             |             | used to map |             | use the     |
|             |             | target and  |             | same        |
|             |             | fundamental |             | identifier  |
|             |             | data to the |             | in all      |
|             |             | company     |             | three input |
|             |             |             |             | data        |
|             |             |             |             | files/tabs. |
+-------------+-------------+-------------+-------------+-------------+
| company_isin| Text        | Identifier  | Required,   |             |
|             |             | for the     | for         |             |
|             |             | company in  | portfolio   |             |
|             |             | your        | coverage    |             |
|             |             | portfolio,  | and         |             |
|             |             | used to get | temperature |             |
|             |             | the SBTi    | score.      |             |
|             |             | status of   |             |             |
|             |             | the company |             |             |
|             |             | (i.e.       |             |             |
|             |             | whether or  |             |             |
|             |             | not the     |             |             |
|             |             | company has |             |             |
|             |             | a target    |             |             |
|             |             | approved by |             |             |
|             |             | the SBTi)   |             |             |
+-------------+-------------+-------------+-------------+-------------+
| investment  | Monetary    | The         | Required    | Make sure   |
| _value      | value       | monetary    |             | all values  |
|             |             | value       |             | are in the  |
|             |             | invested in |             | same        |
|             |             | the         |             | currency.   |
|             |             | company.    |             |             |
|             |             | Used for    |             |             |
|             |             | aggregation |             |             |
+-------------+-------------+-------------+-------------+-------------+
| engagement  | TRUE, FALSE | Used for    | Optional    |             |
| _target     | or empty    | engagement  |             |             |
|             |             | analysis.   |             |             |
|             |             | When set to |             |             |
|             |             | TRUE for a  |             |             |
|             |             | company it  |             |             |
|             |             | is possible |             |             |
|             |             | to analyze  |             |             |
|             |             | what it     |             |             |
|             |             | would do    |             |             |
|             |             | for your    |             |             |
|             |             | portfolio   |             |             |
|             |             | temperature |             |             |
|             |             | score if    |             |             |
|             |             | this        |             |             |
|             |             | company     |             |             |
|             |             | would set a |             |             |
|             |             | well below  |             |             |
|             |             | 2 degree    |             |             |
|             |             | Celsius (C) |             |             |
|             |             | or a 2C     |             |             |
|             |             | target.     |             |             |
+-------------+-------------+-------------+-------------+-------------+
| Additional  | Text        | It is       | Optional    |             |
| _field      |             | possible to |             |             |
|             |             | add         |             |             |
|             |             | additional  |             |             |
|             |             | fields to   |             |             |
|             |             | your        |             |             |
|             |             | portfolio   |             |             |
|             |             | data. These |             |             |
|             |             | fields can  |             |             |
|             |             | be used to  |             |             |
|             |             | group       |             |             |
|             |             | companies   |             |             |
|             |             | by other    |             |             |
|             |             | categories  |             |             |
|             |             | than        |             |             |
|             |             | sectors,    |             |             |
|             |             | industries, |             |             |
|             |             | regions and |             |             |
|             |             | countries,  |             |             |
|             |             | e.g. market |             |             |
|             |             | cap bucket, |             |             |
|             |             | investment  |             |             |
|             |             | strategy,   |             |             |
|             |             | asset       |             |             |
|             |             | class, etc. |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

Fundamental data
----------------
.. tabularcolumns:: |l|p{5cm}|p{5cm}|
+-------------+-------------+-------------+-------------+-------------+
| **Data      | **Expected  | **Ex        | **Optional  | **comment** |
| field**     | value**     | planation** | /           |             |
|             |             |             | required**  |             |
+=============+=============+=============+=============+=============+
| company_name| Text        | Name of the | Optional    |             |
|             |             | company in  |             |             |
|             |             | your        |             |             |
|             |             | portfolio   |             |             |
+-------------+-------------+-------------+-------------+-------------+
| company_id  | Text        | Identifier  | Required    | You can use |
|             |             | for the     |             | any unique  |
|             |             | company in  |             | company     |
|             |             | your        |             | identifier, |
|             |             | portfolio,  |             | but must    |
|             |             | used to map |             | use the     |
|             |             | target and  |             | same        |
|             |             | fundamental |             | identifier  |
|             |             | data to the |             | in all      |
|             |             | company     |             | three input |
|             |             |             |             | data        |
|             |             |             |             | files/tabs. |
+-------------+-------------+-------------+-------------+-------------+
| isic        | Text        | Sector      | Required    |             |
|             |             | cla         |             |             |
|             |             | ssification |             |             |
|             |             | code for    |             |             |
|             |             | the company |             |             |
|             |             | based on    |             |             |
|             |             | the         |             |             |
|             |             | In          |             |             |
|             |             | ternational |             |             |
|             |             | Standard    |             |             |
|             |             | Industrial  |             |             |
|             |             | Cla         |             |             |
|             |             | ssification |             |             |
|             |             | (htt        |             |             |
|             |             | ps://siccod |             |             |
|             |             | e.com/page/ |             |             |
|             |             | what-is-an- |             |             |
|             |             | isic-code). |             |             |
|             |             | Used to map |             |             |
|             |             | targets to  |             |             |
|             |             | the correct |             |             |
|             |             | regression  |             |             |
|             |             | model.      |             |             |
|             |             | Should      |             |             |
|             |             | include at  |             |             |
|             |             | least the   |             |             |
|             |             | first two   |             |             |
|             |             | levels:     |             |             |
|             |             | Section and |             |             |
|             |             | Division.   |             |             |
+-------------+-------------+-------------+-------------+-------------+
| country     | Text        | Country     | Optional    |             |
|             |             | where the   |             |             |
|             |             | company has |             |             |
|             |             | its         |             |             |
|             |             | h           |             |             |
|             |             | eadquarter. |             |             |
|             |             | Used for    |             |             |
|             |             | analysis    |             |             |
|             |             | purposes    |             |             |
|             |             | only.       |             |             |
+-------------+-------------+-------------+-------------+-------------+
| region      | Text        | Region      | Optional    |             |
|             |             | where the   |             |             |
|             |             | company has |             |             |
|             |             | its         |             |             |
|             |             | h           |             |             |
|             |             | eadquarter. |             |             |
|             |             | Used for    |             |             |
|             |             | analysis    |             |             |
|             |             | purposes    |             |             |
|             |             | only. Can   |             |             |
|             |             | be          |             |             |
|             |             | continental |             |             |
|             |             | or more     |             |             |
|             |             | granular.   |             |             |
+-------------+-------------+-------------+-------------+-------------+
| industry    | Text        | Level 1     | Optional    |             |
| _level_1-4  |             | through 4   |             |             |
|             |             | of the      |             |             |
|             |             | industry    |             |             |
|             |             | cla         |             |             |
|             |             | ssification |             |             |
|             |             | of the      |             |             |
|             |             | company.    |             |             |
|             |             | Used for    |             |             |
|             |             | analysis    |             |             |
|             |             | purposes    |             |             |
|             |             | only. Can   |             |             |
|             |             | be based on |             |             |
|             |             | any         |             |             |
|             |             | industry    |             |             |
|             |             | cla         |             |             |
|             |             | ssification |             |             |
|             |             | system.     |             |             |
+-------------+-------------+-------------+-------------+-------------+
| sector      | Text        | Sector of   | Optional    |             |
|             |             | the         |             |             |
|             |             | company.    |             |             |
|             |             | Used for    |             |             |
|             |             | analysis    |             |             |
|             |             | purposes    |             |             |
|             |             | only. Can   |             |             |
|             |             | be based on |             |             |
|             |             | any         |             |             |
|             |             | cla         |             |             |
|             |             | ssification |             |             |
|             |             | system.     |             |             |
+-------------+-------------+-------------+-------------+-------------+
| ghg_s1s2    | tCO2e       | Total GHG   | Required    |             |
|             |             | emissions   |             |             |
|             |             | for scope 1 |             |             |
|             |             | + 2 for the |             |             |
|             |             | company.    |             |             |
|             |             | Used to     |             |             |
|             |             | combine     |             |             |
|             |             | temperature |             |             |
|             |             | scores for  |             |             |
|             |             | scope 1 + 2 |             |             |
|             |             | and scope 3 |             |             |
|             |             | to          |             |             |
|             |             | temperature |             |             |
|             |             | score for   |             |             |
|             |             | scope 1 + 2 |             |             |
|             |             | + 3. Also   |             |             |
|             |             | used in     |             |             |
|             |             | combination |             |             |
|             |             | with ghg_s3 |             |             |
|             |             | in most     |             |             |
|             |             | aggregation |             |             |
|             |             | methods     |             |             |
|             |             | (except     |             |             |
|             |             | WATS)       |             |             |
+-------------+-------------+-------------+-------------+-------------+
| ghg_s3      | tCO2e       | Total GHG   | Required    |             |
|             |             | emissions   |             |             |
|             |             | for scope 3 |             |             |
|             |             | for the     |             |             |
|             |             | company.    |             |             |
|             |             | Used to     |             |             |
|             |             | combine     |             |             |
|             |             | temperature |             |             |
|             |             | scores for  |             |             |
|             |             | scope 1 + 2 |             |             |
|             |             | and scope 3 |             |             |
|             |             | to          |             |             |
|             |             | temperature |             |             |
|             |             | score for   |             |             |
|             |             | scope 1 + 2 |             |             |
|             |             | + 3. Also   |             |             |
|             |             | used in     |             |             |
|             |             | combination |             |             |
|             |             | with        |             |             |
|             |             | ghg_s1s2 in |             |             |
|             |             | most        |             |             |
|             |             | aggregation |             |             |
|             |             | methods     |             |             |
|             |             | (except     |             |             |
|             |             | WATS)       |             |             |
+-------------+-------------+-------------+-------------+-------------+
| company     | Monetary    | In single   | Required    | All values  |
| _revenue    | value       | dollars /   | only if     | must be in  |
|             |             | euros / ….  | using       | the same    |
|             |             | (can be any | aggregation | currency.   |
|             |             | currency    | method      |             |
|             |             | you         | ROTS.       |             |
|             |             | choose).    |             |             |
|             |             | Revenue of  |             |             |
|             |             | the company |             |             |
|             |             | in the most |             |             |
|             |             | recent      |             |             |
|             |             | year.       |             |             |
+-------------+-------------+-------------+-------------+-------------+
| company     | Monetary    | Market      | Required    | All values  |
| _market_cap | value       | cap         | only if     | must be in  |
|             |             | italization | using       | the same    |
|             |             | of the      | aggregation | currency.   |
|             |             | company in  | method      |             |
|             |             | single      | MOTS.       |             |
|             |             | dollars /   |             |             |
|             |             | euros / ….  |             |             |
+-------------+-------------+-------------+-------------+-------------+
| company     | Monetary    | Enterprise  | Required    | All values  |
| _enterprise | value       | value of    | only if     | must be in  |
| _value      |             | the company | using       | the same    |
|             |             | in single   | aggregation | currency.   |
|             |             | dollars /   | method EOTS |             |
|             |             | euros / ….  | or ECOTS.   |             |
+-------------+-------------+-------------+-------------+-------------+
| company     | Monetary    | Total       | Required    | All values  |
| _total      | value       | assets of   | only if     | must be in  |
| _assets     |             | the company | using       | the same    |
|             |             | in single   | aggregation | currency.   |
|             |             | dollars /   | method      |             |
|             |             | euros / ….  | AOTS.       |             |
+-------------+-------------+-------------+-------------+-------------+
| company     | Monetary    | Cash        | Required    | All values  |
| _cash       | value       | equivalents | only if     | must be in  |
| _equivalents|             | of the      | using       | the same    |
|             |             | company in  | aggregation | currency.   |
|             |             | single      | method      |             |
|             |             | dollars /   | ECOTS.      |             |
|             |             | euros / … . |             |             |
+-------------+-------------+-------------+-------------+-------------+

Target data
-----------
.. tabularcolumns:: |l|p{5cm}|p{5cm}|
+-------------+-------------+-------------+-------------+-------------+
| **Data      | **Expected  | **Ex        | **Optional  | **comment** |
| field**     | value**     | planation** | /           |             |
|             |             |             | required**  |             |
+=============+=============+=============+=============+=============+
| company_name| Text        | Name of the | Optional    |             |
|             |             | company in  |             |             |
|             |             | your        |             |             |
|             |             | portfolio   |             |             |
+-------------+-------------+-------------+-------------+-------------+
| company_id  | Text        | Identifier  | Required    | You can use |
|             |             | for the     |             | any unique  |
|             |             | company in  |             | company     |
|             |             | your        |             | identifier, |
|             |             | portfolio,  |             | but must    |
|             |             | used to map |             | use the     |
|             |             | target and  |             | same        |
|             |             | fundamental |             | identifier  |
|             |             | data to the |             | in all      |
|             |             | company     |             | three input |
|             |             |             |             | data        |
|             |             |             |             | files/tabs. |
+-------------+-------------+-------------+-------------+-------------+
| target_type | *Absolute*, | Type of     | Required    | If          |
|             | *Intensity* | target. Can |             | target_type |
|             | or *Other*  | be absolute |             | is left     |
|             |             | or          |             | empty the   |
|             |             | intensity   |             | target will |
|             |             | based GHG   |             | not be      |
|             |             | emission    |             | valid. If   |
|             |             | reduction   |             | no other    |
|             |             | target. All |             | target is   |
|             |             | targets     |             | available   |
|             |             | that are    |             | for that    |
|             |             | not GHG     |             | time-frame  |
|             |             | emissions   |             | and scope   |
|             |             | reduction   |             | combination |
|             |             | targets can |             | the company |
|             |             | be mapped   |             | will be     |
|             |             | to *Other.* |             | given a     |
|             |             | Used in the |             | default     |
|             |             | target      |             | score.      |
|             |             | validation  |             |             |
|             |             | protocol    |             |             |
|             |             | and to map  |             |             |
|             |             | the target  |             |             |
|             |             | to the      |             |             |
|             |             | relevant    |             |             |
|             |             | regression  |             |             |
|             |             | model in    |             |             |
|             |             | the         |             |             |
|             |             | temperature |             |             |
|             |             | score       |             |             |
|             |             | module.     |             |             |
+-------------+-------------+-------------+-------------+-------------+
| intensity   | *Revenue*,  | The metric  | Required    |             |
| _metric     | *Product*,  | the         | for targets |             |
|             | *Cement*,   | intensity   | with target |             |
|             | *Oil*,      | based GHG   | type        |             |
|             | *Steel*,    | emission    | “           |             |
|             | *Aluminum*, | reduction   | Intensity”. |             |
|             | *Power      | target is   | Can be left |             |
|             | Generation* | based on.   | empty for   |             |
|             | or *Other*  | All         | other       |             |
|             |             | intensity   | targets.    |             |
|             |             | metrics     |             |             |
|             |             | must be     |             |             |
|             |             | mapped to   |             |             |
|             |             | these 8     |             |             |
|             |             | categories. |             |             |
|             |             | Used in     |             |             |
|             |             | target      |             |             |
|             |             | validation  |             |             |
|             |             | protocol    |             |             |
|             |             | and to map  |             |             |
|             |             | the target  |             |             |
|             |             | to the      |             |             |
|             |             | relevant    |             |             |
|             |             | regression  |             |             |
|             |             | model in    |             |             |
|             |             | the         |             |             |
|             |             | temperature |             |             |
|             |             | score       |             |             |
|             |             | module.     |             |             |
+-------------+-------------+-------------+-------------+-------------+
| scope       | S1, S2,     | The         | Required    | Targets     |
|             | S1+S2,      | scope(s)    |             | without     |
|             | S1+S2+S3,   | covered by  |             | scope are   |
|             | S3          | the target. |             | not valid.  |
|             |             | All scope 3 |             | If no       |
|             |             | targets,    |             | target is   |
|             |             | whether     |             | available   |
|             |             | covering    |             | for a       |
|             |             | downstream, |             | time-frame  |
|             |             | upstream or |             | and scope   |
|             |             | both must   |             | combination |
|             |             | be mapped   |             | the company |
|             |             | to S3.      |             | will be     |
|             |             |             |             | given a     |
|             |             |             |             | default     |
|             |             |             |             | score.      |
+-------------+-------------+-------------+-------------+-------------+
| coverage_s1 | Number in   | The part of | Required    |             |
|             | decimals,   | emissions   | for a       |             |
|             | between 0   | covered in  | target that |             |
|             | and 1, e.g. | scope 1 for | covers      |             |
|             | 70% is      | the target. | scope 1     |             |
|             | denoted     | Used to     |             |             |
|             | 0.7.        | determine   |             |             |
|             |             | the         |             |             |
|             |             | temperature |             |             |
|             |             | score.      |             |             |
|             |             |             |             |             |
|             |             | For targets |             |             |
|             |             | covering    |             |             |
|             |             | scope 1 and |             |             |
|             |             | 2 specify   |             |             |
|             |             | the same    |             |             |
|             |             | coverage    |             |             |
|             |             | percentage  |             |             |
|             |             | in          |             |             |
|             |             | coverage_s1 |             |             |
|             |             | and         |             |             |
|             |             | coverage_s2 |             |             |
+-------------+-------------+-------------+-------------+-------------+
| coverage_s2 | Number in   | The part of | Required    |             |
|             | decimals,   | emissions   | for a       |             |
|             | between 0   | covered in  | target that |             |
|             | and 1, e.g. | scope 2 for | covers      |             |
|             | 70% is      | the target. | scope 2     |             |
|             | denoted     | Used to     |             |             |
|             | 0.7.        | determine   |             |             |
|             |             | the         |             |             |
|             |             | temperature |             |             |
|             |             | score.      |             |             |
|             |             |             |             |             |
|             |             | For targets |             |             |
|             |             | covering    |             |             |
|             |             | scope 1 and |             |             |
|             |             | 2 specify   |             |             |
|             |             | the same    |             |             |
|             |             | coverage    |             |             |
|             |             | percentage  |             |             |
|             |             | in          |             |             |
|             |             | coverage_s1 |             |             |
|             |             | and         |             |             |
|             |             | c           |             |             |
|             |             | overage_s2. |             |             |
+-------------+-------------+-------------+-------------+-------------+
| coverage_s3 | Number in   | The part of | Required    |             |
|             | decimals,   | emissions   | for a       |             |
|             | between 0   | covered in  | target that |             |
|             | and 1, e.g. | scope 3 for | covers      |             |
|             | 70% is      | the target. | scope 3     |             |
|             | denoted     | Used to     |             |             |
|             | 0.7.        | determine   |             |             |
|             |             | the         |             |             |
|             |             | temperature |             |             |
|             |             | score.      |             |             |
|             |             |             |             |             |
|             |             | Note: this  |             |             |
|             |             | should be   |             |             |
|             |             | the         |             |             |
|             |             | coverage    |             |             |
|             |             | compare to  |             |             |
|             |             | the whole   |             |             |
|             |             | scope 3     |             |             |
|             |             | emissions,  |             |             |
|             |             | so not just |             |             |
|             |             | the part    |             |             |
|             |             | that is     |             |             |
|             |             | covered by  |             |             |
|             |             | the target. |             |             |
+-------------+-------------+-------------+-------------+-------------+
| reduction   | Number in   | The         | Required    |             |
| _ambition   | decimals,   | emission    |             |             |
|             | between 0   | reduction   |             |             |
|             | and 1, e.g. | that is set |             |             |
|             | 70% is      | as ambition |             |             |
|             | denoted     | in the      |             |             |
|             | 0.7.        | target.     |             |             |
|             |             | Used to     |             |             |
|             |             | determine   |             |             |
|             |             | the         |             |             |
|             |             | temperature |             |             |
|             |             | score.      |             |             |
+-------------+-------------+-------------+-------------+-------------+
| base_year   | Year        | Base year   | Required    |             |
|             |             | of the      |             |             |
|             |             | target.     |             |             |
|             |             | Used in the |             |             |
|             |             | target      |             |             |
|             |             | validation  |             |             |
|             |             | protocol    |             |             |
|             |             | and to      |             |             |
|             |             | determine   |             |             |
|             |             | the time    |             |             |
|             |             | frame of    |             |             |
|             |             | the target. |             |             |
+-------------+-------------+-------------+-------------+-------------+
| end_year    | Year        | End year of | Required    |             |
|             |             | the target. |             |             |
|             |             | Used in the |             |             |
|             |             | target      |             |             |
|             |             | validation  |             |             |
|             |             | protocol    |             |             |
|             |             | and to      |             |             |
|             |             | determine   |             |             |
|             |             | the time    |             |             |
|             |             | frame of    |             |             |
|             |             | the target. |             |             |
+-------------+-------------+-------------+-------------+-------------+
| start_year  | Year        | Year the    | Optional    |             |
|             |             | target was  |             |             |
|             |             | announced.  |             |             |
|             |             | Used in the |             |             |
|             |             | target      |             |             |
|             |             | validation  |             |             |
|             |             | protocol.   |             |             |
|             |             | If not      |             |             |
|             |             | specified,  |             |             |
|             |             | it will be  |             |             |
|             |             | assumed the |             |             |
|             |             | start year  |             |             |
|             |             | is equal to |             |             |
|             |             | the base    |             |             |
|             |             | year.       |             |             |
+-------------+-------------+-------------+-------------+-------------+
| base_year   | tCO2e       | Total       | Required    |             |
| _ghg_s1     |             | reported    | for targets |             |
|             |             | GHG         | that only   |             |
|             |             | emissions   | cover scope |             |
|             |             | for scope 1 | 1 or scope  |             |
|             |             | for the     | 2           |             |
|             |             | company at  |             |             |
|             |             | the base    |             |             |
|             |             | year of the |             |             |
|             |             | target.     |             |             |
|             |             | Used to     |             |             |
|             |             | convert     |             |             |
|             |             | targets     |             |             |
|             |             | covering    |             |             |
|             |             | only scope  |             |             |
|             |             | 1 or scope  |             |             |
|             |             | 2 to scope  |             |             |
|             |             | 1 + scope 2 |             |             |
|             |             | targets.    |             |             |
+-------------+-------------+-------------+-------------+-------------+
| base_year   | tCO2e       | Total       | Required    |             |
| _ghg_s2     |             | reported    | for targets |             |
|             |             | GHG         | that only   |             |
|             |             | emissions   | cover scope |             |
|             |             | for scope 2 | 1 or scope  |             |
|             |             | for the     | 2           |             |
|             |             | company at  |             |             |
|             |             | the base    |             |             |
|             |             | year of the |             |             |
|             |             | target.     |             |             |
|             |             | Used to     |             |             |
|             |             | convert     |             |             |
|             |             | targets     |             |             |
|             |             | covering    |             |             |
|             |             | only scope  |             |             |
|             |             | 1 or scope  |             |             |
|             |             | 2 to scope  |             |             |
|             |             | 1 + scope 2 |             |             |
|             |             | targets.    |             |             |
+-------------+-------------+-------------+-------------+-------------+
| base_year   | tCO2e       | Total       | Optional    |             |
| _ghg_s3     |             | reported    |             |             |
|             |             | GHG         |             |             |
|             |             | emissions   |             |             |
|             |             | for scope 3 |             |             |
|             |             | for the     |             |             |
|             |             | company at  |             |             |
|             |             | the base    |             |             |
|             |             | year of the |             |             |
|             |             | target.     |             |             |
+-------------+-------------+-------------+-------------+-------------+
| achieved    | Number      | Part of the | Optional.   |             |
| _reduction  | between 0   | reduction   | If not      |             |
|             | and 1       | ambition of | specified,  |             |
|             |             | the target  | assumed     |             |
|             |             | that is     | below 1     |             |
|             |             | already     |             |             |
|             |             | achieved by |             |             |
|             |             | the         |             |             |
|             |             | company.    |             |             |
|             |             | Used in the |             |             |
|             |             | target      |             |             |
|             |             | validation  |             |             |
|             |             | protocol.   |             |             |
|             |             | Targets     |             |             |
|             |             | with        |             |             |
|             |             | achieved    |             |             |
|             |             | reduction   |             |             |
|             |             | of 1 are    |             |             |
|             |             | i           |             |             |
|             |             | nvalidated. |             |             |
+-------------+-------------+-------------+-------------+-------------+

Output data
-----------
.. tabularcolumns:: |l|p{5cm}|p{5cm}|
+----------------+----------------+----------------+----------------+
| **Data field** | **Expected     | *              | **From**       |
|                | value**        | *Explanation** |                |
+================+================+================+================+
| achieved       | Number between | Part of the    | Target data    |
| _reduction     | 0 and 1        | reduction      |                |
|                |                | ambition of    |                |
|                |                | the target     |                |
|                |                | that is        |                |
|                |                | already        |                |
|                |                | achieved by    |                |
|                |                | the company.   |                |
|                |                | Used in the    |                |
|                |                | target         |                |
|                |                | validation     |                |
|                |                | protocol.      |                |
|                |                | Targets with   |                |
|                |                | achieved       |                |
|                |                | reduction of 1 |                |
|                |                | are            |                |
|                |                | invalidated.   |                |
+----------------+----------------+----------------+----------------+
| base_year      | Year           | Base year of   | Target data    |
|                |                | the target.    |                |
|                |                | Used in the    |                |
|                |                | target         |                |
|                |                | validation     |                |
|                |                | protocol and   |                |
|                |                | to determine   |                |
|                |                | the time frame |                |
|                |                | of the target. |                |
+----------------+----------------+----------------+----------------+
| base_year      | In tCO2e       | Total GHG      | Target data    |
| _ghg_s1        |                | emissions for  |                |
|                |                | scope 1 for    |                |
|                |                | the company at |                |
|                |                | the base year  |                |
|                |                | of the target. |                |
+----------------+----------------+----------------+----------------+
| base_year      | In tCO2e       | Total GHG      | Target data    |
| _ghg_s2        |                | emissions for  |                |
|                |                | scope 2 for    |                |
|                |                | the company at |                |
|                |                | the base year  |                |
|                |                | of the target. |                |
+----------------+----------------+----------------+----------------+
| base_year      | In tCO2e       | Total GHG      | Target data    |
| _ghg_s3        |                | emissions for  |                |
|                |                | scope 3 for    |                |
|                |                | the company at |                |
|                |                | the base year  |                |
|                |                | of the target. |                |
+----------------+----------------+----------------+----------------+
| company_id     | text           | Identifier for | Portfolio data |
|                |                | the company in |                |
|                |                | your           |                |
|                |                | portfolio,     |                |
|                |                | used to map    |                |
|                |                | target and     |                |
|                |                | fundamental    |                |
|                |                | data to the    |                |
|                |                | company        |                |
+----------------+----------------+----------------+----------------+
| company_isin   | text           | Identifier for | Portfolio data |
|                |                | the company in |                |
|                |                | your           |                |
|                |                | portfolio,     |                |
|                |                | used to get    |                |
|                |                | the SBTi       |                |
|                |                | status of the  |                |
|                |                | company (i.e.  |                |
|                |                | whether or not |                |
|                |                | the company    |                |
|                |                | has a target   |                |
|                |                | approved by    |                |
|                |                | the SBTi)      |                |
+----------------+----------------+----------------+----------------+
| company_name   | text           | Name of the    | Portfolio data |
|                |                | company in     |                |
|                |                | your portfolio |                |
+----------------+----------------+----------------+----------------+
| coverage_s1    | Number in      | The part of    | Target data    |
|                | decimals,      | emissions      |                |
|                | between 0 and  | covered in     |                |
|                | 1              | scope 1 for    |                |
|                |                | the target.    |                |
|                |                | Used to        |                |
|                |                | determine the  |                |
|                |                | temperature    |                |
|                |                | score.         |                |
+----------------+----------------+----------------+----------------+
| coverage_s2    | Number in      | The part of    | Target data    |
|                | decimals,      | emissions      |                |
|                | between 0 and  | covered in     |                |
|                | 1              | scope 2 for    |                |
|                |                | the target.    |                |
|                |                | Used to        |                |
|                |                | determine the  |                |
|                |                | temperature    |                |
|                |                | score.         |                |
+----------------+----------------+----------------+----------------+
| coverage_s3    | Number in      | The part of    | Target data    |
|                | decimals,      | emissions      |                |
|                | between 0 and  | covered in     |                |
|                | 1              | scope 3 for    |                |
|                |                | the target.    |                |
|                |                | Used to        |                |
|                |                | determine the  |                |
|                |                | temperature    |                |
|                |                | score.         |                |
+----------------+----------------+----------------+----------------+
| end_year       | Year           | End year of    | Target data    |
|                |                | the target.    |                |
|                |                | Used in the    |                |
|                |                | target         |                |
|                |                | validation     |                |
|                |                | protocol and   |                |
|                |                | to determine   |                |
|                |                | the time frame |                |
|                |                | of the target. |                |
+----------------+----------------+----------------+----------------+
| Intensity      | Revenue,       | The metric the | Target data    |
| _metric        | Product,       | intensity      |                |
|                | Cement, Oil,   | based GHG      |                |
|                | Steel,         | emission       |                |
|                | Aluminum,      | reduction      |                |
|                | Power          | target is      |                |
|                | Generation or  | based on. All  |                |
|                | Other          | intensity      |                |
|                |                | metrics must   |                |
|                |                | be mapped to   |                |
|                |                | the eight      |                |
|                |                | categories in  |                |
|                |                | the column on  |                |
|                |                | the left. Used |                |
|                |                | in target      |                |
|                |                | validation     |                |
|                |                | protocol and   |                |
|                |                | to map the     |                |
|                |                | target to the  |                |
|                |                | relevant       |                |
|                |                | regression     |                |
|                |                | model in the   |                |
|                |                | temperature    |                |
|                |                | score module.  |                |
+----------------+----------------+----------------+----------------+
| Reduction      | Number in      | The emission   | Target data    |
| _ambition      | decimals,      | reduction that |                |
|                | between 0 and  | is set as      |                |
|                | 1              | ambition in    |                |
|                |                | the target.    |                |
|                |                | Used to        |                |
|                |                | determine the  |                |
|                |                | temperature    |                |
|                |                | score.         |                |
+----------------+----------------+----------------+----------------+
| start_year     | Year           | Year the       | Target data    |
|                |                | target was     |                |
|                |                | announced.     |                |
|                |                | Used in the    |                |
|                |                | target         |                |
|                |                | validation     |                |
|                |                | protocol. If   |                |
|                |                | not specified, |                |
|                |                | it is assumed  |                |
|                |                | the start year |                |
|                |                | is equal to    |                |
|                |                | the base year. |                |
+----------------+----------------+----------------+----------------+
| Target_type    | Absolute,      | Type of        | Target data    |
|                | Intensity or   | target. Can be |                |
|                | Other          | absolute or    |                |
|                |                | intensity      |                |
|                |                | based GHG      |                |
|                |                | emission       |                |
|                |                | reduction      |                |
|                |                | target. All    |                |
|                |                | targets that   |                |
|                |                | are not GHG    |                |
|                |                | emissions      |                |
|                |                | reduction      |                |
|                |                | targets can be |                |
|                |                | mapped to      |                |
|                |                | *Other.* Used  |                |
|                |                | in the target  |                |
|                |                | validation     |                |
|                |                | protocol and   |                |
|                |                | to map the     |                |
|                |                | target to the  |                |
|                |                | relevant       |                |
|                |                | regression     |                |
|                |                | model in the   |                |
|                |                | temperature    |                |
|                |                | score module.  |                |
+----------------+----------------+----------------+----------------+
| Time_frame     | SHORT, MID or  | The targets    | Determined in  |
|                | LONG           | are sorted by  | tool           |
|                |                | time frame.    |                |
|                |                |                |                |
|                |                | SHORT: targets |                |
|                |                | shorter than 5 |                |
|                |                | years          |                |
|                |                |                |                |
|                |                | MID: targets   |                |
|                |                | between 5 and  |                |
|                |                | 15 years       |                |
|                |                |                |                |
|                |                | LONG: targets  |                |
|                |                | between 15 and |                |
|                |                | 30 years.      |                |
+----------------+----------------+----------------+----------------+
| ghg_s1s2       | tCO2e          | Total GHG      | Fundamental    |
|                |                | emissions for  | data           |
|                |                | scope 1 + 2    |                |
|                |                | for the        |                |
|                |                | company. Used  |                |
|                |                | to combine     |                |
|                |                | temperature    |                |
|                |                | scores for     |                |
|                |                | scope 1 + 2    |                |
|                |                | and scope 3 to |                |
|                |                | temperature    |                |
|                |                | score for      |                |
|                |                | scope 1 + 2 +  |                |
|                |                | 3. Also used   |                |
|                |                | in combination |                |
|                |                | with ghg_s3 in |                |
|                |                | most           |                |
|                |                | aggregation    |                |
|                |                | methods        |                |
|                |                | (except WATS)  |                |
+----------------+----------------+----------------+----------------+
| ghg_s3         | tCO2e          | Total GHG      | Fundamental    |
|                |                | emissions for  | data           |
|                |                | scope 3 for    |                |
|                |                | the company.   |                |
|                |                | Used to        |                |
|                |                | combine        |                |
|                |                | temperature    |                |
|                |                | scores for     |                |
|                |                | scope 1 + 2    |                |
|                |                | and scope 3 to |                |
|                |                | temperature    |                |
|                |                | score for      |                |
|                |                | scope 1 + 2 +  |                |
|                |                | 3. Also used   |                |
|                |                | in combination |                |
|                |                | with ghg_s3 in |                |
|                |                | all            |                |
|                |                | aggregation    |                |
|                |                | methods,       |                |
|                |                | except WATS.   |                |
+----------------+----------------+----------------+----------------+
| sbti_validated | FALSE or TRUE  | Returns true   | SBTi data or   |
|                |                | if the company | fundamental    |
|                |                | has a          | data           |
|                |                | SBTi-approved  |                |
|                |                | target.        |                |
+----------------+----------------+----------------+----------------+
| Investment     | Monetary value | The monetary   | Portfolio data |
| _value         |                | value invested |                |
|                |                | in the         |                |
|                |                | company.       |                |
+----------------+----------------+----------------+----------------+
| engagement     | TRUE, FALSE or | Used for       | Portfolio data |
| _target        | empty          | engagement     |                |
|                |                | analysis. When |                |
|                |                | set to TRUE    |                |
|                |                | for a company  |                |
|                |                | it is possible |                |
|                |                | to analyze     |                |
|                |                | what it would  |                |
|                |                | do for your    |                |
|                |                | portfolio      |                |
|                |                | temperature    |                |
|                |                | score if this  |                |
|                |                | company would  |                |
|                |                | set a (well    |                |
|                |                | below) 2       |                |
|                |                | degrees        |                |
|                |                | target.        |                |
+----------------+----------------+----------------+----------------+
| sr15           | text           | The regression | Output from    |
|                |                | model used.    | the tool       |
|                |                | This is        |                |
|                |                | determined     |                |
|                |                | based on the   |                |
|                |                | target type,   |                |
|                |                | ISIC,          |                |
|                |                | in             |                |
|                |                | tensity_metric |                |
|                |                | and scope. See |                |
|                |                | **[link to     |                |
|                |                | methodology    |                |
|                |                | doc, updated   |                |
|                |                | mapping        |                |
|                |                | section]** for |                |
|                |                | more detail    |                |
+----------------+----------------+----------------+----------------+
| Annual         | Number in      | The annual     | Output from    |
| _reduction     | decimals,      | reduction      | the tool       |
|                | between 0 and  | based on the   |                |
|                | 1              | redu           |                |
|                |                | ction_ambition |                |
|                |                | and the length |                |
|                |                | of the target. |                |
|                |                | Calculated     |                |
|                |                | as\ :math:`\te |                |
|                |                | xt{annual\ red |                |
|                |                | uction} = \fra |                |
|                |                | c{\text{reduct |                |
|                |                | ion\ ambition} |                |
|                |                | }{(end\ year - |                |
|                |                |  base\ year)}` |                |
+----------------+----------------+----------------+----------------+
| slope          | Slope5,        | Used in        | Output from    |
|                | slope15,       | determining    | the tool       |
|                | slope30        | the regression |                |
|                |                | model to use   |                |
|                |                | to calculate   |                |
|                |                | the            |                |
|                |                | temperature    |                |
|                |                | score for a    |                |
|                |                | specific       |                |
|                |                | target based   |                |
|                |                | on its time    |                |
|                |                | frame.         |                |
|                |                |                |                |
|                |                | Short-term     |                |
|                |                | targets:       |                |
|                |                | slope5         |                |
|                |                |                |                |
|                |                | Mid-term       |                |
|                |                | targets:       |                |
|                |                | slope15        |                |
|                |                |                |                |
|                |                | Long-term      |                |
|                |                | targets:       |                |
|                |                | slope30        |                |
+----------------+----------------+----------------+----------------+
| samplesize     | Number         | The sample     | Regression     |
|                |                | size used in   | model          |
|                |                | the regression |                |
|                |                | model. For     |                |
|                |                | model 4 this   |                |
|                |                | is 128. Not    |                |
|                |                | used in        |                |
|                |                | calculations.  |                |
|                |                | See            |                |
|                |                | https://g      |                |
|                |                | ithub.com/CDPw |                |
|                |                | orldwide/TROPI |                |
|                |                | CS-regression/ |                |
|                |                | for more       |                |
|                |                | detail about   |                |
|                |                | the            |                |
|                |                | regressions.   |                |
+----------------+----------------+----------------+----------------+
| model          | Integer        | The regression | Regression     |
|                |                | model used.    | model          |
|                |                | This is model  |                |
|                |                | 4 by default.  |                |
|                |                | See            |                |
|                |                | https://g      |                |
|                |                | ithub.com/CDPw |                |
|                |                | orldwide/TROPI |                |
|                |                | CS-regression/ |                |
|                |                | for more       |                |
|                |                | detail about   |                |
|                |                | the            |                |
|                |                | regressions.   |                |
+----------------+----------------+----------------+----------------+
| variable       | text           | The regression | Regression     |
|                |                | scenario used  | model          |
|                |                | to determine   |                |
|                |                | the            |                |
|                |                | temperature    |                |
|                |                | score of a     |                |
|                |                | target, for    |                |
|                |                | example        |                |
|                |                |                |                |
|                |                | E              |                |
|                |                | missions|Kyoto |                |
|                |                | Gases          |                |
+----------------+----------------+----------------+----------------+
| param          | Number in      | The            | Regression     |
|                | decimals,      | temperature    | model          |
|                | between 0 and  | score (TS) is  |                |
|                | 1              | calculated     |                |
|                |                | using linear   |                |
|                |                | regressions.   |                |
|                |                | :m             |                |
|                |                | ath:`\ TS\  =  |                |
|                |                | intersect + pa |                |
|                |                | ram*(annual\ r |                |
|                |                | eduction*100)` |                |
+----------------+----------------+----------------+----------------+
| intercept      | Number in      | The            | Regression     |
|                | decimals,      | temperature    | model          |
|                | between 0 and  | score (TS) is  |                |
|                | 1              | calculated     |                |
|                |                | using linear   |                |
|                |                | regressions.   |                |
|                |                |                |                |
|                |                | ..             |                |
|                |                |  math:: TS\  = |                |
|                |                |  intersect + p |                |
|                |                | aram*(annual\  |                |
|                |                | reduction*100) |                |
+----------------+----------------+----------------+----------------+
| r2             | Number in      | r2 represents  | Regression     |
|                | decimals,      | the fit of the | model          |
|                | between 0 and  | regression     |                |
|                | 1              | model on the   |                |
|                |                | data used to   |                |
|                |                | create the     |                |
|                |                | regressions.   |                |
|                |                | Not used in    |                |
|                |                | calculations.  |                |
+----------------+----------------+----------------+----------------+
| temperature    | Number         | The            | Output from    |
| _score         |                | temperature    | tool           |
|                |                | score          |                |
|                |                | calculated for |                |
|                |                | the            |                |
|                |                | combination of |                |
|                |                | company, scope |                |
|                |                | and time frame |                |
+----------------+----------------+----------------+----------------+
| temperature    | Number in      | Represents the |                |
| _results       | decimals,      | part of the    |                |
|                | between 0 and  | score that is  |                |
|                | 1              | calculated     |                |
|                |                | using a valid  |                |
|                |                | target as      |                |
|                |                | defined by the |                |
|                |                | target         |                |
|                |                | validation     |                |
|                |                | protocol vs.   |                |
|                |                | the part using |                |
|                |                | the default    |                |
|                |                | score. For     |                |
|                |                | more detail,   |                |
|                |                | see **[link to |                |
|                |                | Chapter 2 of   |                |
|                |                | Methodology    |                |
|                |                | document]**    |                |
+----------------+----------------+----------------+----------------+
