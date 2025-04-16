import collections.abc
import itertools
import math

import numpy as np
from common import is_array_like, sd_pose
import cv2


class Point(collections.abc.Sequence):
    """A point, as described by xy or xyz coordinates."""

    def __init__(self, *coordinates):
        """Initialize a Point object.

        Args:
            coordinates: Argument list of two (xy) or three (xyz) coordinates.
                         Coordinates should be of type int, float or similar numeric.
                         These values are converted to float.

        Raises:
            ValueError: If less than 2 or more than 3 arguments are supplied.
        """
        if len(coordinates) == 2 or len(coordinates) == 3:
            self._coordinates = tuple(float(c) for c in coordinates)
        else:
            raise ValueError("Point coordinates must have a length of 2 or 3")

    def __add__(self, vector):
        """The addition of this point and a vector.

        :param vector: The vector to be added to the point.
        :type vector: Vector

        :rtype: Point

        """
        zipped = itertools.zip_longest(self, vector)  # missing values filled with None
        try:
            coordinates = [a + b for a, b in zipped]
        except TypeError:  # occurs if, say, a or b is None
            raise ValueError("Point and vector to add must be of the same length.")
        return Point(*coordinates)

    def __eq__(self, point):
        """Tests if this point and the supplied point have the same coordinates.

        A tolerance value is used so coordinates with very small difference
        are considered equal.

        :param point: The point to be tested.
        :type point: Point

        :raises ValueError: If points are not of the same length.

        :return: True if the point coordinates are the same, otherwise False.
        :rtype: bool

        """
        zipped = itertools.zip_longest(self, point)  # missing values filled with None
        try:
            result = [self._coordinates_equal(a, b) for a, b in zipped]
        except TypeError:  # occurs if, say, a or b is None
            raise ValueError("Points to compare must be of the same length.")
        return all(result)

    def __getitem__(self, index):
        return self._coordinates[index]

    def __len__(self):
        return len(self._coordinates)

    def __lt__(self, point):
        """Tests if the coordinates of this point are lower than the supplied point.

        A tolerance value is used so coordinates with very small difference
        are considered equal.

        :param point: The point to be tested.
        :type point: Point

        :raises ValueError: If points are not of the same length.

        :return: True if the x coordinate of this point is lower than the
            supplied point, otherwise False. If both x coordinates are equal, then
            True if the y coordinate of this point is lower than the
            supplied point, otherwise False. For 3D points -> if both x and y coordinates
            are equal, then
            True if the z coordinate of this point is lower than the
            supplied point, otherwise False.
        :rtype: bool

        """
        zipped = itertools.zip_longest(self, point)  # missing values filled with None
        try:
            for a, b in zipped:
                if self._coordinates_equal(a, b):
                    continue
                return a < b
        except TypeError:  # occurs if, say, a or b is None
            raise ValueError("Points to compare must be of the same length.")

    def __repr__(self):
        return "Point(%s)" % ",".join([str(c) for c in self])

    # def __sub__(self, point_or_vector):
    #     """Subtraction of supplied object from this point.
    #
    #     :param point_or_vector: Either a point or a vector.
    #     :type point_or_vector: Point or Vector
    #
    #     :return: If a point is supplied, then a vector is returned (i.e. v=P1-P0).
    #         If a vector is supplied, then a point is returned (i.e. P1=P0-v).
    #     :rtype: Point2D or Vector2D
    #
    #     """
    #     zipped = itertools.zip_longest(self, point_or_vector)  # missing values filled with None
    #     try:
    #         coordinates = [a - b for a, b in zipped]
    #     except TypeError:  # occurs if, say, a or b is None
    #         raise ValueError(r'Point and point/vector to subtract must be of the same length.')
    #     if isinstance(point_or_vector, Point):
    #         return Vector(*coordinates)
    #     else:
    #         return Point(*coordinates)

    def _coordinates_equal(self, a, b):
        """Return True if a and b are equal within the tolerance value."""
        return math.isclose(a, b, abs_tol=1e-7)

    def project_2D(self, coordinate_index):
        """Projection of a 3D point as a 2D point.

        :param coordinate_index: The index of the coordinate to ignore.
            Use coordinate_index=0 to ignore the x-coordinate, coordinate_index=1
            for the y-coordinate and coordinate_index=2 for the z-coordinate.
        :type coordinate_index: int

        :raises ValueError: If coordinate_index is not between 0 and 2.

        :return: A 2D point based on the projection of the 3D point.
        :rtype: Point2D

        """

        if coordinate_index == 0:
            return Point(self.y, self.z)
        elif coordinate_index == 1:
            return Point(self.z, self.x)
        elif coordinate_index == 2:
            return Point(self.x, self.y)
        else:
            raise ValueError("coordinate_index must be between 0 and 2")

    def project_3D(self, plane, coordinate_index):
        """Projection of the point on a 3D plane.

        :param plane: The plane for the projection
        :type plane: Plane
        :param coordinate_index: The index of the coordinate which was ignored
            to create the 2D projection. For example, coordinate_index=0
            means that the x-coordinate was ignored and this point
            was originally projected onto the yz plane.
        :type coordinate_index: int

        :raises ValueError: If coordinate_index is not between 0 and 2.

        :return: The 3D point as projected onto the plane.
        :rtype: Point

        """

        if coordinate_index == 0:
            point = plane.point_yz(self.x, self.y)
        elif coordinate_index == 1:
            point = plane.point_zx(self.x, self.y)
        elif coordinate_index == 2:
            point = plane.point_xy(self.x, self.y)
        else:
            raise ValueError("coordinate_index must be between 0 and 2")

        return point

    @property
    def x(self):
        """The x coordinate of the point.

        :rtype: int, float

        """
        return self[0]

    @property
    def y(self):
        """The y coordinate of the point.

        :rtype: int, float

        """
        return self[1]

    @property
    def z(self):
        """The z coordinate of the point.

        :raises IndexError: If point is a 2D point.

        :rtype: int, float

        """
        return self[2]


