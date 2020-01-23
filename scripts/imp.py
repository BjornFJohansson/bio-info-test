#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on Thu Jan 23 12:30:19 2020 @author: bjorn

import importlib.util
import sys

file_path = "settings.py"
module_name = "settings"

spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)
