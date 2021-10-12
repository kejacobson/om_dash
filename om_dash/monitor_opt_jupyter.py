from jupyter_dash import JupyterDash
from dash.dependencies import Input, Output, State
from .monitor_opt import GuiOptimizationHistory

app = JupyterDash()
gui = GuiOptimizationHistory()

app.layout = gui.full_layout


@app.callback(
    [Output('live_update_interval', 'interval'),
        Output('opt_hist_graph', 'figure')],
    [Input('start_button', 'n_clicks')],
    [State('refresh_interval_input', 'value'),
        State('recorder_file', 'value')])
def set_live_update_interval_and_initial_plot(n_clicks, interval_sec, recorder_file):
    if n_clicks > 0:
        interval_ms = interval_sec * 1000
        gui.read_histories_from_recorder(recorder_file)
    else:
        interval_ms = 1e9
    fig = gui.generate_history_fig()
    return interval_ms, fig


@app.callback(
    Output('opt_hist_graph', 'extendData'),
    [Input('live_update_interval', 'n_intervals')],
    [State('recorder_file', 'value')])
def update_plot_data(n_intervals, recorder_file):
    gui.read_histories_from_recorder(recorder_file)
    return gui.generate_extend_data_for_opt_hist_traces()


@app.callback(
    Output('opt_hist_export_html_status', 'children'),
    [Input('opt_hist_export_html_button', 'n_clicks')],
    [State('opt_hist_export_html_input', 'value')])
def export_opt_history_html(n_clicks, filename):
    status = ''
    if n_clicks > 0:
        status = gui.export_fig_as_html(gui.obj_con_hist_fig, filename)
    return status
