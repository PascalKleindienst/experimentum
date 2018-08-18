# -*- coding: utf-8 -*-
"""The Performance module lets you easily measure the performance.

It measures *execution time and memory consumption* of your python script
and lets you add messages to each measuring point for a more detailed overview.

Example:

.. code-block:: python

    performance = Performance()
    with performance.point('Task A') as point:
        # Do some heavy work
        point.message('Database query insert xy')

        with performance.point('Subtask A1') as subpoint:
            # Do some heavy work

        with performance.point('Subtask A2') as subpoint:
            subpoint.message('Database query insert xy')

    performance.results()  # print results table
"""
from __future__ import print_function
from contextlib import contextmanager
from timeit import time
from termcolor import colored
from math import floor, log
import psutil
import os
import tabulate
tabulate.PRESERVE_WHITESPACE = True


def memory_usage():
    """Return the memory usage of the current process.

    Note:
        Thanks to Fabian Pedregosa for his overview of different ways to
        determine the memory usage in python.
        http://fa.bianp.net/blog/2013/different-ways-to-get-memory-consumption-or-lessons-learned-from-memory_profiler

    Returns:
        float: used bytes.
    """
    process = psutil.Process(os.getpid())

    # return process.get_memory_info()[0] / float(2 ** 20)
    # return process.memory_info()[0]
    return process.memory_full_info().uss


class Formatter(object):

    """Format performance values to a human-readable format."""

    def memory_to_human(self, bytes, unit='auto', decimals=2):
        """Transform used memory into a better suited unit.

        Args:
            bytes (float): Used Bytes.
            unit (str, optional): Defaults to 'auto'. Unit to transform seconds into.
            decimals (int, optional): Defaults to 2. To which decimal point is rounded to.

        Returns:
            string: used memory suffixed with unit identifer
        """
        if bytes <= 0:
            return '0.00 KB'

        # If decimals is less than 0
        decimals = 2 if decimals < 0 else decimals

        value = 0
        units = {
            'B': 0, 'KB': 1, 'MB': 2, 'GB': 3, 'TB': 4, 'PB': 5, 'EB': 6, 'ZB': 7, 'YB': 8
        }

        if bytes > 0:
            # Generate automatic prefix by bytes if wrong prefix given
            if unit not in units:
                power = floor(log(bytes) / log(1024))
                unit = [k for k, v in units.items() if v == power][0]

            # Calculate byte value by prefix
            value = (bytes / pow(1024, floor(units[unit])))

        return self._format_number(value, decimals, unit)

    def time_to_human(self, seconds, unit='auto', decimals=2):
        """Transform time into a better suited unit.

        Args:
            seconds (float): Time seconds.
            unit (str, optional): Defaults to 'auto'. Unit to transform seconds into.
            decimals (int, optional): Defaults to 2. To which decimal point is rounded to.

        Raises:
            TypeError: if an unknown unit is passed

        Returns:
            string: time suffixed with unit identifer
        """
        if unit == 'auto':
            if seconds >= 1:
                unit = 's'
            elif seconds >= 0.001:
                unit = 'ms'
            else:
                unit = 'µs'

        if unit == 'µs':
            return self._format_number(seconds * 1000000, decimals, unit)
        elif unit == 'ms':
            return self._format_number(seconds * 1000, decimals, unit)
        elif unit == 's':
            return self._format_number(seconds * 1, decimals, unit)
        else:
            raise TypeError('Performance format {} does not exist.'.format(unit))

    def print_table(self, points, tablefmt='psql'):
        """Print performance table in human-readable format.

        Args:
            points (list): Measuring Points.
            tablefmt (str, optional): Defaults to 'psql'. Table format for :mod:`tabulate`
        """
        data = []
        headers = [
            colored('Label', 'cyan', attrs=['bold']),
            colored('Time', 'cyan', attrs=['bold']),
            colored('Memory', 'cyan', attrs=['bold']),
            colored('Peak Memory', 'cyan', attrs=['bold'])
        ]

        for p in points:
            data.extend(self._task(p))

        print(tabulate.tabulate(data, headers, tablefmt=tablefmt))

    def _format_number(self, value, decimals, unit):
        """Round a number and add a unit.

        Args:
            value (float): Number to round.
            decimals (int): Numer of decimals places.
            unit (string): Unit to append

        Returns:
            string
        """
        _format = '{:.%sf} {}' % decimals
        return _format.format(value, unit)

    def _task(self, point):
        """Format all rows associated with a point.

        Args:
            point (dict): Measuring Point

        Returns:
            list: list of formatted rows
        """
        rows = [
            [
                colored(u'› {}'.format(point['label']), attrs=['bold']),
                colored(self.time_to_human(point['difference_time']), attrs=['bold']),
                colored(self.memory_to_human(point['difference_memory']), attrs=['bold']),
                colored(self.memory_to_human(point['peak_memory']), attrs=['bold']),
            ]
        ]

        for msg in point['messages']:
            rows.append(
                [
                    colored('  {}'.format(msg[1]), attrs=['dark']),
                    colored(self.time_to_human(msg[0]), attrs=['dark']),
                    '--',
                    '--'
                ]
            )

        for subpoint in point['subpoints']:
            subpoint = subpoint.to_dict()
            rows.extend(self._task(subpoint))

        return rows


