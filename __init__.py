#!/usr/bin/env python
#-*- coding: utf-8 -*-



__title__ = 'mozrepl'
__version__ = '1.2.4'
__author__ = '별님'
__author_email__ = 'w7dn1ng75r@gmail.com'
__license__ = 'GPL v3'
__copyright__ = 'Copyright 2015 별님'
__url__ = 'https://github.com/Thestars3/pymozrepl/'

import sys
if sys.version_info < (3,):
	from .exception import Exception
from .mozrepl import Mozrepl
