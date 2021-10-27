"""
This script is a dash gui used to monitor an OpenMDAO optimization by periodically updating a
plotly figure of the history from an OpenMDAO recorder.
"""

import argparse
import dash
from om_dash.opt_hist_gui_core import GuiOptHistoryCore, add_callbacks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    core = GuiOptHistoryCore()
    monitor = dash.Dash()
    monitor.layout = core.full_layout
    add_callbacks(monitor, core)

    monitor.run_server(debug=True, dev_tools_ui=True,
                       dev_tools_hot_reload=False, use_reloader=False)


if __name__ == '__main__':
    main()
