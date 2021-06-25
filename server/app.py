from flask import Flask, request, Response
import json
from utils.geopunt import geocode
from utils.db import match_geotiff
from utils.shapefile import get_bbox
from utils.raster import slice_tif

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/raster', methods=['GET'])
def get_raster():
    if request.method == 'GET':
        address = request.args.get('address', '')
        address_coord = geocode(address)
        tif_id = match_geotiff(address_coord)
        bbox = get_bbox(address_coord)
        if bbox:
            ul = bbox[0]
            lr = bbox[1]
        else:
            return '', 204
        dsm = slice_tif(f"static/dsm/DHMVIIDSMRAS1m_k{tif_id:02d}.tif", ul, lr)
        dtm = slice_tif(f"static/dtm/DHMVIIDTMRAS1m_k{tif_id:02d}.tif", ul, lr)
        chm = dsm - dtm
        chm_list = chm.tolist()
        return Response(json.dumps(chm_list), mimetype='application/json')

    else:
        return "Bad request", 400


if __name__ == '__main__':
    app.run()
