## Brian Blaylock

## June 26, 2020
import os
import re
import datetime as d
from datetime import datetime, timedelta

import numpy as np
import urllib.request  # Used to download the file
import requests        # Used to check if a URL exists
import warnings
import pandas as pd    # Just used for the date_range function

def reporthook(a, b, c):
    """
    Report download progress in megabytes (prints progress to screen).
    
    Parameters
    ----------
    a : Chunk number
    b : Maximum chunk size
    c : Total size of the download
    """
    chunk_progress = a * b / c * 100
    total_size_MB =  c / 1000000.
    print(f"\r Download Progress: {chunk_progress:.2f}% of {total_size_MB:.1f} MB\r", end='')

def download_HRRR_subset(url, searchString, SAVEDIR='./', dryrun=False):
    """
    Download a subset of GRIB fields from a HRRR file.
    
    This assumes there is an index (.idx) file available for the file.
    
    Parameters
    ----------
    url : string
        The URL for the HRRR file you are trying to download. There must be an 
        index file for the GRIB2 file. For example, if 
        ``url='https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2'``,
        then ``https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2.idx``
        must also exist on the server.
    searchString : str
        The string you are looking for in each line of the index file. 
        Take a look at the 
        .idx file at https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2.idx
        to get familiar with what is in each line.
        Also look at this webpage: http://hrrr.chpc.utah.edu/HRRR_archive/hrrr_sfc_table_f00-f01.html
        for additional details.**You should focus on the variable and level 
        field for your searches**.
        
        You may use regular expression syntax to customize your search. 
        Check out this regulare expression cheatsheet:
        https://link.medium.com/7rxduD2e06
        
        Here are a few examples that can help you get started
        
        ================ ===============================================
        ``searchString`` Messages that will be downloaded
        ================ ===============================================
        ':TMP:2 m'       Temperature at 2 m.
        ':TMP:'          Temperature fields at all levels.
        ':500 mb:'       All variables on the 500 mb level.
        ':APCP:'         All accumulated precipitation fields.
        ':UGRD:10 m:'    U wind component at 10 meters.
        ':(U|V)GRD:'     U and V wind component at all levels.
        ':.GRD:'         (Same as above)
        ':(TMP|DPT):'    Temperature and Dew Point for all levels .
        ':(TMP|DPT|RH):' TMP, DPT, and Relative Humidity for all levels.
        ':REFC:'         Composite Reflectivity
        ':surface:'      All variables at the surface.
        ================ ===============================================    
        
    SAVEDIR : string
        Directory path to save the file, default is the current directory.
    dryrun : bool
        If True, do not actually download, but print out what the function will
        attempt to do.
    
    Returns
    -------
    The path and name of the new file.
    """
    # Ping Pando first. This *might* prevent a "bad handshake" error.
    if 'pando' in url:
        try:
            requests.head('https://pando-rgw01.chpc.utah.edu/')
        except:
            print('bad handshake...am I able to on?')
            pass
    
    # Make SAVEDIR if path doesn't exist
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
        print(f'Created directory: {SAVEDIR}')

    
    # Make a request for the .idx file for the above URL
    idx = url + '.idx'
    r = requests.get(idx)

    # Check that the file exists. If there isn't an index, you will get a 404 error.
    if not r.ok: 
        print('❌ SORRY! Status Code:', r.status_code, r.reason)
        print(f'❌ It does not look like the index file exists: {idx}')

    # Read the text lines of the request
    lines = r.text.split('\n')
    
    # Search expression
    expr = re.compile(searchString)

    # Store the byte ranges in a dictionary
    #     {byte-range-as-string: line}
    byte_ranges = {}
    for n, line in enumerate(lines, start=1):
        # n is the line number (starting from 1) so that when we call for 
        # `lines[n]` it will give us the next line. (Clear as mud??)

        # Use the compiled regular expression to search the line
        if expr.search(line):   
            # aka, if the line contains the string we are looking for...

            # Get the beginning byte in the line we found
            parts = line.split(':')
            rangestart = int(parts[1])

            # Get the beginning byte in the next line...
            if n+1 < len(lines):
                # ...if there is a next line
                parts = lines[n].split(':')
                rangeend = int(parts[1])
            else:
                # ...if there isn't a next line, then go to the end of the file.
                rangeend = ''

            # Store the byte-range string in our dictionary, 
            # and keep the line information too so we can refer back to it.
            byte_ranges[f'{rangestart}-{rangeend}'] = line
    
    # What should we name the file we save this data to?
    # Let's name it something like `subset_20200624_hrrr.t01z.wrfsfcf17.grib2`
    runDate = list(byte_ranges.items())[0][1].split(':')[2][2:-2]
    outFile = '_'.join(['subset', runDate, url.split('/')[-1]])
    outFile = os.path.join(SAVEDIR, outFile)
    
    for i, (byteRange, line) in enumerate(byte_ranges.items()):
        
        if i == 0:
            # If we are working on the first item, overwrite the existing file.
            curl = f'curl -s --range {byteRange} {url} > {outFile}'
        else:
            # If we are working on not the first item, append the existing file.
            curl = f'curl -s --range {byteRange} {url} >> {outFile}'
            
        num, byte, date, var, level, forecast = line.split(':')
        
        if dryrun:
            print(f'    🐫 Dry Run: Found GRIB line [{num:>3}]: variable={var}, level={level}, forecast={forecast}')
            #print(f'    🐫 Dry Run: `{curl}`')
        else:
            print(f'  Downloading GRIB line [{num:>3}]: variable={var}, level={level}, forecast={forecast}')    
            os.system(curl)
    
    if dryrun:
        print(f'🌵 Dry Run: Success! Searched for [{searchString}] and found [{len(byte_ranges)}] GRIB fields. Would save as {outFile}')
    else:
        print(f'✅ Success! Searched for [{searchString}] and got [{len(byte_ranges)}] GRIB fields and saved as {outFile}')
    
        return outFile
    
