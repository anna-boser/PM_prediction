#####################################################################################

#DO NOT RUN UNLESS YOU WANT TO FORFEIT YOUR RAM FOR THE NEXT FEW DAYS (BAD CODE)!!!

#####################################################################################
import pandas as pd
import numpy as np

header = np.array(["country_cd","region_cd","tribal_code","facility_id","unit_id","rel_point_id","process_id","agy_facility_id","agy_unit_id","agy_rel_point_id","agy_process_id","scc","poll","ann_value","ann_pct_red","facility_name","erptype","stkhgt","stkdiam","stktemp","stkflow","stkvel","naics","longitude","latitude","ll_datum","horiz_coll_mthd","design_capacity","design_capacity_units","reg_codes","fac_source_type","unit_type_code","control_ids","control_measures","current_cost","cumulative_cost","projection_factor","submitter_id","calc_method","data_set_id","facil_category_code","oris_facility_code","oris_boiler_id","ipm_yn","calc_year","date_updated","fug_height","fug_width_xdim","fug_length_ydim","fug_angle","zipcode","annual_avg_hours_per_year","jan_value","feb_value","mar_value","apr_value","may_value","jun_value","jul_value","aug_value","sep_value","oct_value","nov_value","dec_value","jan_pctred","feb_pctred","mar_pctred","apr_pctred","may_pctred","jun_pctred","jul_pctred","aug_pctred","sep_pctred","oct_pctred","nov_pctred","dec_pctred","comment"])[np.newaxis]
cropped_data = header

for i in range(6):

    #read the point data csv file
    if i == 0:
        print(i)
        d= pd.read_csv('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data\\extracted_data\\2017NEI_point_full_20200428\\SmokeFlatFile_POINT_20200412.csv',skiprows=12,nrows=1500000,low_memory=False)
    if i == 1:
        print(i)
        try:
            d= pd.read_csv('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data\\extracted_data\\2017NEI_point_full_20200428\\SmokeFlatFile_POINT_20200412.csv',skiprows=1500012,nrows=1500000,low_memory=False)
        except:
            print("failed 1")
    if i == 2:
        print(i)
        try:
            d= pd.read_csv('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data\\extracted_data\\2017NEI_point_full_20200428\\SmokeFlatFile_POINT_20200412.csv',skiprows=3000012,nrows=1500000,low_memory=False)
        except:
            print("failed 2")
    if i == 3:
        print(i)
        try:
            d= pd.read_csv('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data\\extracted_data\\2017NEI_point_full_20200428\\SmokeFlatFile_POINT_20200412.csv',skiprows=4500012,nrows=1500000,low_memory=False)
        except:
            print("failed 3")
    if i == 4:
        print(i)
        try:
            d= pd.read_csv('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data\\extracted_data\\2017NEI_point_full_20200428\\SmokeFlatFile_POINT_20200412.csv',skiprows=7000012,nrows=1000000,low_memory=False)
        except:
            print("failed 4")
    if i == 5:
        print(i)
        try:
            d= pd.read_csv('C:\\Users\\phili\\Documents\\Anna-Project\\Data\\EPA_Data\\extracted_data\\2017NEI_point_full_20200428\\SmokeFlatFile_POINT_20200412.csv',skiprows=8000012,low_memory=False)
        except:
            print("failed 5")
                

    #header data gets cut off for some reason so I just added it back in here (dumb way to do it but it works :D)
    point_data = np.array(d)

    lat_min = 36.8
    lat_max = 39
    long_min = -123.5
    long_max = -120.8

    for i in point_data:
        if lat_max > i[24] > lat_min and long_max > i[23] > long_min:
            j = np.reshape(i,(1,77))
            cropped_data = np.concatenate((cropped_data,j),axis=0)

    #np.savetxt("foo.csv", cropped_data, delimiter=",")


pd.DataFrame(cropped_data).to_csv("C:\\Users\\phili\\Documents\\Anna-Project\\PM_prediction\\Data\\NEI\\cropped_point_NEI.csv")
#print(data_out)