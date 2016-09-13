#!/usr/bin/env python3
from glob import glob
import pandas as pd

path = './TF-MAR/total_geral.csv'
df = pd.read_csv(path)

# x 1686, 1793 y : 2465, 2599
df = df[(df.y >= 1686) & (df.y <= 1793)]
df = df[(df.x >= 2465) & (df.x <= 2599)]

df.to_csv("testando.csv")
