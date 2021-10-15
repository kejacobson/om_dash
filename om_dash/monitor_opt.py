import dash
from om_dash.opt_hist_gui_core import GuiOptHistoryCore, add_callbacks


core = GuiOptHistoryCore()
app = dash.Dash()
app.layout = core.full_layout
add_callbacks(app, core)

app.run_server(debug=True, dev_tools_ui=True, dev_tools_hot_reload=False, use_reloader=False)