def download_HRRR(DATES, fxx, searchString, model,
                  field, SOURCE, SAVEDIR,
                  dryrun):
    """
    Downloads full HRRR grib2 files for a list of dates and forecasts.
    
    Files are downloaded from the University of Utah HRRR archive (Pando) 
    or NOAA Operational Model Archive and Distribution System (NOMADS).
    
    Parameters
    ----------
    DATES : datetime or list of datetimes
        A datetime or list of datetimes that represent the model 
        initialization time for which you want to download.
    fxx : int or list of ints
        Forecast lead time or list of forecast lead times to download.
        Default only grabs analysis hour (f00), but you might want all
        the forecasts hours, in that case, you could set ``fxx=range(0,19)``.
    searchString : str
        The string that describes the variables you want to download
        from the file. This is used as the `searchString` in
        ``download_hrrr_subset`` to looking for sepecific byte ranges
        from the file to download. 
        
        Default is None, meaning to not search for variables, but to
        download the full file. ':' is an alias for None, becuase
        it is equivalent to identifying every line in the .idx file.
        Read the details below for more help on defining a suitable 
        ``searchString``.
        
        Take a look at the .idx file at 
        https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2.idx
        to get familiar with what an index file is.
        Also look at this webpage: http://hrrr.chpc.utah.edu/HRRR_archive/hrrr_sfc_table_f00-f01.html
        for additional details.**You should focus on the variable and level 
        field for your searches**.
        
        You may use regular expression syntax to customize your search. 
        Check out this regulare expression cheatsheet:
        https://link.medium.com/7rxduD2e06
        
        Here are a few examples that can help you get started
        
        ================ ===============================================
        ``searchString`` Messages that will be downloaded
        ================ ===============================================
        ':TMP:2 m'       Temperature at 2 m.
        ':TMP:'          Temperature fields at all levels.
        ':500 mb:'       All variables on the 500 mb level.
        ':APCP:'         All accumulated precipitation fields.
        ':UGRD:10 m:'    U wind component at 10 meters.
        ':(U|V)GRD:'     U and V wind component at all levels.
        ':.GRD:'         (Same as above)
        ':(TMP|DPT):'    Temperature and Dew Point for all levels .
        ':(TMP|DPT|RH):' TMP, DPT, and Relative Humidity for all levels.
        ':REFC:'         Composite Reflectivity
        ':surface:'      All variables at the surface.
        ================ =============================================== 
    model : {'hrrr', 'hrrrak', 'hrrrX'}
        The model type you want to download.
        - 'hrrr' HRRR Contiguous United States (operational)
        - 'hrrrak' HRRR Alaska. You can also use 'alaska' as an alias.
        - 'hrrrX' HRRR *experimental*
    field : {'prs', 'sfc', 'nat', 'subh'}
        Variable fields you wish to download. 
        - 'sfc' surface fields
        - 'prs' pressure fields
        - 'nat' native fields      ('nat' files are not available on Pando)
        - 'subh' subhourly fields  ('subh' files are not available on Pando)
    SOURCE : {'pando', 'nomads'}
        Specify the source from which to download the HRRR files.
        - 'pando' downloads HRRR files from University of Utah archive:
        http://hrrr.chpc.utah.edu/        
        - 'nomads' downloads HRRR files from NCEP NOMADS server:
        https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/
    SAVEDIR : str
        Directory path to save the downloaded HRRR files.
    dryrun : bool
        If True, instead of downloading the files, it will print out the
        files that could be downloaded. This is set to False by default.

    Returns
    -------
    Downloads the HRRR files, with filename prepended with the run date
    (i.e. `20170101_hrrr.t00z.wrfsfcf00.grib2`)
    """
    
    #**************************************************************************
    ## Check function input
    #**************************************************************************
    
    # Ping Pando first. This *might* prevent a "bad handshake" error.
    if SOURCE == 'pando':
        try:
            requests.head('https://pando-rgw01.chpc.utah.edu/')
        except:
            print('bad handshake...am I able to on?')
            pass
    
    # Force the `SOURCE` and `field` input string to be lower case.
    SOURCE = SOURCE.lower()
    field = field.lower()

    # `DATES` and `fxx` should be a list-like object, but if it doesn't have
    # length, (like if the user requests a single date or forecast hour),
    # then turn it item into a list-like object.
    if not hasattr(DATES, '__len__'): DATES = np.array([DATES])
    if not hasattr(fxx, '__len__'): fxx = [fxx]
    
    # HRRR data on NOMADS is only available for today's and yesterday's runs.
    # If any of the DATES are older than yesterday, raise a warning and
    # change SOURCE to pando.
    if SOURCE == 'nomads':
        yesterday = datetime.utcnow() - timedelta(days=1)
        yesterday = datetime(yesterday.year, yesterday.month, yesterday.day)
        if any(DATES < yesterday):
            warnings.warn("Changed the SOURCE to 'pando' because one or more of the requested DATES are for more than two days ago.")
            SOURCE = 'pando'
    
    # The user may set `model='alaska'` as an alias for 'hrrrak'.
    if model.lower() == 'alaska': model = 'hrrrak'
      
    _SOURCE = {'pando', 'nomads'}
    assert SOURCE in _SOURCE, f'`SOURCE` must be one of {_SOURCE}'
    
    # The model type and field depends on the SOURCE the files are downloaded.
    if SOURCE == 'pando':
        _models = {'hrrr', 'hrrrak', 'hrrrX'}
        _fields = {'sfc', 'prs'}
    elif SOURCE == 'nomads':
        _models = {'hrrr', 'hrrrak'}
        _fields = {'sfc', 'prs', 'nat', 'subh'}
        
    assert model in _models, f'`model` should be set to one of {_models} for `SOURCE={SOURCE}`'
    assert field in _fields, f'`field` should be set to one of {_fields} for `SOURCE={SOURCE}`'
    
    # Make SAVEDIR if path doesn't exist
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
        print(f'Created directory: {SAVEDIR}')

    #**************************************************************************
    # Build the URL path for every file we want
    #**************************************************************************
    # An example URL for a file from Pando is 
    # https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2
    # 
    # An example URL for a file from NOMADS is
    # https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.20200624/conus/hrrr.t00z.wrfsfcf09.grib2
        
    if SOURCE == 'pando':
        base = f'https://pando-rgw01.chpc.utah.edu/{model}/{field}'
        URL_list = [f'{base}/{DATE:%Y%m%d}/{model}.t{DATE:%H}z.wrf{field}f{f:02d}.grib2' for DATE in DATES for f in fxx]
    
    elif SOURCE == 'nomads':
        base = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod'
        if model == 'hrrr':
            URL_list = [f'{base}/hrrr.{DATE:%Y%m%d}/conus/hrrr.t{DATE:%H}z.wrf{field}f{f:02d}.grib2' for DATE in DATES for f in fxx]
        elif model == 'hrrrak':
            URL_list = [f'{base}/hrrr.{DATE:%Y%m%d}/alaska/hrrr.t{DATE:%H}z.wrf{field}f{f:02d}.ak.grib2' for DATE in DATES for f in fxx]
    
    #**************************************************************************
    # Ok, so we have a URL and filename for each requested forecast hour.
    # Now we need to check if each of those files exist, and if it does,
    # we will download that file to the SAVEDIR location.
    
    if dryrun:
        print(f'🌵 Info: Dry Run {len(URL_list)} GRIB2 files')
    else:
        print(f'💡 Info: Downloading {len(URL_list)} GRIB2 files')
    
    for file_URL in URL_list:
        # We want to prepend the filename with the run date, YYYYMMDD
        if SOURCE == 'pando':
            outFile = '_'.join(file_URL.split('/')[-2:])
            outFile = os.path.join(SAVEDIR, outFile)
        elif SOURCE == 'nomads':
            outFile = file_URL.split('/')[-3][5:] + '_' + file_URL.split('/')[-1]
            outFile = os.path.join(SAVEDIR, outFile)
        
        # Check if the URL returns a status code of 200 (meaning the URL is ok)
        # Also check that the Content-Length is >1000000 bytes (if it's smaller,
        # the file on the server might be incomplete)
        head = requests.head(file_URL)
        
        check_exists = head.ok
        check_content = int(head.raw.info()['Content-Length']) > 1000000
        
        if check_exists and check_content:
            # Download the file
            if searchString in [None, ':']:
                if dryrun:
                    print(f'🌵 Dry Run Success! Would have downloaded {file_URL} as {outFile}')
                else:
                    # Download the full file.
                    urllib.request.urlretrieve(file_URL, outFile, reporthook)
                print(f'✅ Success! Downloaded {file_URL} as {outFile}')
            else:
                # Download a subset of the full file based on the seachString.
                download_HRRR_subset(file_URL, searchString, 
                                     SAVEDIR=SAVEDIR, dryrun=dryrun)
        else:
            # The URL request is bad. If status code == 404, the URL does not exist.
            print()
            print(f'❌ WARNING: Status code {head.status_code}: {head.reason}. Content-Length: {int(head.raw.info()["Content-Length"]):,} bytes')
            print(f'❌ Could not download {head.url}')
    
    print("\nFinished 🍦")
    
