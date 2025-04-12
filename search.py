# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import api
import sys

from NVDAObjects import NVDAObject

from .utils import debugLog


# class to collect useful search direction tuples
class SearchDirections:

	LEFT = (0,)
	TOP = (1,)
	RIGHT = (2,)
	BOTTOM = (3,)
	LEFT_TOP = (*LEFT, *TOP)
	HORIZONTAL = (*LEFT, *RIGHT)
	VERTICAL = (*TOP, *BOTTOM)
	ALL = (*LEFT, *TOP, *RIGHT, *BOTTOM)


# class for search config
class SearchConfig:

	configKeys = (
		# obj to label
		"obj",
		# strategy to use (auto, obj, text, web)
		# auto (default): determined by getLabel (according to presence of static objs, see below);
		# obj: based to static objs with the label as name (verify with object review);
		# text: based to text retrieval from parent obj containing labels as simple text (verify with screen review);
		# web: based to treeInterceptor presence (very similar to obj, but into web pages)
		"strategy",
		# (text and web strategy) obj that contains the label
		"labelContainer",
		# the topmost limit under which retrieve label text or objects
		"maxParent",
		# direction(s) to consider for label search
		# must be a SearchDirections constant, or a tuple
		# defined e.g. as: (*SearchDirections.LEFT, *SearchDirections.BOTTOM)
		"directions",
		# max horizontal distance between an obj point (left or right) and the outside comparison point
		"maxHorizontalDistance",
		# max vertical distance between an obj point (top or bottom) and the outside comparison point
		"maxVerticalDistance"
	)

	def __init__(self, oldConfig=None, **kwargs):
		self.config = {}
		# derive from an old config
		if isinstance(oldConfig, SearchConfig):
			self.config = {k:v for k,v in oldConfig.config.items() if k in self.configKeys}
		# integrate new passed values
		# overriding those already present
		for key in self.configKeys:
			val = kwargs.get(key, None)
			if val:
				self.config[key] = val

	@property
	def obj(self):
		val = self.config.get("obj", None)
		if isinstance(val, NVDAObject):
			return val
		# it's better to provide obj, e.g. via event_* filtering, but anyway...
		if self.strategy == "web":
			return api.getNavigatorObject()
		return api.getFocusObject()

	@property
	def strategy(self):
		val = self.config.get("strategy", None)
		if val in ("auto", "obj", "text", "web"):
			return val
		return "auto"

	@property
	def labelContainer(self):
		val = self.config.get("labelContainer", None)
		if isinstance(val, NVDAObject):
			return val
		# force search in obj ancestors
		return None

	@property
	def maxParent(self):
		val = self.config.get("maxParent", None)
		if isinstance(val, NVDAObject):
			return val
		if self.strategy == "web":
			return None
		return api.getForegroundObject()

	@property
	def directions(self):
		val = self.config.get("directions", None)
		if isinstance(val, tuple) and all([isinstance(i, int) for i in val]):
			return val
		# labels are usally on left, or top
		return SearchDirections.LEFT_TOP

	@property
	def maxHorizontalDistance(self):
		val = self.config.get("maxHorizontalDistance", None)
		if isinstance(val, int):
			if val == sys.maxsize and self.strategy in ("obj", "text", "web"):
				fg = api.getForegroundObject()
				return fg.location.width if self.strategy != "text" else 10000
			return val
		elif self.strategy == "auto":
			# it should never happen, but anyway...
			return sys.maxsize
		elif self.strategy in ("obj", "web"):
			return 100
		elif self.strategy == "text":
			from .labelFromText import RestrictedDMTI
			return RestrictedDMTI.minHorizontalWhitespace

	@property
	def maxVerticalDistance(self):
		val = self.config.get("maxHorizontalDistance", None)
		if isinstance(val, int):
			if val == sys.maxsize and self.strategy in ("obj", "text", "web"):
				fg = api.getForegroundObject()
				return fg.location.height if self.strategy != "text" else 10000
			return val
		elif self.strategy == "auto":
			# it should never happen, but anyway...
			return sys.maxsize
		elif self.strategy in ("obj", "web"):
			return 100
		elif self.strategy == "text":
			return None
