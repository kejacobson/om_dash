import numpy as np
from om_dash.plotly_base import PlotlyBase
from om_dash.recorder_parser import RecorderParser
import pandas as pd

import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots


class GuiOptHistoryCore(PlotlyBase):
    def __init__(self):
        super().__init__()

        self.recorder_file = 'paraboloid.sql'
        self.include_dvs = True

        self.parser = RecorderParser()
        self.parser.read_histories_from_recorder(self.recorder_file)

        sections = []
        sections.append(self.create_optimization_information_div())
        sections.append(self.create_graphs_div())
        self.full_layout = html.Div(children=sections,
                                    style=dict(backgroundColor=self.background_color))

    def create_optimization_information_div(self):
        start_button = html.Button('Start', id='start_button', n_clicks=0,
                                   style=dict(backgroundColor='dodgerblue',
                                              fontSize='24px',
                                              color='white'))
        children = [html.H1('Case Information'),
                    self.create_case_information_input_table(),
                    start_button,
                    dcc.Interval(id='live_update_interval', interval=1e9, n_intervals=0)]
        div = html.Div(children=children, id='div_case_info')
        return div

    def create_case_information_input_table(self):
        return html.Table([
            html.Tr([html.Td('Refresh interval in seconds:'),
                     dcc.Input(id='refresh_interval_input', type='number',
                               value=5, style=dict(width='30%')),
                     ]),
            html.Tr([html.Td('Recorder file:'),
                     dcc.Input(id='recorder_file', type='text',
                               value='paraboloid.sql', style=dict(width='300%'))
                     ]),
            html.Tr([self._create_checklist_for_including_dvs()]),
        ])

    def _create_checklist_for_including_dvs(self):
        return dcc.Checklist(options=[{'label': 'Include DVs', 'value': 'DVS'}],
                             value=['DVS'],
                             id='include_dvs_checklist')

    def create_graphs_div(self):
        div = html.Div(children=self.generate_graphs(),
                       id='div_outer_graphs')
        return div

    def generate_graphs(self):
        return [self.generate_opt_history_div()]

    def generate_opt_history_div(self):
        fig = self.generate_opt_history_fig()
        export_html = self.generate_export_field_and_button(default_filename='opt_hist.html',
                                                            button_txt='Export interactive figure',
                                                            id_base='opt_export_html')
        children = [html.H1('Optimization History'),
                    dcc.Graph(figure=fig, id='opt_hist_graph')]
        children.extend(export_html)
        return html.Div(children=children)

    def generate_opt_history_fig(self):

        if self.include_dvs:
            all_data = self.parser.get_dataframe_of_all_data()
        else:
            all_data = self.parser.get_dataframe_of_objectives_and_constraints()

        self.iterations = np.arange(all_data.shape[0])
        on_secondary_y = self.determine_which_traces_to_put_on_2nd_y_axis(all_data)
        include_y2 = any(on_secondary_y)

        xaxis, yaxis = self.get_axis_settings()
        xaxis['title'] = 'Iteration'
        yaxis['title'] = 'Objective'
        if include_y2:
            yaxis2 = self.get_secondary_y_axis_settings()
            yaxis2['title'] = 'Constraints and DVs' if self.include_dvs else 'Constraints'
        else:
            yaxis2 = None

        self.opt_hist_fig = make_subplots(specs=[[{"secondary_y": True}]])
        self.set_default_figure_layout(self.opt_hist_fig, xaxis, yaxis, yaxis2)

        for sec_y, (key, vals) in zip(on_secondary_y, all_data.items()):
            self.opt_hist_fig.add_trace(go.Scattergl(x=self.iterations,
                                                     y=vals,
                                                     mode='lines+markers',
                                                     name=key),
                                        secondary_y=sec_y)

        return self.opt_hist_fig

    def determine_which_traces_to_put_on_2nd_y_axis(self, all_data: pd.DataFrame):
        secondary_y = []
        for key in all_data.keys():
            if key in self.parser.cons.keys():
                secondary_y.append(True)
            elif key in self.parser.dvs.keys():
                secondary_y.append(True)
            else:
                secondary_y.append(False)
        return secondary_y

    def generate_extend_data_for_opt_hist_traces(self):
        if self.iterations.size == 0:
            return dict(x=[], y=[])

        if self.include_dvs:
            all_data = self.parser.get_dataframe_of_all_data()
        else:
            all_data = self.parser.get_dataframe_of_objectives_and_constraints()
        n_traces = all_data.shape[1]
        extend_data = dict(x=[[] for _ in range(n_traces)],
                           y=[[] for _ in range(n_traces)])

        if all_data.shape[0] > 0 and self.iterations.size > 0:
            start = self.iterations[-1] + 1
            new_iterations = np.arange(start, all_data.shape[0])
            if new_iterations.size > 0:
                extend_data = dict(x=[new_iterations.copy() for _ in range(n_traces)], y=[
                                   val[new_iterations].to_numpy() for _, val in all_data.items()])
                self.iterations = np.arange(new_iterations[-1]+1)
        return extend_data


def add_callbacks(app, core: GuiOptHistoryCore):
    @app.callback(
        [Output('live_update_interval', 'interval'),
         Output('opt_hist_graph', 'figure')],
        [Input('start_button', 'n_clicks')],
        [State('refresh_interval_input', 'value'),
         State('recorder_file', 'value'),
         State('include_dvs_checklist', 'value')])
    def set_live_update_interval_and_initial_plots_div(
            n_clicks, interval_sec, recorder_file, check):
        core.include_dvs = True if 'DVS' in check else False
        if n_clicks > 0:
            interval_ms = interval_sec * 1000
            core.recorder_file = recorder_file
            core.parser.read_histories_from_recorder(core.recorder_file)
        else:
            interval_ms = 1e9
        fig = core.generate_opt_history_fig()
        return interval_ms, fig

    @app.callback(
        Output('opt_hist_graph', 'extendData'),
        Input('live_update_interval', 'n_intervals'))
    def update_plot_data(n_intervals):
        core.parser.read_histories_from_recorder(core.recorder_file)
        return core.generate_extend_data_for_opt_hist_traces()

    @ app.callback(
        Output('opt_export_html_status', 'children'),
        [Input('opt_export_html_button', 'n_clicks')],
        [State('opt_export_html_input', 'value')])
    def export_obj_con_history_html(n_clicks, filename):
        status = ''
        if n_clicks > 0:
            status = core.export_fig_as_html(core.opt_hist_fig, filename)
        return status
