"""
This script will read the file that captured the screen output from an OpenMDAO optimization and
create a plotly plot showing the convergence of the NLBGS and/or the LNBGS solvers.
"""
import os
import argparse
from typing import List
import numpy as np
import plotly.graph_objects as go

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
    arg_parser.set_defaults(nlbgs=True, lnbgs=True)

    return arg_parser


def grep_for_bgs_residuals_in_file(filename: str, doing_nlbgs: bool):
    prefix = 'NL: NLBGS' if doing_nlbgs else 'LN: LNBGS'
    return os.popen(f'grep -E "{prefix} [0-9]" {filename}').read().split('\n')[:-1]


def split_line_into_residual_data(line: str, nlbgs: bool):
    key = 'NLBGS' if nlbgs else 'LNBGS'
    iteration = int(line.split(';')[0].split(key)[-1])
    abs_resid = float(line.split(';')[-1].split(' ')[1])
    rel_resid = float(line.split(';')[-1].split(' ')[2])
    return iteration, abs_resid, rel_resid


def get_residual_data_from_lines(lines: List[str], doing_nlbgs: bool) -> List[np.ndarray]:
    all_data = []
    current_solve = []
    start_iteration = 1 if doing_nlbgs else 0
    for line in lines:
        iteration, abs_resid, rel_resid = split_line_into_residual_data(line, doing_nlbgs)
        if iteration == start_iteration and len(current_solve) > 0:
            all_data.append(np.array(current_solve))
            current_solve = []
        current_solve.append([iteration, abs_resid, rel_resid])

    # append the last solve
    all_data.append(np.array(current_solve))
    return all_data


def set_output_file_name(input: str, default_ext: str, bgs: str) -> str:
    input_root = os.path.splitext(input)[0]
    output_arg = f'{input_root}_{bgs}.{default_ext}'
    return output_arg


def set_figure_settings(add_update_menus: bool):
    base = PlotlyBase()
    fig = go.Figure()
    xaxis, yaxis = base.get_axis_settings()
    xaxis['title'] = 'Iteration'
    yaxis['title'] = 'Residual'
    base.set_default_figure_layout(fig, xaxis, yaxis, add_update_menus=add_update_menus)
    return fig


def plot_residual_data(all_data: List[np.ndarray], input_filename: str, doing_nlbgs: bool):
    bgs = 'nlbgs' if doing_nlbgs else 'lnbgs'
    outfile = set_output_file_name(input_filename, 'html', bgs)
    write_html = (outfile.split('.')[-1] == 'html')
    start_iteration = 0
    fig = set_figure_settings(write_html)

    for solve, data_set in enumerate(all_data):
        current_num_iterations = data_set.shape[0]
        end_iteration = start_iteration + current_num_iterations
        plot_iterations = np.arange(start_iteration, end_iteration)
        fig.add_trace(go.Scattergl(x=plot_iterations,
                                   y=data_set[:, 1],
                                   mode='lines+markers',
                                   name=f'Solve {solve}: Absolute'))
        fig.add_trace(go.Scattergl(x=plot_iterations,
                                   y=data_set[:, 2],
                                   mode='lines+markers',
                                   name=f'Solve {solve}: Relative',
                                   line=dict(dash='dot')))
        start_iteration += current_num_iterations

    if write_html:
        fig.write_html(outfile)
    else:
        fig.write_image(outfile)


def main():
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    if args.nlbgs:
        doing_nlbgs = True
        lines = grep_for_bgs_residuals_in_file(args.input, doing_nlbgs)
        residual_data = get_residual_data_from_lines(lines, doing_nlbgs)
        plot_residual_data(residual_data, args.input, doing_nlbgs)

    if args.lnbgs:
        doing_nlbgs = False
        lines = grep_for_bgs_residuals_in_file(args.input, doing_nlbgs)
        residual_data = get_residual_data_from_lines(lines, doing_nlbgs)
        plot_residual_data(residual_data, args.input, doing_nlbgs)


if __name__ == '__main__':
    main()
