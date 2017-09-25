"""
Module that provides classes for tree creation and handling.

Trees are powerful structures to sort a huge amount of data and to speed up performing query requests on them
significantly.
"""

import numpy as np

__all__ = [
    "IntervalTree"
]


class IntervalTreeNode:
    """Helper class for IntervalTree.

    """
    def __init__(self, center_point, center, left, right):
        self.center_point = center_point
        self.center = np.asarray(center)
        self.left = left
        self.right = right


class IntervalTree:
    """Tree to implement fast 1-dimensional interval searches.

    Based on the description in Wikipedia (https://en.wikipedia.org/wiki/Interval_tree#Centered_interval_tree)
    and the GitHub repository by tylerkahn (https://github.com/tylerkahn/intervaltree-python).

    """
    def __init__(self, intervals):
        """Creates an IntervalTree object.

        Args:
            intervals: A numpy array containing the intervals (list of two numbers).
        """
        self.left = np.min(intervals)
        self.right = np.max(intervals)

        # We want to return the indices of the intervals instead of their actual bounds. But the original indices will
        # be lost due resorting. Hence, we add the original indices to the intervals themselves.
        indices = np.arange(intervals.shape[0]).reshape(intervals.shape[0], 1)
        indexed_intervals = np.hstack([intervals, indices])
        self.root = self._build_tree(np.sort(indexed_intervals, axis=0))

    def _build_tree(self, intervals):
        if not intervals.any():
            return None

        center_point = self._get_center(intervals)

        # Sort the intervals into bins
        center = intervals[(intervals[:, 0] <= center_point) & (intervals[:, 1] >= center_point)]
        left = intervals[intervals[:, 1] < center_point]
        right = intervals[intervals[:, 0] > center_point]

        return IntervalTreeNode(center_point, center, self._build_tree(left), self._build_tree(right))

    @staticmethod
    def _get_center(intervals):
        return intervals[int(intervals.shape[0]/2), 0]

    @staticmethod
    def overlaps(interval1, interval2):
        """Checks whether two interval overlap each other.

        Args:
            x1: The lower bound of the first interval.
            x2: The higher bound of the first interval.
            y1: The lower bound of the second interval.
            y2: The higher bound of the second interval.

        Returns:
            True if the interval overlap.
        """
        return interval1[0] <= interval2[0] <= interval1[1] or \
               interval1[0] <= interval2[1] <= interval1[1] or \
               (interval2[0] <= interval1[0] and interval2[1] >= interval1[1])

    @staticmethod
    def contains(interval, point):
        """Checks whether a point lies in a interval.

        Args:
            x1: The lower bound of the interval.
            x2: The higher bound of the interval.
            y: The point.

        Returns:
            True if point lies in the interval.
        """
        return interval[0] <= point <= interval[1]

    def query(self, intervals):
        """Find all overlaps between this tree and a list of intervals.

        Args:
            intervals: A list of intervals. Each interval is a tuple/list of two elements: its lower and higher
            boundary.

        Returns:
            List of lists which contain the overlapping intervals of this tree for each element in `intervals`.
        """
        return [self._query(interval, self.root, check_extreme=True) for interval in intervals]

    def _query(self, query_interval, node, check_extreme=False):
        # Check this special case: the bounds of the query interval lie outside of the bounds of this tree:
        if (check_extreme
                and IntervalTree.contains(query_interval, self.left)
                and IntervalTree.contains(query_interval, self.right)):
            return [] # TODO: Return all intervals

        # Let's start with the centered intervals
        intervals = [int(interval[2]) for interval in node.center if IntervalTree.overlaps(interval, query_interval)]

        #print("Query interval", query_interval)
        #print(node.center_point, node.center, intervals)
        # if node.left is not None:
        #     print("links:", node.left.center)
        # else:
        #     print("Links ist leer.")
        # if node.right is not None:
        #     print("rechts:", node.right.center)
        # else:
        #     print("Rechts ist leer.")

        if query_interval[0] <= node.center_point and node.left is not None:
            #print("Gehe nach links!")
            intervals.extend(self._query(query_interval, node.left))

        if query_interval[1] >= node.center_point and node.right is not None:
            #print("Gehe nach rechts!")
            intervals.extend(self._query(query_interval, node.right))

        return intervals

    def query_points(self, points):
        """Find all intervals of this tree which contain one of those points.

        Args:
            points: A list of points.

        Returns:
            List of lists which contain the enclosing intervals of this tree for each element in `points`.
        """
        return [self._query_point(point, self.root, check_extreme=True) for point in points]

    def _query_point(self, point, node, check_extreme=False):
        # Check this special case: the query point lies outside of the bounds of this tree:
        if check_extreme and not IntervalTree.contains((self.left, self.right), point):
            return []

        # Let's start with the centered intervals
        intervals = [int(interval[2]) for interval in node.center if IntervalTree.contains(interval, point)]

        if point < node.center_point and node.left is not None:
            intervals.extend(self._query_point(point, node))

        if point > node.center_point and node.right is not None:
            intervals.extend(self._query_point(point, node))

        return intervals
