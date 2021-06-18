# Global Pseudo Code for a program

#standart imports
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#API
import requests
import json

#working with .shp and .gtif
import geopandas as gpd
from osgeo import gdal
from shapely.geometry import Point

# some magic to make geopandas work
#from shapely import speedups
#speedups.disable()

# imports for 3D rendering
from ipywidgets import FloatSlider, FloatRangeSlider, Dropdown, Select, VBox, AppLayout, jslink
from ipygany import Scene, IsoColor, PolyMesh, Component, ColorBar, colormaps

# optional import (not used yet)
# from scipy.spatial import cKDTree
# from shapely.ops import nearest_points

# so, the flow of the program could be as follow:
# 0. Client gives a specific address
# 1. We convert it into coordinates with API
# 2. We found this coordinates in our database as a box plain
# 3. We found the corresponding geotiff and slice a small part related
# 4. We plot this slice into 3D.

# Every of this step should be done in a separate file and then imported here
# like from utils.coordinates import coordinates

# but for now I will just write them down all together

# THIS IS PSEUDO CODE AND IT MIGHT NOT WORK :)

# ===== PART 1 ===== (code is working if you provide proper input)
# ----- Convert an address into coordinates -----

address = input('Please, provide your address in Brussels: ') 
# here we should sanitize input
# for example Wiertz 31 should become => wiertzstraat%2031
# where %20 is a encoding for a space character
api_link = f'http://loc.geopunt.be/geolocation/location?q={address}'
loc_result = requests.get(api_link).json()

# so, API gives you location only if you get the exact name
# of a street and/or house/postcode, otherwise it returns an empty response
# so we could use "geolocation/suggestion" instead of "geolocation/location" query to give hints to the user
# it's also v4/suggestion and v4/location

if len(loc_result['LocationResult']) == 0:
    #print('no results')
    api_guess_link = f'http://loc.geopunt.be/geolocation/suggestion?q={address}'
    guess_result = requests.get(api_guess_link).json()
    #print('this is guess result', guess_result)

# and here we should ask for another input to correct the address
# but I omit this part for now

else: #print('this is locresult', loc_result)
      print('yes')

# Let's assume we got an exact address response.
# So we are extracting coordinates

X_Lambert72 = loc_result['LocationResult'][0]['Location']['X_Lambert72']
Y_Lambert72 = loc_result['LocationResult'][0]['Location']['Y_Lambert72']
#print(X_Lambert72,Y_Lambert72)
#print(type(X_Lambert72),type(Y_Lambert72))
# 150429.1 169626.88 type float

# ===== PART 2 ===== 
# ----- Find coordinates in our database -----

# first we have to create a database of coordinates

point = Point(X_Lambert72, Y_Lambert72)
shape = gpd.read_file('../data/Belgium/Bpn_CaBu.shp', mask=point)
box_coords = shape['geometry'].bounds

##############################
# and here comes pseudo code #
##############################


# ===== PART 3 =====
# ----- Find corresponding geotiff file -----

# we should create a database of geotiffs coordinates as well
# we could you the code from the client
# here it is below as we have it in our repo as a hint
# though we should change it to slice only our house box coordinates
"""
out_path = "../DSM_split/"
output_filename = "tile_"
cpt = 0

# for x in range(1, 44)
for x in range(1, 2):
    tile = f"{x:02d}"
    print(f"Getting map n°{tile}, total tiles : {cpt}")
    in_filename = f"DHMVIIDSMRAS1m_k{tile}.tif"

    in_path = f"./DSM/DHMVIIDSMRAS1m_k{tile}/GeoTIFF/"
    input_fp = in_path + in_filename
    print(input_fp)
    if not path.exists(input_fp):
        raise Exception("Nope")

    tile_size_x = 1000
    tile_size_y = 500

    ds = gdal.Open(input_fp)
    band = ds.GetRasterBand(1)
    xsize = band.XSize
    ysize = band.YSize
    for i in range(0, xsize, tile_size_x):
        for j in range(0, ysize, tile_size_y):
            cpt += 1
            gdal_options = {
                "format": "GTiff",
                "srcWin": [i, j, tile_size_x, tile_size_y]
            }
            gdal.Translate(
                destName=f"{out_path}{output_filename}{cpt}.tif",
                srcDS=f"{input_fp}",
                **gdal_options
            )

"""

