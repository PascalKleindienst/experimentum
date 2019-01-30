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
import collections
import math
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


def _to_df(point, level=0):
    """Transfrom point to dataframe dict layout.

    Args:
        point (dict): Point
        level (int, optional): Defaults to 0. Level

    Returns:
        dict
    """
    data = {
        'Label': [point['label']],
        'Time': [point['difference_time']],
        'Memory': [point['difference_memory']],
        'Peak Memory': [point['peak_memory']],
        'Level': [level],
        'Type': ['point'],
        'ID': [point['id']],
        'Key': ['{}_{}_{}'.format(point['id'], level, point['label'])]
    }

    for msg in point['messages']:
        data['Label'].append(msg[1])
        data['Time'].append(msg[0])
        data['Memory'].append(point['difference_memory'])
        data['Peak Memory'].append(point['peak_memory'])
        data['Level'].append(level)
        data['Type'].append('message')
        data['ID'].append(point['id'])
        data['Key'].append('{}_{}_{}'.format(point['id'], level, msg[1]))

    for subpoint in point['subpoints']:
        _point = subpoint.to_dict()
        result = _to_df(_point, level+1)
        data['Label'].extend(result['Label'])
        data['Time'].extend(result['Time'])
        data['Memory'].extend(result['Memory'])
        data['Peak Memory'].extend(result['Peak Memory'])
        data['Level'].extend(result['Level'])
        data['Type'].extend(result['Type'])
        data['ID'].extend(result['ID'])
        data['Key'].extend(result['Key'])

    return data


class Formatter(object):

    """Format performance values to a human-readable format."""

    def memory_to_human(self, _bytes, unit='auto', decimals=2):
        """Transform used memory into a better suited unit.

        Args:
            _bytes (float): Used Bytes.
            unit (str, optional): Defaults to 'auto'. Unit to transform seconds into.
            decimals (int, optional): Defaults to 2. To which decimal point is rounded to.

        Returns:
            string: used memory suffixed with unit identifer
        """
        if _bytes <= 0:
            return '0.00 KB'

        # If decimals is less than 0
        decimals = 2 if decimals < 0 else decimals

        value = 0
        units = {
            'B': 0, 'KB': 1, 'MB': 2, 'GB': 3, 'TB': 4, 'PB': 5, 'EB': 6, 'ZB': 7, 'YB': 8
        }

        if _bytes > 0:
            # Generate automatic prefix by bytes if wrong prefix given
            if unit not in units:
                power = math.floor(math.log(_bytes) / math.log(1024))
                unit = [k for k, v in units.items() if v == power][0]

            # Calculate byte value by prefix
            value = (_bytes / pow(1024, math.floor(units[unit])))

        return self.format_number(value, decimals, unit)

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
                unit = u'\u03BCs'

        if unit == u'\u03BCs':
            return self.format_number(seconds * 1000000, decimals, unit)
        elif unit == 'ms':
            return self.format_number(seconds * 1000, decimals, unit)
        elif unit == 's':
            return self.format_number(seconds * 1, decimals, unit)
        else:
            raise TypeError('Performance format {} does not exist.'.format(unit))

    def print_table(self, points, tablefmt='psql'):
        """Print performance table in human-readable format.

        Args:
            points (list): Measuring Points.
            tablefmt (str, optional): Defaults to 'psql'. Table format for :mod:`tabulate`
        """
        print(self.get_table(points, tablefmt))

    def get_table(self, points, tablefmt='psql'):
        """Print performance table in human-readable format.

        Args:
            points (list): Measuring Points.
            tablefmt (str, optional): Defaults to 'psql'. Table format for :mod:`tabulate`

        Returns:
            str: Performance table
        """
        data = []
        headers = [
           colored('Label', 'cyan', attrs=['bold']),
           colored('Time', 'cyan', attrs=['bold']),
           colored('Memory', 'cyan', attrs=['bold']),
           colored('Peak Memory', 'cyan', attrs=['bold'])
        ]

        # Color items and build data list
        for row in points:
            label = {'format': u'› {}', 'attrs': ['bold']}
            time = {
                'val': self.time_to_human(row['mean_time']),
                'std': self.time_to_human(row['std_time']),
                'attrs': ['bold']
            }
            memory = {
                'val': self.memory_to_human(row['mean_memory']),
                'std': self.memory_to_human(row['std_memory']),
                'peak': self.memory_to_human(row['peak_memory']),
                'frmt': u'{} (± {})',
                'attrs': ['bold']
            }

            if row['type'] == 'message':
                label = {'format': '  {}', 'attrs': ['dark']}
                memory['frmt'] = '--'
                memory['peak'] = '--'

            data.append([
                colored(label['format'].format(row['label']), attrs=label['attrs']),
                u'{} (± {})'.format(colored(time['val'], attrs=time['attrs']), time['std']),
                memory['frmt'].format(colored(memory['val'], attrs=memory['attrs']), memory['std']),
                colored(memory['peak'], attrs=memory['attrs'])
            ])

        return tabulate.tabulate(data, headers, tablefmt=tablefmt)

    @staticmethod
    def format_number(value, decimals, unit):
        """Round a number and add a unit.

        Args:
            value (float): Number to round.
            decimals (int): Numer of decimals places.
            unit (str): Unit to append

        Returns:
            string
        """
        _format = u'{:.%sf} {}' % decimals
        return _format.format(value, unit)


