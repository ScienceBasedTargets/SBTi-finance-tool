from abc import ABC, abstractmethod
from typing import Tuple


class DataProvider(ABC):
    """
    General data provider super class.
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_report(self, company) -> Tuple[float, float]:
        """
        Get the emissions and the temperature score given a company. Throws a CompanyNotFoundException if the company
        is not found.

        :param company: str: The identifier of the company to get the emissions for
        :return: float, float: The emissions and the temperature score
        """
        pass


class CompanyNotFoundException(Exception):
    """
    This exception occurs when a company is not found.
    """
    pass
