import os
import argparse
import numpy as np
from pathlib import Path

from pythonnet import load
load("coreclr")

import clr

clr.AddReference("ChaosSoft")
from ChaosSoft.NumericalMethods.Lyapunov import LleWolf

# Description of arguments
#
# -d / --e_dim            Determines the number of dimensions in the reconstructed phase space, 
#                         representing how many past values of the time series are used.
#
# -t / --tau              Specifies the time lag between points used in the reconstruction of the phase space, 
#                         ensuring independence between neighboring points.
#          
# -l / --dt               Represents the time interval between successive points in the time series, 
#                         used for time-related calculations.
#
# -m / --eps_min          Sets the minimum distance threshold for defining neighborhood points in the reconstructed 
#                         phase space, ensuring points closer than this threshold are not considered neighbors.
#
# -s / --eps_max          Sets the maximum distance threshold for defining neighborhood points, ensuring points 
#                         farther than this threshold are not considered neighbors.
#
# -v / --evolv            Determines the number of steps the system evolves in time during the Lyapunov exponent calculation, 
#                         influencing the accuracy of the result and computational requirements.
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
        prog='LLE by Wolf',
        description='Calculates the Largest lyapunov exponent of a time series using Wolf\'s algorithm',
    )

    # eDim (Embedding Dimension): .
    # tau (Reconstruction Time Delay): .
    # dt (Series Time Step): .
    # epsMin (Minimum Scale): .
    # epsMax (Maximum Scale): .
    # evolv (Evolution Steps): .

    parser.add_argument(
      '-d', '--e_dim', 
      type=int, help='Number of dimensions in reconstructed phase space',
      default=2
    )
    parser.add_argument(
      '-t', '--tau', 
      type=int, help='Time lag between points for reconstruction',
      default=1
    )
    parser.add_argument(
      '-l', '--dt', 
      type=float, help='Time interval between successive points in series',
      default=1.0
    )
    parser.add_argument(
      '-m', '--eps_min', 
      type=float, help='Minimum distance for defining neighbors',
      default=0.0
    )
    parser.add_argument(
      '-s', '--eps_max', 
      type=float, help='Maximum distance for defining neighbors',
      default=0.0
    )
    parser.add_argument(
      '-v', '--evolv', 
      type=int, help='Number of evolution steps in Lyapunov calculation',
      default=1
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
        args.output = os.path.join('LLE', 'wolf')

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

      lle = LleWolf(args.e_dim, args.tau, args.dt, args.eps_min, args.eps_max, args.evolv)
      lle.Calculate(series)

      print(lle.ToString())
      print(lle.GetResultAsString())

      stem = Path(file_path).stem
      dirname = os.path.dirname(file_path)
      new_file_name = f'{stem}.txt'
      output_dir = os.path.join(dirname, args.output)
      if not os.path.exists(output_dir):
          os.makedirs(output_dir, exist_ok=True)
      with open(os.path.join(output_dir, new_file_name), 'w') as f:
          result = float(lle.Result)
          f.write(f'{result}')
