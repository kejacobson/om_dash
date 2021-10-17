import argparse
from om_dash.recorder_parser import RecorderParser


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('recorder_filename', type=str, help='OpenMDAO recorder filename (.sql file)')
parser.add_argument('--tecplot_filename', type=str, default='{recorder_root}.dat',
                    help='Filename to write to tecplot.')
args = parser.parse_args()

recorder_filename = args.recorder_filename
parser = RecorderParser(recorder_filename)

tecplot_filename = args.tecplot_filename
if 'recorder_root' in tecplot_filename:
    recorder_root = recorder_filename.split('.sql')[0]
    tecplot_filename = f'{recorder_root}.dat'


parser.write_data_to_tecplot(tecplot_filename)
