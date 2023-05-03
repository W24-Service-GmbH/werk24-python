"""Improvement of the Pydantic Deserializer.

This allows us to dynamically specify the
models without the need to update the deserializer.

Be sure to specify the discriminators in the Config.

Example:
-------

class MetaData(W24TypedModel):
    class Config:
        discriminators = ('meta_data_type',)

class MetaDataLogo(MetaData):
    meta_data_type: Literal["LOGO"] = "LOGO"

class MetaDataDesignation(MetaData):
    meta_data_type: Literal["DESIGNATION"] = "DESIGNATION"
    designation: str


# serializiation
obj = MetaDataDesignation(blurb="a", designation="b").dict()

# deserialization
print(MetaData.parse_obj(obj))

"""
from typing import Dict, Tuple
from pydantic import BaseModel


class W24TypedModel(BaseModel):
    """Parent to any type-based sub-model.

    Attributes:
    ----------
    _subtypes_ (Dict[Tuple[str,...], BaseModel]): Map
        that associates the discriminators to a specific
        model that shall be called.
    """
    _subtypes_: Dict[Tuple[str, ...], BaseModel] = {}

    def __init_subclass__(cls):
        """Called when a subclass is specified.

        Registers the class locally.
        """
        # get the key from the default values.
        key_ = tuple(
            [cls._first_child()] + [
                cls.__fields__[disc].default
                for disc in cls.Config.discriminators
            ])

        # ignore if any of the key values is None.
        # This happens for classes that are not
        # meant to be initiated
        if any(k is None for k in key_):
            return

        cls._subtypes_[key_] = cls

    @classmethod
    def _first_child(cls):
        parent = cls
        for _ in range(100):
            child = parent
            parent = parent.__bases__[0]
            if parent.__name__ == "W24TypedModel":
                return child

        raise RecursionError()

    @classmethod
    def _convert_to_real_type_(cls, data):
        """Convert the data to the correct subtype.
        """
        # get the key from the data.
        key_ = tuple(
            [cls] + [
                data.get(disc)
                for disc in cls.Config.discriminators
            ])

        # check whether the subtype actually exists.
        # Be careful with updates here.
        sub = cls._subtypes_.get(key_)
        if sub is None:
            raise TypeError(f"Unsupport sub-type: {key_}")

        # parse the object using the subclass
        return sub(**data)

    @ classmethod
    def parse_obj(cls, obj):
        """Parse the object with the correct deserializer.
        """
        return cls._convert_to_real_type_(obj)
