from pathlib import Path
import os
import argparse
import numpy as np

from pythonnet import load
load("coreclr")

import clr

clr.AddReference("ChaosSoft")
from ChaosSoft.NumericalMethods.Lyapunov import LeSpecSanoSawada

# Description of arguments
#
# -d / --e_dim            Embedding dimension used for phase space reconstruction. This is an integer value that
#                         defines the number of dimensions in which the time series will be reconstructed.
#
# -t / --tau              Delay time for phase space reconstruction. It is an integer value representing the
#                         amount of time to delay in the phase space trajectory.
#
# -i / --iterations       Number of iterations for the algorithm to run. It is an integer value that
#                         specifies how many times the algorithm should be executed.
#
# -m / --eps_min          Minimum epsilon value for the neighborhood search. This is a floating-point number
#                         indicating the smallest distance to be considered when searching for neighbors in the phase space.
#
# -s / --eps_step         Step size for epsilon in the neighborhood search. This floating-point value determines
#                         the increment for epsilon during the neighborhood search process.
#
# -n / --min_neighbors    Minimum number of neighbors required for calculations. This integer value
#                         specifies the least number of neighbors that must be found for the algorithm to perform calculations.
#
# -o / --output           Output file path. This string specifies the path to the file where the results of
#                         the calculations will be saved.
#
# -f / --file             File path to the time series. This string argument provides the path to the input file
#                         containing the time series data.
#
# -F / --folder           Folder path to the time series file(s). This string argument specifies the directory
#                         in where the time series files are located.
#
# -c / --column           Column index of the time series in the file. An integer value indicating which
#                         column in the file contains the time series data.
#
# -a / --xstart           Start row index of the time series in the file. This integer value indicates the row number at
#                         which to start reading the time series data.
#
# -p / --xstop            Stop row index (exclusive) of the time series in the file. This integer specifies
#                         the row number at which to stop reading the time series data (not inclusive).

# py main.py -f "D:\Projects\TsaToolbox\ff985070-a967-41ce-9922-f3cd8cfd9d8d.txt" -c 2 -a 32000 -p 42000 -d 4 -t 4
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Lyapunov Exponent Spectrum',
        description='Calculates the Lyapunov Exponent Spectrum',
    )

    parser.add_argument(
        '-d', '--e_dim',
        type=int, help='Embedding dimension used for phase space reconstruction',
        default=2
    )
    parser.add_argument(
        '-t', '--tau',
        type=int, help='Delay time for phase space reconstruction',
        default=1
    )
    parser.add_argument(
        '-i', '--iterations',
        type=int, help='Number of iterations for the algorithm to run',
        default=0
    )
    parser.add_argument(
        '-m', '--eps_min',
        type=float, help='Minimum epsilon value for the neighborhood search',
        default=0
    )
    parser.add_argument(
        '-s', '--eps_step',
        type=float, help='Step size for epsilon in the neighborhood search',
        default=1.2
    )
    parser.add_argument(
        '-n', '--min_neighbors',
        type=int, help='Minimum number of neighbors required for calculations',
        default=30
    )

    parser.add_argument(
        '-o', '--output',
        type=str, help='Output file path',
        default=None
    )
    parser.add_argument(
        '-f', '--file',
        type=str, help='File path to the time series',
        default=None
    )
    parser.add_argument(
        '-e', '--extension',
        type=str, help='Extension of the time series file',
        default=None
    )
    parser.add_argument(
        '-F', '--folder',
        type=str, help='Folder path to the time series file(s)',
        default=None
    )
    parser.add_argument(
        '-c', '--column',
        type=int, help='Column index of the time series in the file',
        default=1
    )
    parser.add_argument(
        '-a', '--xstart',
        type=int, help='Start row index of the time series in the file',
        default=None
    )
    parser.add_argument(
        '-p', '--xstop',
        type=int, help='Stop row index (exclusive) of the time series in the file',
        default=None
    )

    args = parser.parse_args()

    if args.output is None:
        args.output = os.path.join('LES', 'sano_sawada')

    file_paths = []
    file, extension, folder = args.file, args.extension, args.folder
    start, stop = args.xstart, args.xstop
    if folder and os.path.exists(folder):
        if file and os.path.exists(file_path := os.path.join(folder, file)):
            if os.path.isfile(file_path):
                if not extension:
                    file_paths.append(file_path)
                else:
                    if Path(file_path).suffix == extension:
                        file_paths.append(file_path)
        else:
            for file_entry in os.scandir(folder):
                file_path = file_entry.path
                if os.path.isfile(file_path):
                    if not extension:
                        file_paths.append(file_path)
                    else:
                        if Path(file_path).suffix == extension:
                            file_paths.append(file_path)
    else:
        if file and os.path.exists(file) and os.path.isfile(file):
            if not extension:
                file_paths.append(file)
            else:
                if Path(file).suffix == extension:
                    file_paths.append(file)

    if len(file_paths) == 0:
        raise Exception('No file found!')

    for file_path in file_paths:
        data = np.loadtxt(file_path)
        start = args.xstart
        stop = args.xstop
        series = data[start:stop, args.column]

        lesss = LeSpecSanoSawada(int(args.e_dim), int(args.tau), int(args.iterations), float(
            args.eps_min), float(args.eps_step), int(args.min_neighbors), False)
        lesss.Calculate(series)

        print(lesss.ToString())
        print(lesss.GetResultAsString())

        stem = Path(file_path).stem
        dirname = os.path.dirname(file_path)
        new_file_name = f'{stem}.txt'
        output_dir = os.path.join(dirname, args.output)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, new_file_name), 'w') as f:
            result = map(str, list(lesss.Result))
            f.write('\n'.join(result))
