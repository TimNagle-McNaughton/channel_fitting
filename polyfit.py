#!/usr/bin/env python
# coding: utf-8

# In[ ]:


### imports
import arcpy
import matplotlib.pyplot as plt

get_ipython().run_line_magic('matplotlib', 'inline')

import glob
import numpy as np
import pandas as pd

print("Imports complete.")


# In[ ]:


### setup

# DEM to extract profiles from
dem = "/channel_fitting/test_dem.tif" 

# put single-profile shapefiles in this folder, preferably with useful names
shapefile_folder = "/channel_fitting/shapefiles/"

# each profile will generate a corresponding X, Y table in this folder
output_table_folder = "/channel_fitting/tables/"

# each profile will be saved as a figure with the fitted line in this folder
output_figure_folder = "/channel_fitting/figures/"

# the name and location of the textfile that will log the final data
output_textfile = "channel_fitting/polyfit_values.csv"

print("Variables set.")


# In[ ]:


### run the stack profile
# check out 3D analyst
arcpy.CheckOutExtension("3D")

# get a list of shapefiles to process
shapefile_list = glob.glob(shapefile_folder + "*.shp")

# loop through each shapefile
for shapefile in shapefile_list:
    # get name
    out_name = arcpy.Describe(shapefile).basename
    
    # save path
    save_path = output_table_folder + out_name  + ".csv"
    
    # run the stack profile
    arcpy.StackProfile_3d(shapefile, profile_targets=dem, out_table=save_path)

# return 3D analyst
arcpy.CheckInExtension("3D")

print("Profile tables generated.")


# In[ ]:


### process the tables
    
# write the header -- WILL OVERWRITE
with open(output_textfile, "w") as output:
    output.write("table, a, b, c, residuals \n")
    
# get a list of all the tables to process
table_list = glob.glob(output_table_folder + "*.csv")

# loop through all the tables
for profile_table in table_list:
    
    # open the table
    table = pd.read_csv(profile_table)
    
    # get x and y
    x_values = table["FIRST_DIST"].tolist() 
    y_values = table["FIRST_Z"].tolist()
    
    second_order_poly_fit = np.polyfit(x_values, y_values, 2, full=True)
    a = second_order_poly_fit[0][0]
    b = second_order_poly_fit[0][1]
    c = second_order_poly_fit[0][2]
    residuals = second_order_poly_fit[1][0]
    equation = "{}x^2 + {}x + {}, residuals = {}".format(round(a, 4), round(b, 2), round(c ,1), round(residuals, 0))

    # write the table values
    with open(output_textfile, "a") as output:
        output.write("{}, {}, {}, {}, {}\n".format(profile_table, a, b, c, residuals))
        
    print("{}\nFit: {}x^2 + {}x + {}".format(profile_table, round(a, 4), round(b, 4), round(c ,4)))
    
    # plot original values
    fig, ax = plt.subplots( nrows=1, ncols=1)
    ax.scatter(x_values, y_values, c="r", s= 5)

    # generate a dummy x series
    x_dummy = np.linspace(0, len(x_values))
    
    # plot the fit
    ax.plot(x_dummy, second_order_poly_fit[0][0]*x_dummy**2 + second_order_poly_fit[0][1]*x_dummy + second_order_poly_fit[0][2], c="k")
    plt.title(equation)
    plt.savefig(output_figure_folder + profile_table[len(output_table_folder):-3] + "png")
    plt.close(fig)

