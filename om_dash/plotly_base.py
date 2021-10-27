
import numpy as np
from typing import List

import plotly.graph_objects as go
from dash import dcc, html


class PlotlyBase:
    def __init__(self):
        """
        Plotly and dash functions and settings not specific to an individual application
        """
        self._set_plot_style()

    def _set_plot_style(self):
        self.axis_settings = dict(linecolor='black',
                                  linewidth=3,
                                  showgrid=True,
                                  gridcolor='black',
                                  ticks='outside',
                                  zerolinecolor='black',
                                  exponentformat='e')
        self.background_color = 'white'
        self.plot_height = 700

    def set_default_figure_layout(self, fig: go.Figure, xaxis: dict, yaxis: dict,
                                  yaxis2=None, add_update_menus=True):
        have_2nd_yaxis = False if yaxis2 is None else True
        if add_update_menus:
            updatemenus, menu_annotations = self.make_update_menus_for_log_scale(have_2nd_yaxis)
        else:
            updatemenus = None
            menu_annotations = None
        fig.update_layout(updatemenus=updatemenus,
                          xaxis=xaxis,
                          yaxis=yaxis,
                          legend=dict(x=1.1, y=0.5),
                          hoverlabel=dict(bgcolor='white',
                                          font=dict(color='black')),
                          plot_bgcolor=self.background_color,
                          paper_bgcolor=self.background_color,
                          height=self.plot_height,
                          width=self.plot_height*2,
                          annotations=menu_annotations)
        if have_2nd_yaxis:
            fig.update_yaxes(yaxis2, secondary_y=True)

    def get_axis_settings(self):
        return self.axis_settings.copy(), self.axis_settings.copy()

    def get_secondary_y_axis_settings(self):
        yaxis2 = self.axis_settings.copy()
        yaxis2['zerolinecolor'] = 'lightgray'
        yaxis2['showgrid'] = True
        yaxis2['gridcolor'] = 'lightgray'
        yaxis2['showline'] = True
        yaxis2['linecolor'] = 'lightgray'
        return yaxis2

    def generate_export_field_and_button(self, default_filename, button_txt, id_base):
        comps = []
        comps.append(dcc.Input(id=f'{id_base}_input', type='text',
                               value=default_filename,
                               style=dict(width='30%'))
                     )
        comps.append(html.Button(button_txt,
                                 id=f'{id_base}_button',
                                 n_clicks=0)
                     )
        comps.append(html.Div(id=f'{id_base}_status',
                              style={'whiteSpace': 'pre-line'})
                     )
        return comps

    def make_update_menus_for_log_scale(self, have_2nd_yaxis=False):
        button_layer_height = 1.08
        x_axis_menu = dict(active=1,
                           x=0.05,
                           xanchor='left',
                           y=button_layer_height,
                           yanchor='top',
                           buttons=[dict(label='Log Scale',
                                         method='relayout',
                                         args=[{'xaxis.type': 'log'}]),
                                    dict(label='Linear Scale',
                                         method='relayout',
                                         args=[{'xaxis.type': 'linear'}]),
                                    ]
                           )

        y_axis_menu = dict(active=1,
                           x=0.25,
                           xanchor='left',
                           y=button_layer_height,
                           yanchor='top',
                           buttons=[dict(label='Log Scale',
                                         method='relayout',
                                         args=[{'yaxis.type': 'log'}]),
                                    dict(label='Linear Scale',
                                         method='relayout',
                                         args=[{'yaxis.type': 'linear'}]),
                                    ]
                           )

        updatemenu = [x_axis_menu, y_axis_menu]
        if have_2nd_yaxis:
            y_axis2_menu = dict(active=1,
                                x=0.5,
                                xanchor='left',
                                y=button_layer_height,
                                yanchor='top',
                                buttons=[dict(label='Log Scale',
                                              method='relayout',
                                              args=[{'yaxis2.type': 'log'}]),
                                         dict(label='Linear Scale',
                                              method='relayout',
                                              args=[{'yaxis2.type': 'linear'}]),
                                         ]
                                )
            updatemenu.append(y_axis2_menu)

        x_menu_annotation = dict(text="X axis",
                                 x=0.0,
                                 y=button_layer_height - 0.02,
                                 xref='paper',
                                 yref='paper',
                                 showarrow=False)
        y_menu_annotation = dict(text="Y axis",
                                 x=0.2,
                                 y=button_layer_height - 0.02,
                                 xref='paper',
                                 yref='paper',
                                 showarrow=False)
        annotations = [x_menu_annotation, y_menu_annotation]
        if have_2nd_yaxis:
            y2_menu_annotation = dict(text="2nd Y axis",
                                      x=0.45,
                                      y=button_layer_height - 0.02,
                                      xref='paper',
                                      yref='paper',
                                      showarrow=False)
            annotations.append(y2_menu_annotation)
        return updatemenu, annotations

    def export_fig_as_html(self, fig: go.Figure, filename: str) -> str:
        fig.write_html(filename)
        return f'Exported to {filename}'

    def export_fig_as_image(self, fig: go.Figure, filename: str):
        fig.write_image(filename)
        return f'Exported to {filename}'
