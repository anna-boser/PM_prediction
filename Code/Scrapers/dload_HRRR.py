# Brian Blaylock
# February 13, 2018

# Updated December 10, 2018 for Python 3

"""
Download archived HRRR files from MesoWest Pando S3 archive system.

Please register before downloading from our HRRR archive:
http://hrrr.chpc.utah.edu/hrrr_download_register.html

For info on the University of Utah HRRR archive and to see what dates are 
available, look here:
http://hrrr.chpc.utah.edu/

Contact:
brian.blaylock@utah.edu
"""

import urllib.request
from datetime import date
import datetime
import time
import os

def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    # ',' at the end of the line is important!
    print("\r % 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.), end='')

def download_HRRR(DATE,
                  model,
                  field,
                  hour,
                  fxx,
                  OUTDIR):
    """
    Downloads from the University of Utah MesoWest HRRR archive
    Input:
        DATE   - A date object for the model run you are downloading from.
        model  - The model type you want to download. Default is 'hrrr'
                 Model Options are ['hrrr', 'hrrrX','hrrrak']
        field  - Variable fields you wish to download. Default is sfc, surface.
                 Options are fields ['prs', 'sfc','subh', 'nat']
        hour   - Range of model run hours. Default grabs all hours of day.
        fxx    - Range of forecast hours. Default grabs analysis hour (f00).
        OUTDIR - Directory to save the files.

    Outcome:
        Downloads the desired HRRR file and renames with date info preceeding
        the original file name (i.e. 20170101_hrrr.t00z.wrfsfcf00.grib2)
    """
    # Make OUTDIR if path doesn't exist
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)

    # Loop through each hour and each forecast and download.
    for h in hour:
        for f in fxx:
            # 1) Build the URL string we want to download.
            #    fname is the file name in the format
            #    [model].t[hh]z.wrf[field]f[xx].grib2
            #    i.e. hrrr.t00z.wrfsfcf00.grib2
            fname = "%s.t%02dz.wrf%sf%02d.grib2" % (model, h, field, f)
            URL = "https://pando-rgw01.chpc.utah.edu/%s/%s/%s/%s" \
                   % (model, field, DATE.strftime('%Y%m%d'), fname)

            # 2) Rename file with date preceeding original filename
            #    i.e. 20170105_hrrr.t00z.wrfsfcf00.grib2
            rename = "%s_%s" \
                     % (DATE.strftime('%Y%m%d'), fname)

            # 3) Download the file via https
            # Check the file size, make it's big enough to exist.         
            check_this = urllib.request.urlopen(URL)
            file_size = int(check_this.info()['content-length'])
            if file_size > 10000:
                print("Downloading:", URL)
                urllib.request.urlretrieve(URL, OUTDIR+rename, reporthook)
                print("\n")
            else:
                # URL returns an "Key does not exist" message
                print("ERROR:", URL, "Does Not Exist")

            # 4) Sleep five seconds, as a courtesy for using the archive.
            time.sleep(5)

if __name__ == '__main__':
    #Specify the dates you want to include (year, month, day), excludes end date
    start_date = date(2017, 1, 1)
    end_date   = date(2018, 1, 1)

    date_range = [ start_date + datetime.timedelta(n) for n in range(int ((end_date - start_date).days))]
    
    for day in date_range:
        # Example downloads all analysis hours for a single day.
    
        # -------------------------------------------------------------------------
        # --- Settings: Check online documentation for available dates and hours --
        # -------------------------------------------------------------------------
        # Start and End Date
        get_this_date = day
    
        # Model Type: options include 'hrrr', 'hrrrX', 'hrrrak'
        model_type = 'hrrr'
    
        # Variable field: options include 'sfc' or 'prs'
        # (if you want to initialize WRF with HRRR, you'll need the prs files)
        var_type = 'sfc'
    
        #Specify which hours to download
        #(this example downloads all hours)
        if model_type == 'hrrrak':
            # HRRR Alaska run every 3 hours at [0, 3, 6, 9, 12, 15, 18, 21] UTC
            hours = range(0, 24, 3)
        else:
            hours = range(21, 22)
        # Specify which forecasts hours to download. Most can be range(19) for hrrr.
        # (this example downloads the analysis hours, f00)
        forecasts = [0]
    
        # Specify a Save Directory
        SAVEDIR = '../../Data/HRRR/'
        
        # -------------------------------------------------------------------------
    
        # Call the function to download
        download_HRRR(get_this_date, model=model_type, field=var_type,
                      hour=hours, fxx=forecasts, OUTDIR=SAVEDIR)