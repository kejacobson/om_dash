from om_dash.plotly_base import PlotlyBase
from om_dash.opt_hist_figure_generator import OptHistoryFigureGenerator
from om_dash.recorder_parser import RecorderParser

from dash import html, dcc
from dash.dependencies import Input, Output, State


class GuiOptHistoryCore(PlotlyBase):
    def __init__(self):
        """
        The primary dash and html elements in the GUI for monitoring the history of OpenMDAO optimizations
        """
        super().__init__()

        self.recorder_file = 'nonexistent_history_file_to_start.sql'
        self.default_refresh_time_in_seconds = 30

        self.parser = RecorderParser(self.recorder_file)
        self.fig_generator = OptHistoryFigureGenerator()

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
                               value=self.default_refresh_time_in_seconds, style=dict(width='30%')),
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
        self.fig_generator.parser = self.parser
        self.opt_hist_fig = self.fig_generator.create_figure()
        return self.opt_hist_fig


def add_callbacks(app, core: GuiOptHistoryCore):

    @app.callback(
        [Output('live_update_interval', 'interval'),
         Output('opt_hist_graph', 'figure')],
        [Input('start_button', 'n_clicks')],
        [State('refresh_interval_input', 'value'),
         State('recorder_file', 'value'),
         State('include_dvs_checklist', 'value')])
    def set_live_update_interval_and_initial_plots_div(n_clicks, interval_in_seconds,
                                                       recorder_file, dv_checklist):
        core.fig_generator.include_dvs = True if 'DVS' in dv_checklist else False
        if n_clicks > 0:
            interval_in_milliseconds = interval_in_seconds * 1000
            core.recorder_file = recorder_file
            core.parser.update_histories_from_recorder(core.recorder_file)
        else:
            interval_in_milliseconds = 1e9
        fig = core.generate_opt_history_fig()
        return interval_in_milliseconds, fig

    @app.callback(
        Output('opt_hist_graph', 'extendData'),
        Input('live_update_interval', 'n_intervals'))
    def update_plot_data(n_intervals):
        core.parser.update_histories_from_recorder(core.recorder_file)
        return core.fig_generator.generate_extend_data_for_opt_hist_traces()

    @app.callback(
        Output('opt_export_html_status', 'children'),
        [Input('opt_export_html_button', 'n_clicks')],
        [State('opt_export_html_input', 'value')])
    def export_opt_history_fig_to_html(n_clicks, filename):
        status = ''
        if n_clicks > 0:
            status = core.export_fig_as_html(core.opt_hist_fig, filename)
        return status
