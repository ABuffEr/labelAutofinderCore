# -*- coding: UTF-8 -*-
# LabelAutofinder module
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

from .search import SearchDirections
from .utils import debugLog


# explorer for obj and web strategy
class ObjExplorer:

	def __init__(self, objRect, config):
		# obj rectangle which you look around to
		self.objRect = objRect
		# direction(s) to consider for label search
		searchDirections = config.directions
		# max external distance from an obj point (left or right)
		self.maxHorizontalDistance = config.maxHorizontalDistance
		# max external distance from an obj point (top or bottom)
		self.maxVerticalDistance = config.maxVerticalDistance
		# methods for checking on each direction
		checkerMethods = (self.leftCheck, self.topCheck, self.rightCheck, self.bottomCheck)
		# point distances and labels collected for each direction
		self.distancesAndLabels = {}
		# checker methods to be invoked (according to passed directions)
		self.checkers = {}
		# initialize  for each passed direction
		for direction, checker in zip(SearchDirections.ALL, checkerMethods):
			if direction in searchDirections:
				self.distancesAndLabels[direction] = []
				self.checkers[direction] = checker

	def getDistanceAndLabelText(self, labelObjs):
		debugLog("Labels to analyze: %d"%len(labelObjs))
		# check proximity for each label obj
		# around obj in specified directions,
		# saving distance if in the neighborhood
		for labelObj in labelObjs:
			labelText = labelObj.name
			labelObjRect = labelObj.location.toLTRB()
			for direction, checker in self.checkers.items():
				distance = checker(labelObjRect)
				if distance:
					self.distancesAndLabels[direction].append((distance, labelText,))
		if not any(self.distancesAndLabels.values()):
			debugLog("No label obj found!")
			return
		# establish nearest label for each direction
		minDistancesAndLabels = {}
		for direction in self.checkers.keys():
			distancesAndLabels = self.distancesAndLabels[direction]
			debugLog("Distances and labels for direction %d: %s"%(direction, distancesAndLabels))
			minDistanceAndLabel = min(distancesAndLabels, key=lambda i: i[0]) if distancesAndLabels else (10000, None)
			minDistancesAndLabels[direction] = minDistanceAndLabel
		# establish the direction with nearest label
		chosenDirection = min(minDistancesAndLabels, key=minDistancesAndLabels.get)
		minDistance, labelText = minDistancesAndLabels[chosenDirection]
		if minDistance == 10000:
			debugLog("Unable to establish label position")
			return
		debugLog("Min distance: %d"%minDistance)
		if not labelText or labelText.isspace():
			# TODO: manage image with OCR and AI
			debugLog("Found label obj, but no text (maybe it's an image?)")
			return
		return (minDistance, labelText)

	def leftCheck(self, labelObjRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		labelLeft, labelTop, labelRight, labelBottom = labelObjRect
		if (
			(objTop <= labelBottom)
			and
			(objBottom > labelTop)
			and
			(
				(objLeft > labelRight and objLeft-labelRight <= self.maxHorizontalDistance)
				or
				# overlapping edges
				(objLeft <= labelRight < objRight)
			)
		):
			distance = abs(objLeft-labelRight)
			return distance

	def topCheck(self, labelObjRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		labelLeft, labelTop, labelRight, labelBottom = labelObjRect
		if (
			(objLeft < labelRight)
			and
			(objRight > labelLeft)
			and
			(objTop > labelBottom)
			and
			(objTop-labelBottom <= self.maxVerticalDistance)
		):
			distance = objTop-labelBottom
			return distance

	def rightCheck(self, labelObjRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		labelLeft, labelTop, labelRight, labelBottom = labelObjRect
		if (
			(objTop <= labelBottom)
			and
			(objBottom > labelTop)
			and
			(
				(objRight < labelLeft and labelLeft-objRight <= self.maxHorizontalDistance)
				or
				# overlapping edges
				(objLeft < labelLeft <= objRight)
			)
		):
			distance = abs(labelLeft-objRight)
			return distance

	def bottomCheck(self, labelObjRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		labelLeft, labelTop, labelRight, labelBottom = labelObjRect
		if (
			(objLeft < labelRight)
			and
			(objRight > labelLeft)
			and
			(objBottom < labelTop)
			and
			(labelTop-objBottom <= self.maxVerticalDistance)
		):
			distance = labelTop-objBottom
			return distance


# explorer for text strategy
class CharExplorer:

	def __init__(self, objRect, config):
		# obj rectangle which you look around
		self.objRect = objRect
		# direction(s) to consider for char search
		searchDirections = config.directions
		# max external distance from an obj point (left or right)
		self.maxHorizontalDistance = config.maxHorizontalDistance
		# max external distance from an obj point (top or bottom)
		self.maxVerticalDistance = config.maxVerticalDistance
		# methods for checking on each direction
		checkerMethods = (self.leftCheck, self.topCheck, self.rightCheck, self.bottomCheck)
		# char distances and offsets collected for each direction
		self.distancesAndOffsets = {}
		# checker methods to be invoked (according to passed directions)
		self.checkers = {}
		# initialize  for each passed direction
		for direction, checker in zip(SearchDirections.ALL, checkerMethods):
			if direction in searchDirections:
				self.distancesAndOffsets[direction] = {}
				self.checkers[direction] = checker

	def getDistanceAndCharOffsets(self, charRects):
		debugLog("Rects to analyze: %d"%len(charRects))
		# check proximity for each char rect
		# around obj in specified directions,
		# saving offset and distance if in the neighborhood
		for offset, charRect in enumerate(charRects):
			for direction, checker in self.checkers.items():
				distance = checker(charRect)
				if distance:
					self.distancesAndOffsets[direction].setdefault(distance, []).append(offset)
		if not any(self.distancesAndOffsets.values()):
			debugLog("No chunk offset found!")
			return
		# establish best direction to consider
		distanceAndDirection = self.getDistanceAndDirection()
		if not distanceAndDirection:
			debugLog("No direction found!")
			return
		distance, chosenDirection = distanceAndDirection
		debugLog("Chosen direction: %s"%chosenDirection)
		# and return min distance and the collected offsets in that direction
		offsets = self.distancesAndOffsets[chosenDirection][distance]
		return (distance, offsets)

	def getDistanceAndDirection(self):
		# find minimum distance in specified directions
		# or set a no-sense, giant one instead (when no offsets)
		minDistanceInDirection = {}
		for direction in self.checkers.keys():
			distances = self.distancesAndOffsets[direction].keys()
			minDistanceInDirection[direction] = min(distances) if distances else 10000
		# get direction with minimum distance
		# and check whether it's valid
		chosenDirection = min(minDistanceInDirection, key=minDistanceInDirection.get)
		minDistance = minDistanceInDirection[chosenDirection]
		if minDistance == 10000:
			debugLog("Unable to establish label position")
			return
		debugLog("Min distance: %d"%minDistance)
		# return best direction where retrieve offsets
		res = (minDistance, chosenDirection)
		return res

	def leftCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		if (
			(objTop<charBottom<=objBottom)
			and
			(objLeft > charRight)
			and
			(objLeft-charRight <= self.maxHorizontalDistance)
		):
			distance = objLeft-charRight
			return distance

	def topCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		maxVerticalDistance = self.maxVerticalDistance if self.maxVerticalDistance else charRect.height
		if (
			(objLeft<=charLeft<objRight)
			and
			(objTop > charBottom)
			and
			(objTop-charBottom <= maxVerticalDistance)
		):
			distance = objTop-charBottom
			return distance

	def rightCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		if (
			(objTop<charBottom<=objBottom)
			and
			(charLeft > objRight)
			and
			(charLeft-objRight <= self.maxHorizontalDistance)
		):
			distance = charLeft-objRight
			return distance

	def bottomCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		maxVerticalDistance = self.maxVerticalDistance if self.maxVerticalDistance else charRect.height
		if (
			(objLeft<=charLeft<objRight)
			and
			(charTop > objBottom)
			and
			(charTop-objBottom <= maxVerticalDistance)
		):
			distance = charTop-objBottom
			return distance
