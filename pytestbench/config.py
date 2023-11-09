# -*- coding: utf-8 -*-

import os.path as osp

from guidata import configtools

APP_NAME = "PyTestBench"
MOD_NAME = "pytestbench"

configtools.add_image_module_path(MOD_NAME, osp.join("data", "logo"))

DATAPATH = configtools.get_module_data_path(MOD_NAME, "data")
