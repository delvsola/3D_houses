from osgeo import gdal
from shapely.geometry import Point
import numpy


def slice_tif(fp: str, ul: Point, lr: Point, pad: float = 5.0) -> numpy.ndarray:
    gdal_options = {
        "destName": "",
        "format": "MEM",
        "projWin": [ul.x-pad, ul.y+pad, lr.x+pad, lr.y-pad]

    }
    ds = gdal.Translate(
        srcDS=fp,
        **gdal_options
    )
    band = ds.GetRasterBand(1)
    return band.ReadAsArray()
