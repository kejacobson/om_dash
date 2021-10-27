"""
This script will read the sql file from an OpenMDAO recorder and write a tecplot
.dat file or csv file with the history of the optimization.
"""

import argparse
from om_dash.recorder_parser import RecorderParser


def write_data_to_file(parser: RecorderParser, filename: str):
    ext = filename.split('.')[-1]
    if ext == 'dat':
        parser.write_data_to_tecplot(filename)
    else:
        data = parser.get_dataframe_of_all_data()
        data.to_csv(filename)


def main():
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         description=__doc__)
    arg_parser.add_argument('recorder_filename', type=str,
                            help='OpenMDAO recorder filename (.sql file)')
    arg_parser.add_argument(
        '-o', '--output', type=str, default='{recorder_root}.dat',
        help='Filename to write. Should have a ".dat" file extension for tecplot or ".csv" for comma separated values.')
    args = arg_parser.parse_args()

    recorder_filename = args.recorder_filename
    om_parser = RecorderParser(recorder_filename)

    outfile = args.output
    if 'recorder_root' in outfile:
        recorder_root = recorder_filename.split('.sql')[0]
        outfile = f'{recorder_root}.dat'
    write_data_to_file(om_parser, outfile)


if __name__ == '__main__':
    main()
