#!/usr/bin/python3

import pandas as pd
from glob import glob
from osgeo import gdal
from osgeo import osr

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
    ds = gdal.Open(geotifAddr)
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
    ds = gdal.Open(geotifAddr)
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

if __name__ == "__main__":

    filename = glob('./Baia_do_Guajara/*.txt')
    columns = ['LAT', 'LONG', 'X1']

    # let test on this file
    tiffname = './LC82230612013208LGN00/LC82230612013208LGN00_B2.TIF'

    # automaticaly generate files with lat_dec and long_dec
    for name in filename:
        _temp = pd.read_csv(name, sep=',', usecols=[0,1,2], names=columns)
        _temp['LAT DEC'] = convert2dec(_temp['LAT'])
        _temp['LONG DEC'] = convert2dec(_temp['LONG'])
        _temp.to_csv(name.split('-')[-1], sep=',', index=False)

    # 'I.txt' is a file generated by the loop above ^
    df = pd.read_csv('I.txt', sep=',')
    latlong = df[['LAT DEC', 'LONG DEC']]

    copy = latlong.copy()

    pixelpair = latLon2Pixel(tiffname, copy.copy().values)
    # making the inverse
    latlongpair = pixel2LatLon(tiffname, pixelpair)