class Point2D(Point):
    """A two-dimensional point, situated on an x, y plane.

    :param x: The x coordinate of the point.
    :type x: float
    :param y: The y coordinate of the point.
    :type y: float

    """

    def __init__(self, x, y):
        super().__init__(x, y)
        self._x = x
        self._y = y

    def __add__(self, vector):
        """The addition of this point and a vector.

        :param vector: The vector to be added to the point.
        :type vector: Vector2D

        :rtype: Point2D

        """
        return Point2D(self.x + vector.x, self.y + vector.y)

    def __lt__(self, point):
        """Tests if the coordinates of this point are lower than the supplied point.

        :param point: The point to be tested.
        :type point: Point2D

        :return: True if the x coordinate of this point is lower than the
            supplied point, otherwise False. If both x coordinates are equal, then
            True if the y coordinate of this point is lower than the
            supplied point, otherwise False.
        :rtype: bool

        """
        if self.x < point.x:
            return True
        else:
            if self.x == point.x and self.y < point.y:
                return True
            else:
                return False

    def __repr__(self):
        """"""
        return "Point2D(%s)" % ",".join([str(round(c, 4)) for c in self.coordinates])

    @property
    def coordinates(self):
        """The coordinates of the point.

        :return: The x and y coordinates as a tuple (x,y)
        :rtype: tuple

        """
        return self.x, self.y

    @property
    def dimension(self):
        """The dimension of the point.

        :return: '2D'
        :rtype: str

        """
        return "2D"

    @property
    def x(self):
        """The x coordinate of the point.

        :rtype: float

        """
        return self._x

    @property
    def y(self):
        """The y coordinate of the point.

        :rtype: float

        """
        return self._y


class Point3D(Point):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    @property
    def homogenous(self):
        return np.array([self.x, self.y, self.z, 1.0])

    @property
    def coordinates(self):
        return self.x, self.y, self.z

    @property
    def dimension(self):
        """The dimension of the point.

        :return: '3D'
        :rtype: str

        """
        return "3D"

    def to_list(self):
        return [self.x, self.y, self.z]

    def transform_with(self, *args):
        """Transform the 3D point P in frame A from frame A to frame B, given the transformation matrix
        from B to A, i.e., B_T_P = B_T_A * A_T_P. For example, assume the point is in the camera frame,
        and we want to transform it to the world frame, then the given transform should be the
        transform from the world frame to the camera frame (the inverse of the extrinsic matrix).

        Args:
            *args: ndarray Transformation matrix from frame B to frame A (B_T_A).

        Returns:
            Transformed Point3D in frame B.
        """
        if (
                len(args) == 1
                and isinstance(args[0], np.ndarray)
                and args[0].shape == (4, 4)
        ):
            transform_matrix = args[0]
        elif len(args) == 1 and is_array_like(args[0]):
            transform_matrix = sd_pose(args[0], True)
        else:
            raise NotImplementedError()

        p = np.dot(transform_matrix, self.homogenous)
        return Point3D(p[0], p[1], p[2])


