import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from om_dash.plotly_base import PlotlyBase
from .recorder_parser import RecorderParser


class OptHistoryFigureGenerator(PlotlyBase):
    def __init__(self, parser: RecorderParser = None):
        self.parser = parser
        self.include_dvs = True
        super().__init__()

    def _key_is_a_constraint_key(self, key):
        return key in self.parser.cons.keys()

    def _key_is_a_dv_key(self, key):
        return key in self.parser.dvs.keys()

    def create_figure(self):
        all_data = self._get_opt_history_data_from_parser()

        self.plotted_iterations = all_data['Iteration'].to_numpy()
        on_secondary_y = self._determine_which_traces_to_put_on_2nd_y_axis(all_data)
        need_y2_axis = any(on_secondary_y)

        xaxis, yaxis = self.get_axis_settings()
        xaxis['title'] = 'Iteration'
        yaxis['title'] = 'Objective'
        if need_y2_axis:
            yaxis2 = self.get_secondary_y_axis_settings()
            yaxis2['title'] = 'Constraints and DVs' if self.include_dvs else 'Constraints'
        else:
            yaxis2 = None

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        self.set_default_figure_layout(fig, xaxis, yaxis, yaxis2)

        for sec_y, (key, vals) in zip(on_secondary_y, all_data.items()):
            if key == 'Iteration':
                continue

            fig.add_trace(go.Scattergl(x=self.plotted_iterations,
                                       y=vals,
                                       mode='lines+markers',
                                       name=key),
                          secondary_y=sec_y)

        return fig

    def generate_extend_data_for_opt_hist_traces(self):
        all_data = self._get_opt_history_data_from_parser()

        iteration_column_offset = 1
        n_traces = all_data.shape[1] - iteration_column_offset
        new_data = dict(x=[[] for _ in range(n_traces)],
                        y=[[] for _ in range(n_traces)])
        if self._valid_data_was_read(all_data):
            start = self.plotted_iterations[-1] + 1
            new_iterations = np.arange(start, all_data.shape[0])

            if self._have_new_data_to_plot(new_iterations):
                new_data = dict(x=[new_iterations.copy() for _ in range(n_traces)], y=[
                                val[new_iterations].to_numpy() for key, val in all_data.items() if key != 'Iteration'])
                self.plotted_iterations = np.arange(new_iterations[-1]+1)
        return new_data

    def _valid_data_was_read(self, all_data: pd.DataFrame):
        return all_data.shape[0] > 0

    def _data_has_already_been_plotted(self):
        return self.plotted_iterations.size > 0

    def _have_new_data_to_plot(self, new_iterations):
        return new_iterations.size > 0

    def _get_opt_history_data_from_parser(self):
        if self.include_dvs:
            return self.parser.get_dataframe_of_all_data()
        else:
            return self.parser.get_dataframe_of_objectives_and_constraints()

    def _determine_which_traces_to_put_on_2nd_y_axis(self, all_data: pd.DataFrame):
        secondary_y = []
        for key in all_data.keys():
            if self._key_is_a_constraint_key(key):
                secondary_y.append(True)
            elif self._key_is_a_dv_key(key):
                secondary_y.append(True)
            else:
                secondary_y.append(False)
        return secondary_y
