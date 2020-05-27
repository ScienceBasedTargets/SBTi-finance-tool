from typing import Tuple

from .data_provider import DataProvider, CompanyNotFoundException


class ExampleProvider(DataProvider):
    """
    Example data provider.
    """

    def __init__(self):
        super().__init__()

    def get_report(self, company) -> Tuple[float, float]:
        """
        Get the emissions and the temperature score given a company. Throws a CompanyNotFoundException if the company
        is not found. For testing purposes "Ortec Finance Data Analytics B.V." won't be found.

        :param company: str: The identifier of the company to get the emissions for
        :return: float, float: The emissions and the temperature score
        """
        if company == "Ortec Finance Data Analytics B.V.":
            raise CompanyNotFoundException

        return 0.0, 0.0
