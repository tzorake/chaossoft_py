setlocal enabledelayedexpansion

call .\venv\Scripts\activate

python batching.py -F ".\txt" -w "les_sano_sawada.py" -a "-c 1 -a 7000 -p 10000 -d 4"
python batching.py -F ".\txt" -w "lle_kantz.py" -a "-c 1 -a 7000 -p 10000"
python batching.py -F ".\txt" -w "lle_rosenstein.py" -a "-c 1 -a 7000 -p 10000"
python batching.py -F ".\txt" -w "lle_wolf.py" -a "-c 1 -a 7000 -p 10000"

deactivate
pause