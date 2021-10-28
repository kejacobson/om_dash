"""
This script will read the sql file from an OpenMDAO recorder(s) and use plotly
to write an html or image of the optimization history. If multiple record files are provided,
the histories will be concatenated and a single plot will be generated.
"""

import argparse
from om_dash.recorder_history_stacker import RecorderHistoryStacker
from om_dash.opt_hist_figure_generator import OptHistoryFigureGenerator
from om_dash.om_convert_recorder_hist import set_output_file_name


def main():
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         description=__doc__)
    arg_parser.add_argument('-i', '--inputs', nargs='+', type=str,
                            help='OpenMDAO recorder filenames (.sql file)')
    arg_parser.add_argument('-o', '--output', type=str, default='{first_recorder_root}.html',
                            help='Filename to write to image or html.')
    args = arg_parser.parse_args()

    outfile = set_output_file_name(args.inputs, args.output, 'html')

    om_parser = RecorderHistoryStacker(args.inputs)
    fig_gen = OptHistoryFigureGenerator(om_parser)

    write_html = (outfile.split('.')[-1] == 'html')
    fig = fig_gen.create_figure(add_update_menus=write_html)
    if write_html:
        fig.write_html(outfile)
    else:
        fig.write_image(outfile)


if __name__ == '__main__':
    main()
