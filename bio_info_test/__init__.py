#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"
__author__  = "Björn Johansson"
__email__   = "bjorn_johansson@bio.uminho.pt"
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
