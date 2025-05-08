# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import UIAHandler

from NVDAObjects.UIA import UIA

from .explorers import ObjExplorer
from .search import SearchConfig
from .utils import debugLog, measureTime


def getLabelFromUWPObj(obj, config):
	# recreate config, to specify strategy
	config = SearchConfig(oldConfig=config, obj=obj, strategy="uwp")
	staticUIAElements = getAllStaticUIAElements(config.maxParent)
	if not staticUIAElements:
		debugLog("No UIA elements found!")
		return
	objRect = config.obj.location.toLTRB()
	# explorer that looks for labels around obj
	explorer = ObjExplorer(objRect, config)
	staticObjs = [UIA(UIAElement=element) for element in staticUIAElements]
	res = explorer.getDistanceAndLabelText(staticObjs)
	return res

# to collect UIAElement of all TextBlock objs
def getAllStaticUIAElements(parent):
	client = UIAHandler.handler.clientObject
	classCondition = client.CreatePropertyCondition(UIAHandler.UIA_ClassNamePropertyId, "TextBlock")
	cacheRequest = UIAHandler.handler.baseCacheRequest
	UIAArray = parent.UIAElement.FindAllBuildCache(UIAHandler.TreeScope_Descendants, classCondition, cacheRequest)
	results = [UIAArray.GetElement(n) for n in range(UIAArray.Length)]
	return results
