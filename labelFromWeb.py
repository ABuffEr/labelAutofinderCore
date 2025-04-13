# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import textInfos

from controlTypes import Role as roles
from NVDAObjects.IAccessible import getNVDAObjectFromPoint

from .explorers import ObjExplorer
from .search import SearchConfig
from .utils import debugLog, getReversedAncestors


def getLabelFromWeb(obj, config):
	# recreate config, to specify strategy
	config = SearchConfig(oldConfig=config, obj=obj, strategy="web")
	labelObjs = getLabelsFromWebContainer(config)
	if not labelObjs:
		debugLog("No web labels found!")
		return
	objRect = config.obj.location.toLTRB()
	# explorer that looks for labels around obj
	explorer = ObjExplorer(objRect, config)
	res = explorer.getDistanceAndLabelText(labelObjs)
	return res

webCache = {}
def getLabelsFromWebContainer(config):
	# find a labelContainer in obj ancestors that could provide label objs
	labelObjs = None
	# obj containing labels as simple text
	labelContainer = config.labelContainer
	# obj to label
	obj = config.obj
	# topmost limit for labelContainer search
	maxParent = config.maxParent
	ancestors = [labelContainer] if labelContainer else getReversedAncestors(obj, roleStop=roles.DOCUMENT)
	for ancestor in ancestors:
		cachedObjs = webCache.get(ancestor, None)
		tempObjs = [x for x in getAllStaticChildren(ancestor)] if (cachedObjs is None) else cachedObjs
		if cachedObjs is None:
			debugLog("Ancestor not cached")
			webCache[ancestor] = tempObjs
		if tempObjs:
			labelObjs = tempObjs
			break
		if ancestor == maxParent:
			break
	return labelObjs

def getAllStaticChildren(parent):
	webParent = parent.treeInterceptor
	if not webParent:
		return
	info = parent.makeTextInfo(textInfos.POSITION_ALL)
	for offset in info._iterTextWithEmbeddedObjects(False):
		if not isinstance(offset, int):
			continue
		try:
			rect = info._getBoundingRectFromOffset(offset)
		except LookupError:  # it happens, for some reason
			continue
		point = rect.center
		child = getNVDAObjectFromPoint(point.x, point.y)
		if child and child.role == roles.STATICTEXT and child.name:
			yield child
