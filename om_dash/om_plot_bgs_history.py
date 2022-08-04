"""
This script will read the file that captured the screen output from an OpenMDAO optimization and
create a plotly plot showing the convergence of the NLBGS and/or the LNBGS solvers.
"""
import os
import argparse
from typing import List
import numpy as np
import plotly.graph_objects as go
from om_dash.bgs_residual_parser import BgsResidualParser

from om_dash.om_convert_recorder_hist import set_output_file_name
from om_dash.plotly_base import PlotlyBase


def create_arg_parser():
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         description=__doc__)
    arg_parser.add_argument('-i', '--input', type=str, required=True,
                            help='captured OpenMDAO screen output')
    arg_parser.add_argument('--nlbgs',
                            action='store_true',
                            dest='confirm',
                            help='Whether to search for NLBGS in the output')
    arg_parser.add_argument('--no-nlbgs', dest='nlbgs', action='store_false')
    arg_parser.add_argument('--lnbgs',
                            action='store_true',
                            dest='confirm',
                            help='Whether to search for LNBGS in the output')
    arg_parser.add_argument('--no-lnbgs', dest='lnbgs', action='store_false')
    arg_parser.add_argument('--absolute',
                            action='store_true',
                            dest='absolute',
                            help='Whether to plot absolute residuals')
    arg_parser.add_argument('--no-absolute', dest='absolute', action='store_false')
    arg_parser.add_argument('--relative',
                            action='store_true',
                            dest='relative',
                            help='Whether to plot relative residuals')
    arg_parser.add_argument('--no-relative', dest='relative', action='store_false')
    arg_parser.set_defaults(nlbgs=True, lnbgs=True, absolute=True, relative=True)

    return arg_parser


def set_output_file_name(input: str, ext: str, doing_nlbgs: bool) -> str:
    bgs = 'nlbgs' if doing_nlbgs else 'lnbgs'
    input_root = os.path.splitext(input)[0]
    output_arg = f'{input_root}_{bgs}.{ext}'
    return output_arg


def set_figure_settings(add_update_menus: bool):
    base = PlotlyBase()
    fig = go.Figure()
    xaxis, yaxis = base.get_axis_settings()
    xaxis['title'] = 'Iteration'
    yaxis['title'] = 'Residual'
    yaxis['type'] = 'log'
    base.set_default_figure_layout(fig, xaxis, yaxis, add_update_menus=add_update_menus)
    return fig


def create_residual_figure(all_data: List[np.ndarray], outfile: str,
                           doing_nlbgs: bool, absolute: bool, relative: bool):
    write_html = (outfile.split('.')[-1] == 'html')
    start_iteration = 0
    fig = set_figure_settings(write_html)

    for solve, data_set in enumerate(all_data):
        current_num_iterations = data_set.shape[0]
        end_iteration = start_iteration + current_num_iterations
        plot_iterations = np.arange(start_iteration, end_iteration)
        if absolute:
            fig.add_trace(go.Scattergl(x=plot_iterations,
                                       y=data_set[:, 1],
                                       mode='lines+markers',
                                       name=f'Solve {solve}: Absolute'))
        if relative:
            fig.add_trace(go.Scattergl(x=plot_iterations,
                                       y=data_set[:, 2],
                                       mode='lines+markers',
                                       name=f'Solve {solve}: Relative'))
        start_iteration += current_num_iterations
    return fig


def write_file(outfile: str, fig: go.Figure):
    write_html = (outfile.split('.')[-1] == 'html')
    if write_html:
        fig.write_html(outfile)
    else:
        fig.write_image(outfile)


def main():
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    parser = BgsResidualParser()
    if args.nlbgs:
        doing_nlbgs = True
        outfile = set_output_file_name(args.input, 'html', doing_nlbgs)
        parser.parse_residuals(args.input, doing_nlbgs)
        fig = create_residual_figure(parser.all_data, outfile, doing_nlbgs,
                                     args.absolute, args.relative)
        write_file(outfile, fig)

    if args.lnbgs:
        doing_nlbgs = False
        parser.parse_residuals(args.input, doing_nlbgs)
        outfile = set_output_file_name(args.input, 'html', doing_nlbgs)
        parser.parse_residuals(args.input, doing_nlbgs)
        fig = create_residual_figure(parser.all_data, outfile, doing_nlbgs,
                                     args.absolute, args.relative)
        write_file(outfile, fig)


if __name__ == '__main__':
    main()
