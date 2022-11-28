import datetime
import itertools

import pandas as pd
from typing import Type, List, Tuple, Optional
from SBTi.configs import PortfolioAggregationConfig
import logging

from SBTi.interfaces import (
    IDataProviderTarget,
    IDataProviderCompany,
    EScope,
    ETimeFrames,
)


class TargetProtocol:
    """
    This class validates the targets, to make sure that only active, useful targets are considered. It then combines the targets with company-related data into a dataframe where there's one row for each of the nine possible target types (short, mid, long * S1+S2, S3, S1+S2+S3). This class follows the procedures outlined by the target protocol that is a part of the "Temperature Rating Methodology" (2020), which has been created by CDP Worldwide and WWF International.

    :param config: A Portfolio aggregation config
    """

    def __init__(
        self, config: Type[PortfolioAggregationConfig] = PortfolioAggregationConfig
    ):
        self.c = config
        self.logger = logging.getLogger(__name__)
        self.s2_targets: List[IDataProviderTarget] = []
        self.target_data: pd.DataFrame = pd.DataFrame()
        self.company_data: pd.DataFrame = pd.DataFrame()
        self.data: pd.DataFrame = pd.DataFrame()

    def process(
        self, targets: List[IDataProviderTarget], companies: List[IDataProviderCompany]
    ) -> pd.DataFrame:
        """
        Process the targets and companies, validate all targets and return a data frame that combines all targets and company data into a 9-box grid.

        :param targets: A list of targets
        :param companies: A list of companies
        :return: A data frame that combines the processed data
        """
        # Create multiindex on company, timeframe and scope for performance later on
        targets = self.prepare_targets(targets)
        self.target_data = pd.DataFrame.from_records([c.dict() for c in targets])

        # Create an indexed DF for performance purposes
        self.target_data.index = (
            self.target_data.reset_index()
            .set_index(
                [self.c.COLS.COMPANY_ID, self.c.COLS.TIME_FRAME, self.c.COLS.SCOPE]
            )
            .index
        )
        self.target_data = self.target_data.sort_index()

        self.company_data = pd.DataFrame.from_records([c.dict() for c in companies])
        self.group_targets()
        return pd.merge(
            left=self.data, right=self.company_data, how="outer", on=["company_id"]
        )

    def validate(self, target: IDataProviderTarget) -> bool:
        """
        Validate a target, meaning it should:

        * Have a valid type
        * Not be finished
        * A valid end year

        :param target: The target to validate
        :return: True if it's a valid target, false if it isn't
        """
        # Only absolute targets or intensity targets with a valid intensity metric are allowed.
        target_type = "abs" in target.target_type.lower() or (
            "int" in target.target_type.lower()
            and target.intensity_metric is not None
            and target.intensity_metric.lower() != "other"
        )
        # The target should not have achieved it's reduction yet.
        target_process = (
            pd.isnull(target.achieved_reduction)
            or target.achieved_reduction is None
            or target.achieved_reduction < 1
        )

        # The end year should be greater than the start year.

        if target.start_year is None or pd.isnull(target.start_year):
            target.start_year = target.base_year

        target_end_year = target.end_year > target.start_year

        # The end year should be greater than or equal to the current year
        # Added in update Oct 22
        target_current = target.end_year >= datetime.datetime.now().year

        # Delete all S1 or S2 targets we can't combine
        s1 = target.scope != EScope.S1 or (
            not pd.isnull(target.coverage_s1)
            and not pd.isnull(target.base_year_ghg_s1)
            and not pd.isnull(target.base_year_ghg_s2)
        )
        s2 = target.scope != EScope.S2 or (
            not pd.isnull(target.coverage_s2)
            and not pd.isnull(target.base_year_ghg_s1)
            and not pd.isnull(target.base_year_ghg_s2)
        )
        return target_type and target_process and target_end_year and target_current and s1 and s2

    def _split_s1s2s3(
        self, target: IDataProviderTarget
    ) -> Tuple[IDataProviderTarget, Optional[IDataProviderTarget]]:
        """
        If there is a s1s2s3 scope, split it into two targets with s1s2 and s3

        :param target: The input target
        :return The split targets or the original target and None
        """
        if target.scope == EScope.S1S2S3:
            s1s2, s3 = target.copy(), None
            if (
                not pd.isnull(target.base_year_ghg_s1)
                and not pd.isnull(target.base_year_ghg_s2)
            ) or target.coverage_s1 == target.coverage_s2:
                s1s2.scope = EScope.S1S2
                if (
                    not pd.isnull(target.base_year_ghg_s1)
                    and not pd.isnull(target.base_year_ghg_s2)
                    and target.base_year_ghg_s1 + target.base_year_ghg_s2 != 0
                ):
                    coverage_percentage = (
                        s1s2.coverage_s1 * s1s2.base_year_ghg_s1
                        + s1s2.coverage_s2 * s1s2.base_year_ghg_s2
                    ) / (s1s2.base_year_ghg_s1 + s1s2.base_year_ghg_s2)
                    s1s2.coverage_s1 = coverage_percentage
                    s1s2.coverage_s2 = coverage_percentage

            if not pd.isnull(target.coverage_s3):
                s3 = target.copy()
                s3.scope = EScope.S3
            return s1s2, s3
        else:
            return target, None

    def _combine_s1_s2(self, target: IDataProviderTarget):
        """
        Check if there is an S2 target that matches this target exactly (if this is a S1 target) and combine them into one target.

        :param target: The input target
        :return: The combined target (or the original if no combining was required)
        """
        if target.scope == EScope.S1 and not pd.isnull(target.base_year_ghg_s1):
            matches = [
                t
                for t in self.s2_targets
                if t.company_id == target.company_id
                and t.base_year == target.base_year
                and t.start_year == target.start_year
                and t.end_year == target.end_year
                and t.target_type == target.target_type
                and t.intensity_metric == target.intensity_metric
            ]
            if len(matches) > 0:
                matches.sort(key=lambda t: t.coverage_s2, reverse=True)
                s2 = matches[0]
                combined_coverage = (
                    target.coverage_s1 * target.base_year_ghg_s1
                    + s2.coverage_s2 * s2.base_year_ghg_s2
                ) / (target.base_year_ghg_s1 + s2.base_year_ghg_s2)
                target.reduction_ambition = (
                    (
                        target.reduction_ambition
                        * target.coverage_s1
                        * target.base_year_ghg_s1
                        + s2.reduction_ambition * s2.coverage_s2 * s2.base_year_ghg_s2
                    )
                ) / (
                    target.coverage_s1 * target.base_year_ghg_s1
                    + s2.coverage_s2 * s2.base_year_ghg_s2
                )

                target.coverage_s1 = combined_coverage
                target.coverage_s2 = combined_coverage
                # Enforce that we use the combined target - changed 2022-09-01/BBG input
                # Note removed ".value" on 2022-11-23
                target.scope = EScope.S1S2
                # We don't need to delete the S2 target as it'll be definition have a lower coverage than the combined
                # target, therefore it won't be picked for our 9-box grid
        return target

    def _convert_s1_s2(self, target: IDataProviderTarget):
        """
        Convert a S1 or S2 target into a S1+S2 target.

        :param target: The input target
        :return: The converted target (or the original if no conversion was required)
        """
        # In both cases the base_year_ghg s1 + s2 should not be zero
        if target.base_year_ghg_s1 + target.base_year_ghg_s2 != 0:
            if target.scope == EScope.S1:
                coverage = (
                    target.coverage_s1
                    * target.base_year_ghg_s1
                    / (target.base_year_ghg_s1 + target.base_year_ghg_s2)
                )
                target.coverage_s1 = coverage
                target.coverage_s2 = coverage
                target.scope = EScope.S1S2
            elif target.scope == EScope.S2:
                coverage = (
                    target.coverage_s2
                    * target.base_year_ghg_s2
                    / (target.base_year_ghg_s1 + target.base_year_ghg_s2)
                )
                target.coverage_s1 = coverage
                target.coverage_s2 = coverage
                target.scope = EScope.S1S2
        return target

    def _boundary_coverage(self, target: IDataProviderTarget) -> IDataProviderTarget:
        """
        Test on boundary coverage:

        Option 1: minimal coverage threshold
        For S1+S2 targets: coverage% must be at or above 95%, for S3 targets coverage must be above 67%

        Option 2: weighted coverage
        Thresholds are still 95% and 67%, target is always valid. Below threshold ambition is scaled.*
        New target ambition = input target ambition * coverage
        *either here or in tem score module

        Option 3: default coverage
        Target is always valid, % uncovered is given default score in temperature score module.

        :param target: The input target
        :return: The original target with a weighted reduction ambition, if so required
        """
        if target.scope == EScope.S1S2:
            if target.coverage_s1 < 0.95:
                target.reduction_ambition = (
                    target.reduction_ambition * target.coverage_s1
                )
        elif target.scope == EScope.S3:
            if target.coverage_s3 < 0.67:
                target.reduction_ambition = (
                    target.reduction_ambition * target.coverage_s3
                )
        return target

    def _time_frame(self, target: IDataProviderTarget) -> IDataProviderTarget:
        """
        Time frame is forward looking: target year - current year. Less than 5y = short, between 5 and 15 is mid, 15 to 30 is long

        :param target: The input target
        :return: The original target with the time_frame field filled out (if so required)
        """
        now = datetime.datetime.now()
        time_frame = target.end_year - now.year
        if time_frame <= 4:
            target.time_frame = ETimeFrames.SHORT
        elif time_frame <= 15:
            target.time_frame = ETimeFrames.MID
        elif time_frame <= 30:
            target.time_frame = ETimeFrames.LONG

        return target

    def _prepare_target(self, target: IDataProviderTarget):
        """
        Prepare a target for usage later on in the process.

        :param target:
        :return:
        """
        target = self._combine_s1_s2(target)
        target = self._convert_s1_s2(target)
        target = self._boundary_coverage(target)
        target = self._time_frame(target)
        return target

    def prepare_targets(self, targets: List[IDataProviderTarget]):
        targets = list(filter(self.validate, targets))
        self.s2_targets = list(
            filter(
                lambda target: target.scope == EScope.S2
                and not pd.isnull(target.base_year_ghg_s2)
                and not pd.isnull(target.coverage_s2),
                targets,
            )
        )

        targets = list(
            filter(
                None, itertools.chain.from_iterable(map(self._split_s1s2s3, targets))
            )
        )
        # BBG proposal - changed 2022-09-01
        # targets = [self._prepare_target(target) for target in targets]
        # Apply the four APIs on all targets one API at a time
        # instead of all running each target through all four APIs.
        # This means that we don't have to call _prepare_target.
        targets = [self._combine_s1_s2(target) for target in targets]
        targets = [self._convert_s1_s2(target) for target in targets]
        targets = [self._boundary_coverage(target) for target in targets]
        targets = [self._time_frame(target) for target in targets]

        return targets

    def _find_target(self, row: pd.Series, target_columns: List[str]) -> pd.Series:
        """
        Find the target that corresponds to a given row. If there are multiple targets available, filter them.

        :param row: The row from the data set that should be looked for
        :param target_columns: The columns that need to be returned
        :return: returns records from the input data, which contains company and target information, that meet specific criteria. For example, record of greatest emissions_in_scope
        """

        # Find all targets that correspond to the given row
        try:
            target_data = self.target_data.loc[
                (
                    row[self.c.COLS.COMPANY_ID],
                    row[self.c.COLS.TIME_FRAME],
                    row[self.c.COLS.SCOPE],
                )
            ].copy()
            if isinstance(target_data, pd.Series):
                # One match with Target data
                return target_data[target_columns]
            else:
                if target_data.scope[0] == EScope.S3:
                    coverage_column = self.c.COLS.COVERAGE_S3
                else:
                    coverage_column = self.c.COLS.COVERAGE_S1
                # In case more than one target is available; we prefer targets with higher coverage, later end year, and target type 'absolute'
                return target_data.sort_values(
                    by=[
                        coverage_column,
                        self.c.COLS.END_YEAR,
                        self.c.COLS.TARGET_REFERENCE_NUMBER,
                    ],
                    axis=0,
                    ascending=[False, False, True],
                ).iloc[0][target_columns]
        except KeyError:
            # No target found
            return row

    def group_targets(self):
        """
        Group the targets and create the 9-box grid (short, mid, long * s1s2, s3, s1s2s3).
        Group valid targets by category & filter multiple targets#
        Input: a list of valid targets for each company:
        For each company:

        Group all valid targets based on scope (S1+S2 / S3 / S1+S2+S3) and time frame (short / mid / long-term)
        into 6 categories.

        For each category: if more than 1 target is available, filter based on the following criteria
        -- Highest boundary coverage
        -- Latest base year
        -- Target type: Absolute over intensity
        -- If all else is equal: average the ambition of targets
        """

        grid_columns = [
            self.c.COLS.COMPANY_ID,
            self.c.COLS.TIME_FRAME,
            self.c.COLS.SCOPE,
        ]
        companies = self.company_data[self.c.COLS.COMPANY_ID].unique()
        scopes = [EScope.S1S2, EScope.S3, EScope.S1S2S3]
        empty_columns = [
            column for column in self.target_data.columns if column not in grid_columns
        ]
        extended_data = pd.DataFrame(
            list(
                itertools.product(
                    *[companies, ETimeFrames, scopes] + [[None]] * len(empty_columns)
                )
            ),
            columns=grid_columns + empty_columns,
        )
        target_columns = extended_data.columns
        self.data = extended_data.apply(
            lambda row: self._find_target(row, target_columns), axis=1
        )
