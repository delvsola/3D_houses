from os import path
from osgeo import gdal

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
