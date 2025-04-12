# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import ctypes
import winUser

from NVDAObjects.IAccessible import getNVDAObjectFromEvent

from .explorers import ObjExplorer
from .search import SearchConfig
from .utils import debugLog


def getLabelFromObj(obj, config):
	# recreate config, to specify strategy
	config = SearchConfig(oldConfig=config, obj=obj, strategy="obj")
	staticHandles = getAllStaticHandles(config.maxParent.windowHandle)
	if not staticHandles:
		debugLog("No handles found!")
		return
	objRect = config.obj.location.toLTRB()
	# explorer that looks for labels around obj
	explorer = ObjExplorer(objRect, config)
	staticObjs = [getNVDAObjectFromEvent(handle, winUser.OBJID_CLIENT, 0) for handle in staticHandles]
	res = explorer.getDistanceAndLabelText(staticObjs)
	return res

# to collect handles of all static objs
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
def getAllStaticHandles(parent):
	results = []
	@WNDENUMPROC
	def callback(window, data):
		isWindowVisible = winUser.isWindowVisible(window)
		isWindowEnabled = winUser.isWindowEnabled(window)
		className = winUser.getClassName(window)
		if isWindowVisible and isWindowEnabled and "static" in className.lower():
			results.append(window)
		return True
	# call previous func until it returns True,
	# thus always, getting all windows
	ctypes.windll.user32.EnumChildWindows(parent, callback, 0)
	# return all results
	return results
