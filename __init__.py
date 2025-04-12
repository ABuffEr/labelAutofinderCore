# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import api

from .labelFromObj import getLabelFromObj, getAllStaticHandles
from .labelFromText import getLabelFromText
from .labelFromWeb import getLabelFromWeb
from .search import SearchConfig, SearchDirections
from .utils import debugLog, measureTime, refreshTextContent


__version__ = "2025-04-12"

def getLabel(obj=None, config=None, overview=False):
	"""main method to call, returns label of passed object, if found, None otherwise.
	@param obj: object to label, default to None;
		if None, refers to focus object (or navigator object for web);
		passing an object, usually via event_* or chooseNVDAObjectOverlayClasses, is strongly recomended;
	@type obj: NVDAObject or None;
	@param config: config to consider for label search, default to None;
		if None, a default config is created, according to detected situation;
		see SearchConfig class for more details;
	@type config: SearchConfig or None;
	@param overview: if False, returns label only; if True, returns a tuple with distance of label from object, and label;
		useful to test different config, default to False;
	@type overview: boolean;
	@return: label if overview=False, (distance, label) tuple if True;
	@rtype: str or tuple(int, str).
	"""
	# recreate config to store obj and simplify comparisons
	config = SearchConfig(oldConfig=config, obj=obj)
	debugLog("Start labelling for direction %s"%repr(config.directions))
	strategy = config.strategy
	if strategy == "auto":
		# determine real strategy
		treeInterceptor = config.obj.treeInterceptor
		if treeInterceptor:
			strategy = "web"
		else:
			fg = api.getForegroundObject()
			strategy = "obj" if getAllStaticHandles(fg.windowHandle) else "text"
	debugLog("Established strategy: %s"%strategy)
	if strategy == "web":
		res = getLabelFromWeb(obj, config)
	elif strategy == "obj":
		res = getLabelFromObj(obj, config)
	elif strategy == "text":
		res = getLabelFromText(obj, config)
	debugLog("End labelling for direction %s"%repr(config.directions))
	if not res:
		return
	distance, label = res
	if overview:
		return res
	else:
		return label
