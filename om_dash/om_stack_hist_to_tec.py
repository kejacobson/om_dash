import argparse
from om_dash.recorder_history_stacker import RecorderHistoryStacker


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--inputs', nargs='+', type=str,
                    help='OpenMDAO recorder filenames (.sql file)')
parser.add_argument('-o', '--output', type=str, default='stacked_hist.dat',
                    help='Filename to write to tecplot.')
args = parser.parse_args()

parser = RecorderHistoryStacker(args.inputs)
parser.write_data_to_tecplot(args.output)