# ===== PART 4 =====
# ----- We plot this slice into 2d and 3d -----

# here is Solan's code (working)

"""
def tif_to_arr(fp:str):
    ds = gdal.Open(fp)
    gt = ds.GetGeoTransform()
    projec = ds.GetProjection()
    band = ds.GetRasterBand(1)
    return band.ReadAsArray()

# dsm_array = tif_to_arr("./DSM/DHMVIIDSMRAS1m_k01/GeoTIFF/DHMVIIDSMRAS1m_k01.tif")
# dtm_array = tif_to_arr("DTM/DHMVIIDTMRAS1m_k01/GeoTIFF/DHMVIIDTMRAS1m_k01.tif")
# diff_array = dsm_array - dtm_array
dsm_array = tif_to_arr("split/tile_1748.tif")
render_target = dsm_array

binmask = np.where((render_target >= np.mean(render_target)), render_target, 0)

plt.figure(figsize=(8, 6), dpi=80)
plt.imshow(binmask)

dem =  binmask

# This one is pretty ugly, I should find a way to open the file only once and get gt out of it
ds = gdal.Open("split/tile_1748.tif")
gt = ds.GetGeoTransform()

xres = gt[1]
yres = gt[5]

X = np.arange(gt[0], gt[0] + dem.shape[1]*xres, xres)
Y = np.arange(gt[3], gt[3] + dem.shape[0]*yres, yres)

X, Y = np.meshgrid(X, Y)

# Create triangle indices
nx = binmask.shape[1]
ny = binmask.shape[0]

triangle_indices = np.empty((ny - 1, nx - 1, 2, 3), dtype=int)

r = np.arange(nx * ny).reshape(ny, nx)

triangle_indices[:, :, 0, 0] = r[:-1, :-1]
triangle_indices[:, :, 1, 0] = r[:-1, 1:]
triangle_indices[:, :, 0, 1] = r[:-1, 1:]

triangle_indices[:, :, 1, 1] = r[1:, 1:]
triangle_indices[:, :, :, 2] = r[1:, :-1, None]

triangle_indices.shape = (-1, 3)

# Create vertices
x = np.arange(-5, 5, 10/nx)
y = np.arange(-5, 5, 10/ny)

xx, yy = np.meshgrid(x, y, sparse=True)

vertices = np.empty((ny, nx, 3))
vertices[:, :, 0] = X
vertices[:, :, 1] = Y
vertices[:, :, 2] = dem
vertices = vertices.reshape(nx * ny, 3)

height_component = Component(name='value', array=dem)

mesh = PolyMesh(
    vertices=vertices,
    triangle_indices=triangle_indices,
    data={'height': [height_component]}
)

height_min = np.min(dem)
height_max = np.max(dem)

# Colorize by height
colored_mesh = IsoColor(mesh, input='height', min=height_min, max=height_max)

# Create a slider that will dynamically change the boundaries of the colormap
colormap_slider_range = FloatRangeSlider(value=[height_min, height_max], min=height_min, max=height_max, step=(height_max - height_min) / 100.)

jslink((colored_mesh, 'range'), (colormap_slider_range, 'value'))

# Create a colorbar widget
colorbar = ColorBar(colored_mesh)

# Colormap choice widget
colormap = Dropdown(
    options=colormaps,
    description='colormap:'
)

jslink((colored_mesh, 'colormap'), (colormap, 'index'))


AppLayout(
    left_sidebar=Scene([colored_mesh]),
    right_sidebar=VBox((colormap_slider_range, colormap, colorbar)),
    pane_widths=[2, 0, 1]
)
"""





