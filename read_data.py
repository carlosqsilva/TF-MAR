#!/usr/bin/python3

#Documentação em: http://www.gdal.org/gdal_tutorial.html
#                 http://www.gis.usu.edu/~chrisg/python/2009/lectures/ospy_slides4.pdf

import pandas as pd
from glob import glob
from osgeo import gdal
from osgeo import osr
from gdalconst import *
from skimage import io

def split2float(text, sep='-'):
    return [float(x) for x in text.split(sep)]

def convert2dec(coordinates):
    dec = []
    for x in coordinates:
        grau, minu, seg = split2float(x[:-1])

        if grau >= 0:
            value = (grau + (minu/60) + (seg/3600))*(-1)
            dec.append(value)
        else:
            value = (grau + (minu/60) - (seg/3600))*(-1)
            dec.append(value)

    return dec

def latLon2Pixel(geotifAddr, latLonPairs):
    ds = gdal.Open(geotifAddr, GA_ReadOnly)
    gt = ds.GetGeoTransform()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLong = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLong,srs)
    pixelPairs = []

    for point in latLonPairs:
        (point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
        x = (point[1]-gt[0])/gt[1]
        y = (point[0]-gt[3])/gt[5]
        pixelPairs.append([int(x),int(y)])

    return pixelPairs

def pixel2LatLon(geotifAddr,pixelPairs):
    ds = gdal.Open(geotifAddr, GA_ReadOnly)
    gt = ds.GetGeoTransform()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLong = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srs,srsLatLong)
    latLonPairs = []

    for point in pixelPairs:
        ulon = point[0]*gt[1]+gt[0]
        ulat = point[1]*gt[5]+gt[3]
        (lon,lat,holder) = ct.TransformPoint(ulon,ulat)
        latLonPairs.append([lat,lon])

    return latLonPairs

def tiff_info(geotifAddr):
	dataset = gdal.Open(geotifAddr, GA_ReadOnly)

	print('Driver: ', dataset.GetDriver().ShortName, '/', dataset.GetDriver().LongName)
	print('Size is ',dataset.RasterXSize,'x',dataset.RasterYSize, 'x',dataset.RasterCount)
	print('Projection is ',dataset.GetProjection())
	
	geotransform = dataset.GetGeoTransform()
#    .GeoTransform[0] /* top left x */
#    .GeoTransform[1] /* w-e pixel resolution */
#    .GeoTransform[2] /* 0 */
#    .GeoTransform[3] /* top left y */
#    .GeoTransform[4] /* 0 */
#    .GeoTransform[5] /* n-s pixel resolution (negative value) */
	if geotransform is not None:
		print('Origin = (',geotransform[0], ',',geotransform[3],')')
		print('Pixel Size = (',geotransform[1], ',',geotransform[5],')')

def makeUnique(colOne, colTwo):
    string_values = []
    for one, two in zip(colOne, colTwo):
        string_values.append(str(one)+'_'+str(two))
    return string_values
    
if __name__ == "__main__":

    filename_txt = glob('./Baia_do_Guajara/*.txt')
    filename_tif = glob('./LC82230612013208LGN00/*.TIF')
    columns = ['LAT', 'LONG', 'X1']

    # let test on this file
    tiffname = './LC82230612013208LGN00/LC82230612013208LGN00_B2.TIF'
    tiff_info(tiffname)
    # automaticaly generate files with lat_dec and long_dec
    data_frames = []
    for name in filename_txt:
        _temp = pd.read_csv(name, sep=',', usecols=[0,1,2], names=columns)
        _temp['LAT DEC'] = convert2dec(_temp['LAT'])
        _temp['LONG DEC'] = convert2dec(_temp['LONG'])
        _temp['X1'] = _temp['X1']*(-1)
        _temp['Unique'] = makeUnique(_temp['LAT DEC'], _temp['LONG DEC'])
        _temp.to_csv(name.split('-')[-1], sep=',', index=False)
        data_frames.append(_temp)
    
    total = pd.concat(data_frames, ignore_index=True)
    total = total.groupby(total.Unique).mean()
    total.to_csv('total.csv', sep=',', index=False)
    data_frames = None #release memory
    
    latlong = total[['LAT DEC', 'LONG DEC']]
    pixelpair = latLon2Pixel(tiffname, latlong.copy().values)    
    
    values = dict()
    for tiff in filename_tif:
        image = io.imread(tiff, plugin='tifffile')
        pixel_values = []
        for pixel in pixelpair:
            y, x = pixel
            pixel_values.append(image[x, y])
        colname = tiff.split('_')[-1]
        values[colname] = pixel_values
    
    df = pd.DataFrame(values)
    df.to_csv('pixel_info.csv', sep=',', index=False)