
import os
import argparse
import math
import numpy as np
from pathlib import Path

from pythonnet import load
load("coreclr")

import clr

clr.AddReference("ChaosSoft")
from ChaosSoft.NumericalMethods.Extensions import DataSeriesUtils
from ChaosSoft.NumericalMethods.Lyapunov import LleRosenstein

# Description of arguments
#
# -d / --e_dim            Determines how many previous states are considered to predict the next state in the phase space.
#
# -t / --tau              Specifies the time gap between consecutive points used in reconstructing the phase space.
#
# -i / --iterations       Controls the number of iterations used to compute the Lyapunov exponent, influencing the accuracy of the result.
#
# -w / --window           Specifies the size of the window around each point where nearby points are excluded to avoid
#                         correlations in the Lyapunov exponent calculation.
#
# -m / --eps_min          Sets the smallest scale to be used in the calculation, ensuring a suitable starting point for the range of scales.
#
# =========================================================================================================
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='LLE by Rosenstein',
        description='Calculates the largest lyapunov exponent of a time series using Rosenstein\'s algorithm',
    )

    parser.add_argument(
        '-d', '--e_dim',
        type=int, help='Previous states for prediction',
        default=2
    )
    parser.add_argument(
        '-t', '--tau',
        type=int, help='Time gap between points in reconstruction',
        default=1
    )
    parser.add_argument(
        '-i', '--iterations',
        type=int, help='Number of Lyapunov exponent iterations',
        default=50
    )
    parser.add_argument(
        '-w', '--window',
        type=int, help='Omission window size',
        default=0
    )
    parser.add_argument(
        '-m', '--eps_min',
        type=float, help='Smallest scale for calculation',
        default=0.0
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
        args.output = os.path.join('LLE', 'rosenstein')

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

        lle = LleRosenstein(args.e_dim, args.tau,
                            args.iterations, args.window, args.eps_min)
        lle.Calculate(series)

        leSectorEnd = DataSeriesUtils.SlopeChangePointIndex(
            lle.Slope, 3, lle.Slope.Amplitude.Y / 30)

        if (leSectorEnd <= 0):
            leSectorEnd = lle.Slope.Length

        slope = math.atan2(lle.Slope.DataPoints[leSectorEnd - 1].Y - lle.Slope.DataPoints[0].Y,
                           lle.Slope.DataPoints[leSectorEnd - 1].X - lle.Slope.DataPoints[0].X)

        print(lle.ToString())
        print(slope)

        stem = Path(file_path).stem
        dirname = os.path.dirname(file_path)
        new_file_name = f'{stem}.txt'
        output_dir = os.path.join(dirname, args.output)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, new_file_name), 'w') as f:
            f.write(f'{slope}')
