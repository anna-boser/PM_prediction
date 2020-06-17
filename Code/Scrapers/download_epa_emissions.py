#pulls a load of zip files from the EPA Database
#still need to figure out what they are all about

from ftplib import FTP
import os

ftp = FTP('newftp.epa.gov')
ftp.login()
ftp.cwd('/air/nei/2017/doc/flat_files/')
filenames = ftp.nlst()
print(filenames)

for filename in filenames:
    local_filename = os.path.join('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data', filename) #change to your own filepath
    file = open(local_filename, 'wb')
    try:
        ftp.retrbinary('RETR '+ filename, file.write)
    except:
        print('Failed for: ' + filename)

    file.close()

ftp.quit()
