#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# thoth-lab
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Various helpers and utils for interaction with the graph database."""

import asyncio
import typing

from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
import pandas as pd
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go


class GraphQueryResult(object):
    def __init__(self, result):
        """Initialization.

        :param result: the result to be used as a query result, can be directly coroutine that is fired.
        """
        if isinstance(result, typing.Coroutine):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(result)

        self.result = result

    def _get_items(self):
        """Get items from the result."""
        items = list(self.result.items())
        labels = [item[0] for item in items]
        values = [item[1] for item in items]
        return labels, values

    def to_dataframe(self):
        """Construct a panda's dataframe on results."""
        return pd.DataFrame(data=self.result)

    def plot_pie(self):
        """Plot a pie of results into Jupyter notebook."""
        init_notebook_mode(connected=True)

        labels, values = self._get_items()
        trace = go.Pie(labels=labels, values=values)
        return iplot([trace])

    def plot_bar(self):
        """Plot histogram of results obtained."""
        init_notebook_mode(connected=True)

        labels, values = self._get_items()
        trace = go.Bar(x=labels, y=values)
        return iplot([trace])

    def serialize(self):
        """Serialize the output of graph query."""
        # It should be fine to just use one check for nested parts. We can extend this later on.
        def _serialize(obj):
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            return obj

        if isinstance(self.result, list):
            return list(map(lambda x: _serialize(x), self.result))

        return _serialize(self.result)


def get_graph_traversal(location: str, port: int=80):
    """Get graph traversal handle for your experiments.

    :param location: A location to the graph database instance. Recommended to be
                     used with :func:`thoth.lab.utils.obtain_location`
    :param port: a port number on which the gremlin listens on
    :return: a graph traversal object "g"
    """
    return Graph().traversal().withRemote(DriverRemoteConnection(f'ws://{location}:{port}/gremlin', 'g'))
