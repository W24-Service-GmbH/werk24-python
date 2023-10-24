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
from pydantic import BaseModel
from pint import Quantity
from pydantic_core import PydanticUndefined

class W24TypedModel(BaseModel):
    """
    Parent to any type-based sub-model.

    Attributes:
    ----------
    _subtypes_ (Dict[Tuple[str,...], BaseModel]): Map
        that associates the discriminators to a specific
        model that shall be called.
    """

    __subtypes__ = {}

    class Config:
        arbitrary_types_allowed = True

        """Have the custom encoders here.
        This is not the nicest solution, but more
        a workaround until Pydantic 2.0 is ready.
        See: https://github.com/pydantic/pydantic/issues/2277
        """
        json_encoders = {
            # NOTE: specify a custom validator to make
            # sure that the serialization is done correctly.
            # See validator for details.
            Quantity: lambda v: str(v)
        }

    @classmethod
    def __pydantic_init_subclass__(
        cls,
    ):
        """Called when a subclass is specified.

        Registers the class locally.
        """
        key_ = tuple(
            [cls._first_child()]
            + [
                None
                if cls.model_fields[disc].default == PydanticUndefined
                else cls.model_fields[disc].default
                for disc in cls.Config.discriminators
            ]
        )
        cls.__subtypes__[key_] = cls

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
        """Convert the data to the correct subtype."""
        # get the key from the data.
        key_ = tuple([cls] + [data.get(disc) for disc in cls.Config.discriminators])

        # check whether the subtype actually exists.
        # Be careful with updates here.
        sub = cls.__subtypes__.get(key_)
        if sub is None:
            raise TypeError(f"Unsupported sub-type: {key_}")

        # parse the object using the subclass
        return sub(**data)

    @classmethod
    def parse_obj(cls, obj):
        """Parse the object with the correct deserializer."""
        return cls._convert_to_real_type_(obj)
