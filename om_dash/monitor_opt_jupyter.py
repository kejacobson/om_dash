from jupyter_dash import JupyterDash
from om_dash.opt_hist_gui_core import GuiOptHistoryCore, add_callbacks


core = GuiOptHistoryCore()
app = JupyterDash()
app.layout = core.full_layout
add_callbacks(app, core)
