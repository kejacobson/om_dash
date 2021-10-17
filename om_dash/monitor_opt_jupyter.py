from jupyter_dash import JupyterDash
from om_dash.opt_hist_gui_core import GuiOptHistoryCore, add_callbacks


core = GuiOptHistoryCore()
monitor = JupyterDash()
monitor.layout = core.full_layout
add_callbacks(monitor, core)