class Point(object):

    """Measuring Point Data Structure.

    Keeps track of execution time and memory consumption. You can also append
    messages to a point to keep track of different events. Each message contains
    the time since the last message was logged and the message content itself.

    Attributes:
        label (str): Label of the point.
        id (int): Id to keep track of same points when iterating.
        start_time (float): Startpoint Timestamp.
        stop_time (float): Endpoint Timestamp.
        start_memory (int): Memory consumption on start.
        stop_memory (int): Memory consumption on end.
        messages (list): List of optional messages.
        subpoints (list): List of optional subpoints.
    """

    def __init__(self, label, iter_id=None):
        """Set the current time and memory consumption and default values for other attributes.

        Args:
            label (str): Label of the point.
            iter_id (int): Id to keep track of same points when iterating.
        """
        self.label = label
        self.id = iter_id
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
            msg (str): Enter message
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
            'id': self.id,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'difference_time': self.stop_time - self.start_time,
            'start_memory': self.start_memory,
            'stop_memory': self.stop_memory,
            'difference_memory': self.stop_memory - float(self.start_memory),
            'peak_memory': max(self.stop_memory, self.start_memory),
            'messages': self.messages,
            'subpoints': self.subpoints
        }

    def to_df(self):
        """Transform point to dataframe.

        Returns:
            dict: Dataframe
        """
        return _to_df(self.to_dict())


class Performance(object):

    """Easily measure the performance of your python scripts.

    Attributes:
        points (list): List of measuring points
        iteration (int): Number of current iteration
        formatter (Formatter): Formatter to output human readable results
    """

    def __init__(self):
        """Set measuring points list and default formatter."""
        self.points = []
        self.iteration = 0
        self.set_formatter(Formatter())

    def set_formatter(self, formatter):
        """Set a formatter for human readable output.

        Args:
            formatter (Formatter): Human-readable output formatter
        """
        self.formatter = formatter

    def iterate(self, start, stop):
        """Iterate over multiple performance points to later calculate avg and standard deviation.

        Args:
            start (int): Start at
            stop (int): Stop at

        Yields:
            int: current iteration
        """
        current = start
        while current <= stop:
            self.iteration = 0
            yield current
            current += 1

    @contextmanager
    def point(self, label='Point'):
        """Set measuring point with or without a label.

        Keyword Arguments:
            label (str, optional): Defaults to 'Point'. Enter point label

        Example::

            with performance.point('Task A') as point:
                # do something
                point.message('Some Message)

        Yields:
            Point: new measuring point
        """
        try:
            self.iteration += 1
            point = Point(label, self.iteration)

            if len(self.points) and self.points[-1].stop_time == 0:
                self.points[-1].subpoints.append(point)
            else:
                self.points.append(point)

            yield point

        except Exception as exc:
            print('Exception: {}'.format(exc))
        finally:
            point.stop_time = time.time()
            point.stop_memory = memory_usage()

    def export(self, metrics=False):
        """Export the measuring points as a dictionary.

        Args:
            metrics (bool, optional). Defaults to False. Whether or not metrics should be calculated

        Returns:
            dict: Measuring points
        """
        # Build grouped Dataframe of points
        frames = [point.to_df() for point in self.points]
        result = collections.OrderedDict()
        for frame in frames:
            key = '|'.join(frame['Key'])
            if key in result:
                result[key].append(frame)
            else:
                result[key] = [frame]

        # Transform to ouput format
        data = []
        for row in result.values():
            # Only last iteration
            points = self._get_points(
                row[-1], ['Label', 'Level', 'Type', 'Time', 'Memory', 'Peak Memory']
            )

            # Calculate metrics for time and memory
            if metrics:
                metrics = self._calc_metrics(row)

                # add metrics to each point
                for idx, point in enumerate(points):
                    point['mean_time'] = metrics[idx][0]
                    point['std_time'] = metrics[idx][1]
                    point['mean_memory'] = metrics[idx][2]
                    point['std_memory'] = metrics[idx][3]

            # add points to data list
            data.extend(points)

        return data

    def _get_points(self, points, attrs):
        """Transform points to another format for better usability.

        Args:
            points (dict): Points
            attrs (list): list of point attributes

        Returns:
            list: List of Points in the format of [{'label': 'foo', ...}, {'label': 'bar'}]
        """
        items = zip(*[points[k] for k in attrs])
        return [
            {
                key.lower().replace(' ', '_'): item[idx] for idx, key in enumerate(attrs)
            }
            for item in items
        ]

    def _calc_metrics(self, row):
        """Calculate metrics for time and memory.

        Args:
            row (list): List of points

        Returns:
            set: Mean Time, STD Time, Mean Memory, STD Memory
        """
        times = list(zip(*[points['Time'] for points in row]))
        mean_time = list(map(Performance.mean, times))
        std_time = list(map(Performance.standard_deviation, times))

        memory = list(zip(*[points['Memory'] for points in row]))
        mean_memory = list(map(Performance.mean, memory))
        std_memory = list(map(Performance.standard_deviation, memory))

        return list(zip(mean_time, std_time, mean_memory, std_memory))

    def results(self):
        """Print the performance results in a human-readable format."""
        self.formatter.print_table(self.export(metrics=True))

    # Mean and Standard Deviation
    @staticmethod
    def mean(values):
        """Calculate Mean of values.

        Args:
            values (list): List of values

        Returns:
            float: Mean value
        """
        return sum(values) / float(len(values))

    @staticmethod
    def standard_deviation(numbers):
        """Calculate the standard deviation.

        Args:
            numbers (list): List of numbers

        Returns:
            float: Standard Deviation
        """
        mean = Performance.mean(numbers)
        return math.sqrt(
            Performance.mean([math.pow(number - mean, 2) for number in numbers])
        )
