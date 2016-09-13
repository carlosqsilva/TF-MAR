#!/usr/bin/env python3
from skimage import io
from glob import glob

# caminho completo até a pasta das imagens .TIF
# exemplo:
# c:\home\user\imagens\LT52230612011251CUB01\.TIF
path = '/home/carlos/github/BAIA_GUAJARA/LT52230612011251CUB01/*.TIF'

# substitua os valores abaixo pelos valores desajados
# pixel superior esquerdo: x1, y1
ulp = [1500, 2000]
# pixel inferior direito: x2, y1
brp = [4200, 4000]

x1, y1 = ulp
x2, y2 = brp

for image in glob(path):
    data = io.imread(image, plugin="tifffile")
    data = data[x1:x2, y1:y2]
    print(image)
    print(data.shape)
    name = image.split("\\")[-1]
    io.imsave(name, data, plugin="tifffile")
