"""Data Models describing part families.

Author: Jochen Mattes
"""

from typing import Any, Dict

from pydantic import UUID4, BaseModel


class W24PartFamilyCharacterization(BaseModel):
    """Instance of a part family described by the File.

    Part families can be defined by the Werk24 partner.
    This allows us the flexibility to consider the exact
    situation of the customer.

    Take two companies that both deal with screws, but use
    different characteristic values to describe the part
    family. With this flexibility, we can simply specify
    a postprocessor for each customer and are able to
    consider their very special situation.

    Attributes:
        part_family_id (UUID4): Unique Identifier of the part
            family. You need this ID to trigger the correct
            postprocessor. Note that this is account-specific,
            so a post-processors need to be activated for your
            account, but are available to all of your tenants.
            If you want to show them selectively to your
            users, you are responsible for checking that the
            postprocessor can only be used by authorized
            tenants / users.

        part_family_name (str): A more human way of referring
            to the part family. This identifier is chosen by
            Werk24 according to an internal naming convention.

        variant_id (UUID4): Unique identifier of the variant.
            Note that a single drawing can specify multiple
            part family instances.

        characteristic_values (Dict[str, Any]): Characteristic
            values that define the part family. When exported to
            CSV, the keys correspond the column names, and the
            values to the cell values.
    """

    part_family_id: UUID4
    part_family_name: str
    variant_id: UUID4
    characteristic_values: Dict[str, Any]
