# -*- coding: utf-8 -*-
from experimentum.Experiments import Performance
from experimentum.Experiments.Performance import Formatter, Point
import pytest


class TestPerformance(object):
    def setup_method(self):
        """ setup """
        self.performance = Performance()

    def test_set_formatter(self):
        formatter = Formatter()
        self.performance.set_formatter(formatter)
        assert self.performance.formatter == formatter

    def test_add_point(self):
        with self.performance.point() as point:
            assert isinstance(point, Point)
            assert point.label == 'Point'
            assert point.id is None
            assert point.start_time >= 0
            assert point.stop_time == 0
            assert point.start_memory >= 0
            assert point.stop_memory == 0
            assert point.messages == []
            assert point.subpoints == []

        assert point.stop_memory > 0
        assert point.stop_time > 0

    def test_add_subpoint(self):
        with self.performance.point() as point:
            assert point.subpoints == []

            with self.performance.point() as subpoint:
                assert subpoint.subpoints == []

        assert point.subpoints == [subpoint]

    def test_add_message_to_point(self):
        with self.performance.point() as point:
            point.message('some message')
            assert point.messages[0][0] >= 0
            assert point.messages[0][1] == 'some message'

    def test_export(self):
        with self.performance.point('Foo Label') as point:
            pass

        export = self.performance.export()
        assert len(export) == 1
        assert 'peak_memory' in export[0]
        assert 'memory' in export[0]
        assert 'time' in export[0]
        assert 'level' in export[0]
        assert 'type' in export[0]
        # assert 'Id' in export[0]
        assert 'label' in export[0]

    def test_export_with_metrics(self):
        with self.performance.point('Foo Label') as point:
            pass

        export = self.performance.export(metrics=True)
        assert len(export) == 1
        assert 'peak_memory' in export[0]
        assert 'memory' in export[0]
        assert 'time' in export[0]
        assert 'mean_memory' in export[0]
        assert 'std_memory' in export[0]
        assert 'level' in export[0]
        assert 'mean_time' in export[0]
        assert 'std_time' in export[0]
        assert 'type' in export[0]
        # assert 'Id' in export[0]
        assert 'label' in export[0]

    def test_iterate(self):
        assert self.performance.iteration is 0

        for i in self.performance.iterate(0, 5):
            assert self.performance.iteration is 0
            self.performance.iteration = i

    def test_results(self, capsys):
        with self.performance.point('Foo Label') as point:
            point.message('some msg')

            with self.performance.point('Sub Foo Label') as point:
                point.message('some sub msg')

        self.performance.results()
        output = capsys.readouterr().out

        assert 'Time' in output
        assert 'Memory' in output
        assert 'Peak Memory' in output
        assert 'Label' in output
        assert 'Foo Label' in output
        assert 'some msg' in output
        assert 'Sub Foo Label' in output
        assert 'some sub msg' in output

    def test_time_to_human_format(self):
        formatter = Formatter()

        assert formatter.time_to_human(1) == '1.00 s'
        assert formatter.time_to_human(0.001) == '1.00 ms'
        assert formatter.time_to_human(0.0001) == u'100.00 \u03BCs'

        assert formatter.time_to_human(1, 'ms') == '1000.00 ms'
        assert formatter.time_to_human(1, decimals=4) == '1.0000 s'

        with pytest.raises(TypeError):
            formatter.time_to_human(2, 'foo')
