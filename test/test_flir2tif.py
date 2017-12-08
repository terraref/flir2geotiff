import subprocess
import os, json, shutil,sys
import numpy
import tempfile
from terrautils.metadata import clean_metadata
from terrautils.metadata import get_terraref_metadata

lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)

from terrautils.formats import create_geotiff
from terrautils.spatial import geojson_to_tuples
from flir2geotiff import Get_FLIR

test_id = 'c3c21db1-deb5-481a-8180-ad447f356a95'
path = os.path.join(os.path.dirname(__file__), 'test_flir2tif_doc', test_id)

bin_file = 'test_flir2tif_doc/'+test_id+'_ir.bin'

f = open(path + '_metadata.json', 'rb')
raw_metadata = json.load(f)
f.close()

cleanmetadata = clean_metadata(raw_metadata, "flirIrCamera")

metadata = get_terraref_metadata(cleanmetadata, 'flirIrCamera')


def test_metadata():
    assert 'spatial_metadata' in metadata.keys()

raw_data = numpy.fromfile(bin_file, numpy.dtype('<u2')).reshape([480, 640]).astype('float')
raw_data = numpy.rot90(raw_data, 3)

tc = Get_FLIR.rawData_to_temperature(raw_data, metadata)


def test_temp():
    assert tc.max() < 1800.

gps_bounds = geojson_to_tuples(metadata['spatial_metadata']['flirIrCamera']['bounding_box'])

out_tmp_tiff = os.path.join(tempfile.gettempdir(), test_id.encode('utf8'))

f = open('test_flir2tif_doc/extractor_info.json', 'rb')
extractor_info = json.load(f)
f.close()

create_geotiff(tc, gps_bounds, out_tmp_tiff, None, True, extractor_info, metadata)

shutil.move(out_tmp_tiff, path+'_test_result.tif')


def test_result_file():
    assert os.path.isfile(path + '_test_result.tif')


if __name__ == '__main__':
    subprocess.call(['python -m pytest test_flir2tif.py -p no:cacheprovider'], shell=True)
