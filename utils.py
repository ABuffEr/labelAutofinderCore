# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import time

from contextlib import contextmanager
from ctypes import windll
from logHandler import log


# to enable debug
DEBUG = False

# for logging
def debugLog(message):
	if DEBUG:
		log.info(message)

# for testing performances
@contextmanager
def measureTime(label):
	start = time.time()
	try:
		yield
	finally:
		end = time.time()
		log.info("%s: %.3f s"%(label, end-start))

# for forcing obj to correctly refresh its text content,
# useful in some (Delphi?) software;
# see SetWindowPos documentation:
# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos
SWP_FRAMECHANGED = 0x0020
SWP_NOCOPYBITS = 0x0100
SWP_NOMOVE = 0x0002
SWP_NOREPOSITION = 0x0200
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
# join together
SWP_FLAGS = SWP_FRAMECHANGED|SWP_NOCOPYBITS|SWP_NOMOVE|SWP_NOREPOSITION|SWP_NOSIZE|SWP_NOZORDER|SWP_SHOWWINDOW

def refreshTextContent(obj):
	windll.user32.SetWindowPos(obj.windowHandle, None, None, None, None, None, SWP_FLAGS)

# generate ancestors of any obj
# in bottom-top order
def getReversedAncestors(obj, roleStop=None):
	while (parent := obj.parent):
		# useful for web strategy
		yield parent
		if roleStop and parent.role == roleStop:
			return
		obj = parent