class ImagePoint(Point2D):
    def __init__(self, x, y, image_width=0, image_height=0):
        super().__init__(x, y)
        self._image_height = image_height
        self._image_width = image_width

        self._x = self._regulate(self._x, self._image_width)
        self._y = self._regulate(self._y, self._image_height)

    @staticmethod
    def _regulate(coordinate, max_value):
        """Regulate the coordinate to make sure it is within the range [0, max_value).

        Args:
            coordinate (float|int):
            max_value (float|int):

        Returns:
            (float|int): Regulated coordinate value.

        Raises:
            ValueError: if the given coordinate is smaller than 0 or larger than max_value.
        """
        if 0 < coordinate < 1:
            coordinate = 0
        elif 0 < max_value == coordinate:
            coordinate -= 1
        elif coordinate < 0:
            raise ValueError("Image point coordinate less than 0 is not allowed")
        elif 0 < max_value < coordinate:
            raise ValueError(
                "Image point coordinate larger than the max value {} is not allowed".format(
                    max_value
                )
            )
        return coordinate

    @property
    def x(self):
        """Return the image point's x coordinate on the ordinary image frame."""
        return self._regulate(int(self._x), self._image_width)

    @property
    def y(self):
        """Return the image point's y coordinate on the ordinary image frame."""
        return self._regulate(int(self._y), self._image_height)

    @property
    def u(self):
        """Return pixel frame x coordinate."""
        return self.x

    @property
    def v(self):
        """Return pixel frame y coordinate."""
        return self.y

    @property
    def x_c(self):
        """Return the image point's x coordinate on the centered image frame."""
        if self._image_height == 0:
            raise ValueError(
                "Image height was not set when initializing the ImagePoint"
            )
        return float(self._image_height) * 0.5 - self._y

    @property
    def y_c(self):
        """Return the image point's y coordinate on the centered image frame."""
        if self._image_width == 0:
            raise ValueError("Image width was not set when initializing the ImagePoint")
        return float(self._image_width) * 0.5 - self._x

    def to_list(self):
        """Convert the ImagePoint to a list of [x, y].

        Returns:
            list[int] [x, y]
        """
        return [self.x, self.y]

    def draw_on_image(self, image, color):
        cv2.drawMarker(
            image, (self.x, self.y), color, cv2.MARKER_CROSS, markerSize=20, thickness=2
        )
        return image

    def to_camera_frame_point_3d(self, *args):
        """Convert this 2D image point in pixel frame to a 3D point in the camera frame.

        Args:
            *args: If two args are given, we assume they are the camera_matrix and Z_c, respectively;
                   If 5 args are given, we assume they are f_x, f_y, c_x, c_y, and Z_c.

        Returns:
            Point3D (X_c, Y_c, Z_c)
        """
        if (
                len(args) == 2
                and isinstance(args[0], np.ndarray)
                and args[0].shape == (3, 3)
        ):
            camera_matrix = args[0]
            Z_c = args[1]
            f_x = camera_matrix[0, 0]
            f_y = camera_matrix[1, 1]
            c_x = camera_matrix[0, 2]
            c_y = camera_matrix[1, 2]
        elif len(args) == 5:
            f_x = args[0]
            f_y = args[1]
            c_x = args[2]
            c_y = args[3]
            Z_c = args[4]
        else:
            raise NotImplementedError(
                f"{len(args)} args whose types are {[type(a) for a in args]} is not supported"
            )
        X_c = Z_c * float(self.u - c_x) / f_x
        Y_c = Z_c * float(self.v - c_y) / f_y
        return Point3D(X_c, Y_c, Z_c)


class Object:
    """
    A class to represent an object in an image.
    """

    def __init__(self, bbox, mask, class_id):
        """

        Args:
            bbox (xyxy):
            mask (np.array):
            class_id (str):
        """

        self._bbox = bbox
        self._mask = mask
        self._class_id = class_id
        self.contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        self._grasp_point = self.get_grasp_point()
        self._mask_area = np.sum(mask)

    def get_grasp_point(self):
        self.largest_contour_points = np.squeeze(self.contours).astype(float)
        mean = np.empty(0)
        mean, eigenvectors, eigenvalues = cv2.PCACompute2(self.largest_contour_points, mean)
        return mean[0]

    @property
    def contour(self):
        return self.largest_contour_points
    @property
    def bbox(self):
        return self._bbox

    @property
    def mask(self):
        return self._mask

    @property
    def class_id(self):
        return self._class_id

    @property
    def grasp_point(self):
        return self._grasp_point

    @property
    def area(self):
        return self._mask_area
