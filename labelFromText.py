# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

from displayModel import DisplayModelTextInfo as DMTI

from .explorers import CharExplorer
from .search import SearchConfig
from .utils import debugLog, getReversedAncestors


def getLabelFromText(obj, config):
	# recreate config, to specify strategy
	config = SearchConfig(oldConfig=config, obj=obj, strategy="text")
	# get text from obj that contains it (labelContainer), provided or discovered automatically
	info = getTextFromTextContainer(config)
	if not info:
		debugLog("No text found!")
		return
	# rectangle of obj to label, in (left, top, right, bottom) representation
	# Remember:
	# x (left and right coordinates) goes from 0 to positive integers,
	# moving from left to right on the screen;
	# y (top and bottom coordinates) does the same but
	# moving from top to bottom on the screen;
	objRect = config.obj.location.toLTRB()
	# explorer that looks for chars around obj
	explorer = CharExplorer(objRect, config)
	# rectangles for each char in labelContainer
	charRects = info._storyFieldsAndRects[1]
	# get possible offsets of label
	res = explorer.getDistanceAndCharOffsets(charRects)
	if not res:
		debugLog("No chars around obj!")
		return
	distance, charOffsets	= res
	# calculate a mean of found offsets, to avoid spurious results
	chunkCenterOffset = sum(charOffsets)//len(charOffsets)
	# get start and end offsets for whole label
	labelStartOffset, labelEndOffset = info._getDisplayChunkOffsets(chunkCenterOffset)
	# finally, get label text from labelContainer
	label = info.text[labelStartOffset:labelEndOffset]
	debugLog("Label: %s"%label)
	res = (distance, label)
	return res

def getTextFromTextContainer(config):
	# find a labelContainer in obj ancestors that could provide labels
	info = None
	# obj containing labels as simple text
	labelContainer = config.labelContainer
	# obj to label
	obj = config.obj
	# topmost limit for labelContainer search
	maxParent = config.maxParent
	ancestors = [labelContainer] if labelContainer else getReversedAncestors(obj)
	for ancestor in ancestors:
		# useful to avoid obj parent that would provide obj content as text
		if ancestor.windowHandle != obj.windowHandle:
			# get text restricted to that ancestor, without children
			tempInfo = RestrictedDMTI(ancestor, ancestor.location.toLTRB())
			if tempInfo.text:
				info = tempInfo
				break
		if ancestor == maxParent:
			break
	return info


# class to exclude children objects from text retrieval
class RestrictedDMTI(DMTI):

	includeDescendantWindows = False
