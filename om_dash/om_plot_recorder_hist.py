"""
This script will read the sql file from an OpenMDAO recorder and use plotly
to write an html or image of the optimization history.
"""

import argparse
from om_dash.recorder_parser import RecorderParser
from om_dash.opt_hist_figure_generator import OptHistoryFigureGenerator


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)
    parser.add_argument('recorder_filename', type=str,
                        help='OpenMDAO recorder filename (.sql file)')
    parser.add_argument('-o', '--output', type=str, default='{recorder_root}.html',
                        help='Filename to write to image or html.')
    args = parser.parse_args()

    recorder_filename: str = args.recorder_filename
    parser = RecorderParser(recorder_filename)

    outfile = args.output
    if 'recorder_root' in outfile:
        recorder_root = recorder_filename.split('.sql')[0]
        outfile = f'{recorder_root}.html'

    write_html = True if outfile.split('.')[-1] == 'html' else False

    fig_gen = OptHistoryFigureGenerator(parser)
    fig = fig_gen.create_figure(add_update_menus=write_html)

    if write_html:
        fig.write_html(outfile)
    else:
        fig.write_image(outfile)


if __name__ == '__main__':
    main()
