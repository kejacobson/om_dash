import os
import pandas as pd
import openmdao.api as om
import numpy as np
from om_dash.plotly_base import PlotlyBase

import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output, State


class GuiOptHistoryCore(PlotlyBase):
    def __init__(self):
        super().__init__()

        recorder_filename = 'paraboloid.sql'
        self.read_histories_from_recorder(recorder_filename)
        xlog = False
        ylog = False

        sections = []
        sections.append(self.create_optimization_information_div())
        sections.append(self.create_graphs_div(xlog, ylog))
        self.full_layout = html.Div(children=sections,
                                    style=dict(backgroundColor=self.background_color))

    def read_histories_from_recorder(self, recorder_filename):
        self.objs = self._create_empty_dataframe()
        self.dvs = self._create_empty_dataframe()
        self.cons = self._create_empty_dataframe()
        if os.path.exists(recorder_filename):
            case_recorder = om.CaseReader(recorder_filename)
            if len(case_recorder.get_cases()) > 0:
                self.objs, self.dvs = self._parse_objective_and_dv_histories(case_recorder)
                self.cons = self._parse_constraint_history(case_recorder)

    def _create_empty_dataframe(self):
        return pd.DataFrame({'empty': []})

    def _parse_objective_and_dv_histories(self, case_recorder):
        objs = self._create_empty_dataframe()
        dvs = self._create_empty_dataframe()

        for icase, case in enumerate(case_recorder.get_cases()):
            dv = self._to_dataframe(case.get_design_vars(scaled=False))
            obj = self._to_dataframe(case.get_objectives(scaled=False))

            if icase == 0:
                dvs = dv
                objs = obj
            else:
                dvs = pd.concat([dvs, dv], ignore_index=True)
                objs = pd.concat([objs, obj], ignore_index=True)
        return objs, dvs

    def _parse_constraint_history(self, case_recorder):
        if self._there_are_no_constraints(case_recorder):
            return self._create_empty_dataframe()

        for icase, case in enumerate(case_recorder.get_cases()):
            con = self._to_dataframe(case.get_constraints(scaled=False))

            if icase == 0:
                cons = con
            else:
                cons = pd.concat([cons, con], ignore_index=True)
        return cons

    def _to_dataframe(self, values_dict):
        new_dict = {}
        for key, vals in values_dict.items():
            if vals.size == 1:
                new_dict[key] = np.array(vals)
            else:
                for i, val in enumerate(vals):
                    new_dict[f'{key}_{i}'] = np.array(val)
        return pd.DataFrame(new_dict)

    def _there_are_no_constraints(self, case_recorder):
        return len(case_recorder.get_case(0).get_constraints().keys()) == 0

    def create_optimization_information_div(self):
        start_button = html.Button('Start', id='start_button', n_clicks=0,
                                   style=dict(backgroundColor='lightblue',
                                              fontSize='24px'))
        children = [html.H1('Case Information'),
                    self.create_case_information_input_table(),
                    start_button,
                    dcc.Interval(id='live_update_interval', interval=10*60*1000, n_intervals=0)]
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
        ])

    def create_graphs_div(self, xlog, ylog):
        div = html.Div(children=self.generate_graphs(xlog, ylog),
                       id='div_outer_graphs')
        return div

    def generate_graphs(self, xlog, ylog):
        return [self.generate_history_div(xlog, ylog)]

    def generate_history_div(self, xlog, ylog):
        fig = self.generate_history_fig(xlog, ylog)
        export_html = self.generate_export_field_and_button(default_filename='opt_hist.html',
                                                            button_txt='Export interactive figure',
                                                            id_base='opt_hist_export_html')
        children = [html.H1('Optimization History'),
                    dcc.Graph(figure=fig, id='opt_hist_graph')]
        children.extend(export_html)
        return html.Div(children=children)

    def generate_history_fig(self, xlog=False, ylog=False):
        all_data = self._merge_dataframes(self.objs, self.cons, self.dvs)

        self.iterations = np.arange(all_data.shape[0])
        self.obj_con_hist_fig = go.Figure()
        for key, vals in all_data.items():
            self.obj_con_hist_fig.add_trace(go.Scattergl(x=self.iterations,
                                                         y=vals,
                                                         mode='lines+markers',
                                                         name=key))

        xaxis, yaxis = self.get_axis_settings()
        xaxis['title'] = 'Iteration'
        xaxis['type'] = 'log' if xlog else 'linear'
        yaxis['title'] = 'Value'
        yaxis['type'] = 'log' if ylog else 'linear'
        self.set_default_figure_layout(self.obj_con_hist_fig, xaxis, yaxis)

        return self.obj_con_hist_fig

    def _merge_dataframes(self, objs, cons, dvs):
        if objs.size == 0:
            all_data = self._create_empty_dataframe()
        elif cons.size > 0:
            all_data = pd.concat([objs, cons, dvs], axis=1)
        else:
            all_data = pd.concat([objs, dvs], axis=1)
        return all_data

    def generate_extend_data_for_opt_hist_traces(self):
        if self.iterations.size == 0:
            return dict(x=[], y=[])

        all_data = self._merge_dataframes(self.objs, self.cons, self.dvs)
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


def add_callbacks(app, core):
    @app.callback(
        [Output('live_update_interval', 'interval'),
         Output('opt_hist_graph', 'figure')],
        [Input('start_button', 'n_clicks')],
        [State('refresh_interval_input', 'value'),
         State('recorder_file', 'value')])
    def set_live_update_interval_and_initial_plot(n_clicks, interval_sec, recorder_file):
        if n_clicks > 0:
            interval_ms = interval_sec * 1000
            core.read_histories_from_recorder(recorder_file)
        else:
            interval_ms = 1e9
        fig = core.generate_history_fig()
        return interval_ms, fig

    @app.callback(
        Output('opt_hist_graph', 'extendData'),
        [Input('live_update_interval', 'n_intervals')],
        [State('recorder_file', 'value')])
    def update_plot_data(n_intervals, recorder_file):
        core.read_histories_from_recorder(recorder_file)
        return core.generate_extend_data_for_opt_hist_traces()

    @app.callback(
        Output('opt_hist_export_html_status', 'children'),
        [Input('opt_hist_export_html_button', 'n_clicks')],
        [State('opt_hist_export_html_input', 'value')])
    def export_opt_history_html(n_clicks, filename):
        status = ''
        if n_clicks > 0:
            core.obj_con_hist_fig.write_html(filename)
            #status = core.export_fig_as_html(core.obj_con_hist_fig, filename)
            status = 'done'
        return status