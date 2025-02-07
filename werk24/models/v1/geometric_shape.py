from decimal import Decimal
from itertools import permutations
from typing import Tuple

from pydantic import BaseModel


class W24GeometricShapeCuboid(BaseModel):
    """Geometric Shape of a cuboid

    Attributes:
        width (Decimal): Width of the cuboid

        height (Decimal): Height of the cuboid

        depth (Decimal): Depth of the cuboid
    """

    width: Decimal
    height: Decimal
    depth: Decimal

    def to_tuple(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Get a `width`x`depth`x`height` tuple

        Returns:
            Tuple[Decimal,Decimal, Decimal]: Width, height, depth
                tuple of the cuboid
        """
        return (self.width, self.height, self.depth)

    def encloses(
        self,
        other: "W24GeometricShapeCuboid",
        allow_width_depth_rotation: bool = True,
    ) -> bool:
        """Does this cuboid enclose `other` cuboid?

        Check whether this cuboid encloses the `other` cuboid.
        The `allow_width_depth_rotation` parameter allows you
        to specify whether the edges of the two cuboids
        need to be parallel.

        Args:
            other (W24GeometricShapeCuboid): Other cuboid
            allow_width_depth_rotation (bool, optional): Allow
                to rotate the `other` cuboid around this
                cuboid's width/depth plane. Especially useful
                for additive manufacturing applications.
                Defaults to True.

        Raises:
            RuntimeError: Raised when receiving a object other
                than a cuboid

        Returns:
            bool: True if `self` encloses `other`.
        """

        # ensure that we are actually dealing with a
        # cuboid. NOTE: in the future we might want to
        # support cylinders as well
        if not isinstance(other, W24GeometricShapeCuboid):
            raise RuntimeError("Invalid datatype for `other`")

        # check whether the part fits into the machine
        # in a fully parallel way.
        if self._encloses__parallel(other):
            return True

        # if rotation on the width-depth plane is allowed,
        # check that as well
        if allow_width_depth_rotation and self._encloses__width_depth_rotation(other):
            return True

        return False

    def _encloses__parallel(self, other: "W24GeometricShapeCuboid") -> bool:
        """Check whether the other cuboid fits into this
        cuboid without rotating the other cuboid on any
        axis. The `other` cuboid can only be rotated by
        fully 90 degrees (i.e, we are allowed to swap
        the width and height)

        Args:
            other (W24GeometricShapeCuboidShape): Other cuboid
                that should be fit into the `self` cuboid

        Returns:
            bool: True if the `other` cuboid fits into the
                `self` cuboid while preserving the parallelism
                between the two cuboids
        """
        machine = sorted(self.to_tuple())
        part = sorted(other.to_tuple())
        return all(m >= p for m, p in zip(machine, part))

    def _encloses__width_depth_rotation(self, other: "W24GeometricShapeCuboid") -> bool:

        # without loss of generality: consider the machine width
        # to be the larger of the width/depth dimensions
        machine_width = float(max(self.width, self.depth))
        machine_depth = float(min(self.width, self.depth))
        diagonal_length = (machine_width**2 + machine_depth**2) ** 0.5
        if machine_depth == 0:
            return False
        aspect_ratio = machine_depth / machine_width

        # go through all possible rotations of the part
        # PERFORMANCE: this will generate at most 6 iterations
        for width, height, depth in set(permutations(other.to_tuple(), 3)):

            # check whether the width fits into the diagonal
            if width > diagonal_length:
                continue

            # check the height first (cheaper to check)
            if height > self.height:
                continue

            # check whether there is still enough space left
            # between the end of the depth-edge of the part
            # and the machine depth
            max_depth = (diagonal_length - float(width)) * aspect_ratio
            if depth > max_depth:
                continue

            # if all criteria are met, we can accept
            return True

        return False


class W24GeometricShapeCylinder(BaseModel):
    """Geometric Shape of a cylinder

    Attributes:
        diameter (Decimal): Diameter of the cylinder

        depths (Decimal): Depth of the cylinder
    """

    diameter: Decimal
    depth: Decimal
