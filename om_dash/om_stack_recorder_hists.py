"""
This script will read the sequence of recorder sql files from OpenMDAO and write a single tecplot
.dat file or csv file with the history of the optimization.
"""
import argparse
from om_dash.recorder_history_stacker import RecorderHistoryStacker
from om_dash.om_convert_recorder_hist import write_data_to_file


def main():
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         description=__doc__)
    arg_parser.add_argument('-i', '--inputs', nargs='+', type=str,
                            help='OpenMDAO recorder filenames (.sql file)')
    arg_parser.add_argument(
        '-o', '--output', type=str, default='{first_recorder_root}.dat',
        help='Filename to write. Should have a ".dat" file extension for tecplot or ".csv" for comma separated values.')
    args = arg_parser.parse_args()

    om_parser = RecorderHistoryStacker(args.inputs)
    outfile = args.output
    if 'recorder_root' in outfile:
        first_recorder_root = args.inputs[0].split('.sql')[0]
        outfile = f'{first_recorder_root}.dat'
    write_data_to_file(om_parser, args.output)


if __name__ == '__main__':
    main()
