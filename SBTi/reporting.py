from typing import List, Tuple

from .data.data_provider import DataProvider, CompanyNotFoundException


class Reporting:
    """
    This class provides a report on a portfolio.
    """

    def __init__(self, fallback_emissions: float = 3.2, fallback_score: float = -1.0):
        """
        Initialize the class.
        :param fallback_emissions: The emission if a company is not found
        :param fallback_score: The temp score if a company is not found
        """
        self.fallback_score = fallback_score
        self.fallback_emissions = fallback_emissions

    def get_report(self, data_provider: DataProvider, portfolio: List[dict]) -> Tuple[List[dict], float, float, float]:
        """
        Get the report on a portfolio.
        :param data_provider: The data provider to retrieve the data from
        :param portfolio: The portfolio (a list of dicts containing the id and proportion).
        :return:
        """
        coverage = 0
        for i_company, company in enumerate(portfolio):
            try:
                portfolio[i_company]["emissions"], portfolio[i_company]["temp_score"] = \
                    data_provider.get_report(company["id"])
                coverage += 1
            except CompanyNotFoundException:
                portfolio[i_company]["temp_score"] = self.fallback_score
                portfolio[i_company]["emissions"] = self.fallback_emissions

        total = sum([company["proportion"] for company in portfolio])
        if total > 0:
            weighted_emissions = sum([company["emissions"] * company["proportion"] for company in portfolio]) / total
            weighted_temp_score = sum([company["temp_score"] * company["proportion"] for company in portfolio]) / total
        else:
            weighted_emissions = 0.0
            weighted_temp_score = 0.0
        return portfolio, coverage / len(portfolio), weighted_emissions, weighted_temp_score
