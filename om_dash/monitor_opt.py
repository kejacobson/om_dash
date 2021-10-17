import dash
from om_dash.opt_hist_gui_core import GuiOptHistoryCore, add_callbacks


core = GuiOptHistoryCore()
monitor = dash.Dash()
monitor.layout = core.full_layout
add_callbacks(monitor, core)

monitor.run_server(debug=True, dev_tools_ui=True, dev_tools_hot_reload=False, use_reloader=False)
