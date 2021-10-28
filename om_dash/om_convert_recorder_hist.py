"""
This script will read the sql file from an OpenMDAO recorder and write a tecplot
.dat file or csv file with the history of the optimization.
If multiple record files are provided, the histories will be concatenated and a single file will
be written.
"""

import argparse
from om_dash.recorder_history_stacker import RecorderHistoryStacker
from typing import List


def set_output_file_name(inputs: List[str], output_arg: str, default_ext='dat'):
    if 'recorder_root' in output_arg:
        first_recorder_root = inputs[0].split('.sql')[0]
        output_arg = f'{first_recorder_root}.{default_ext}'
    return output_arg


def write_data_to_file(parser: RecorderHistoryStacker, filename: str):
    ext = filename.split('.')[-1]
    if ext == 'dat':
        parser.write_data_to_tecplot(filename)
    else:
        data = parser.get_dataframe_of_all_data()
        data.to_csv(filename)


def main():
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         description=__doc__)
    arg_parser.add_argument('-i', '--inputs', nargs='+', type=str, required=True,
                            help='OpenMDAO recorder filenames (.sql file)')
    arg_parser.add_argument(
        '-o', '--output', type=str, default='{first_recorder_root}.dat',
        help='Filename to write. Should have a ".dat" file extension for tecplot or ".csv" for comma separated values.')
    args = arg_parser.parse_args()

    om_parser = RecorderHistoryStacker(args.inputs)
    outfile = set_output_file_name(args.inputs, args.output)
    write_data_to_file(om_parser, outfile)


if __name__ == '__main__':
    main()