#edited: Add main function
if __name__ == '__main__':
    #Specify the dates you want to include (year, month, day, hour), excludes end date
    start_date = datetime(2017, 1, 1, 21)
    end_date   = datetime(2018, 1, 1, 21)

    date_range = [start_date + d.timedelta(n) for n in range(int ((end_date - start_date).days))]
    
    # Example downloads all analysis hours for a single day.

    # -------------------------------------------------------------------------
    # --- Settings: Check online documentation for available dates and hours --
    # -------------------------------------------------------------------------
    # Start and End Date
    # input variable code to pull from full files
    ss = ':HPBL:'
    # Model Type: options include 'hrrr', 'hrrrX', 'hrrrak'
    model_type = 'hrrr'

    # Variable field: options include 'sfc' or 'prs'
    # (if you want to initialize WRF with HRRR, you'll need the prs files)
    var_type = 'sfc'

    #Specify which hours to download
    #(this example downloads all hours)
    # if model_type == 'hrrrak':
    #     # HRRR Alaska run every 3 hours at [0, 3, 6, 9, 12, 15, 18, 21] UTC
    #     hours = range(0, 24, 3)
    # else:
    #     hours = range(21, 22)
    # Specify which forecasts hours to download. Most can be range(19) for hrrr.
    # (this example downloads the analysis hours, f00)
    #forecasts = [0]

    # Specify a Save Directory
    SAVEDIR = r'C:/Users/aboser/Documents/GitHub/PM_prediction/Data/HRRR/'
    
    # -------------------------------------------------------------------------

    # Call the function to download
    download_HRRR(DATES=date_range, fxx=range(0, 1), searchString=ss, 
                  model=model_type, field=var_type,
                  SOURCE='pando', SAVEDIR=SAVEDIR, 
                  dryrun=False)
    
    
    
    
    
    