class Point(object):

    """Measuring Point Data Structure.

    Keeps track of execution time and memory consumption. You can also append
    messages to a point to keep track of different events. Each message contains
    the time since the last message was logged and the message content itself.

    Attributes:
        label (string): Label of the point.
        start_time (float): Startpoint Timestamp.
        stop_time (float): Endpoint Timestamp.
        start_memory (int): Memory consumption on start.
        stop_memory (int): Memory consumption on end.
        messages (list): List of optional messages.
        subpoints (list): List of optional subpoints.
    """

    def __init__(self, label):
        """Set the current time and memory consumption and default values for other attributes.

        Args:
            label (string): Label of the point.
        """
        self.label = label
        self.start_time = time.time()
        self.stop_time = 0
        self.start_memory = memory_usage()
        self.stop_memory = 0
        self.messages = []
        self.subpoints = []

        self._last_msg = self.start_time

    def message(self, msg):
        """Set a message associated with the point.

        Args:
            msg (string): Enter message
        """
        msg_time = time.time()
        self.messages.append([msg_time - self._last_msg, msg])
        self._last_msg = msg_time

    def to_dict(self):
        """Return all measured attributes and messages as a dictionary.

        Returns:
            dict: measured attributes and messages.
        """
        return {
            'label': self.label,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'difference_time': self.stop_time - self.start_time,
            'start_memory': self.start_memory,
            'stop_memory': self.stop_memory,
            'difference_memory': self.stop_memory - self.start_memory,
            'peak_memory': max(self.stop_memory, self.start_memory),
            'messages': self.messages,
            'subpoints': self.subpoints
        }


class Performance(object):

    """Easily measure the performance of your python scripts.

    Attributes:
        points (list): List of measuring points
        formatter (Formatter): Formatter to output human readable results
    """

    def __init__(self):
        """Set measuring points list and default formatter."""
        self.points = []
        self.set_formatter(Formatter())

    def set_formatter(self, formatter):
        """Set a formatter for human readable output.

        Args:
            formatter (Formatter): Human-readable output formatter
        """
        self.formatter = formatter

    @contextmanager
    def point(self, label='Point'):
        """Set measuring point with or without a label.

        Keyword Arguments:
            label (str, optional): Defaults to 'Point'. Enter point label

        Example:
            >>> with performance.point('Task A') as point:
            >>>     # do something
            >>>     point.message('Some Message)

        Yields:
            Point: new measuring point
        """
        try:
            point = Point(label)

            if len(self.points) and self.points[-1].stop_time is 0:
                self.points[-1].subpoints.append(point)
            else:
                self.points.append(point)

            yield point
        except Exception as e:
            print('Exception:', e)

        point.stop_time = time.time()
        point.stop_memory = memory_usage()

    def export(self):
        """Export the measuring points as a dictionary.

        Returns:
            dict: Measuring points
        """
        return [p.to_dict() for p in self.points]

    def results(self):
        """Print the performance results in a human-readable format."""
        points = self.export()
        self.formatter.print_table(points)
