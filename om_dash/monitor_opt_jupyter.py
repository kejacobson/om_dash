"""
The jupyter notebook version of the GUI for live monitoring of an OpenMDAO optimization
This file should be loaded as a module in jupyter then the GUI is launched with:

monitor.run_server(mode='inline')
"""
from jupyter_dash import JupyterDash
from om_dash.opt_hist_gui_core import GuiOptHistoryCore, add_callbacks


core = GuiOptHistoryCore()
monitor = JupyterDash()
monitor.layout = core.full_layout
add_callbacks(monitor, core)
