# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 10:08:49 2024

@author: frpez
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from random import randint

## define directory
dir_path = os.path.abspath('')
os.chdir('..')
from CiSSA.pycissa import cissa, group, cissa_outlier