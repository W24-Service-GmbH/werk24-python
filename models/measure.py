from pydantic import BaseModel


class W24Measure(BaseModel):
    """ Tolerated measure with positve and negative tolerances.
    All measures are in Millimeter

    NOTE: Fit measures are translated into positive and
    negative tolerances.
    """
    value: float
    fit_size: str = None
    positive_tolerance: float = None
    negative_tolerance: float = None

    def __str__(self) -> str:
        """ Return the Measure in a human-readable format
        """

        # start with the value
        result = str(self.value)

        # add the fit size
        if self.fit_size is not None:
            result += " {}".format(self.fit_size)

        # add the positive and negative tolerances
        # start with the +- case in which the
        # positive and negative tolerances are of
        # equal size
        if self.positive_tolerance is not None \
            and self.negative_tolerance is not None \
                and - 1 * self.negative_tolerance == self.positive_tolerance:
            result += " +-{}".format(self.positive_tolerance)

        # add the positive tolerance
        elif self.positive_tolerance is not None:
            result += " +{}".format(self.positive_tolerance)

        # or the negative
        elif self.negative_tolerance is not None:
            result += " {}".format(self.negative_tolerance)

        # return
        return result
