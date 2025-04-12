# LabelAutofinderCore

This is a module for NVDA. Useful in other add-ons, it does nothing by itself.

The module implements various techniques to associate to a chosen object the label (or other info) at screen, according to nearest visual position.

Supported scenarios are:

* web pages, e.g. the fields in a form not correctly labelled;
* programs with labels as object (retrievable with object review), sometimes associated to wrong GUI items;
* programs with labels as text (retrievable with screen review), where association with objects could be completely missed.

TLDR? Jump to "Script for testing" section.

## Usage

The main method to import and call is getLabel, usually from within event_* or chooseNVDAObjectOverlayClasses.

In the best case, with default configuration, you can simply do something like:

```
import appModuleHandler
from .labelAutofinderCore import getLabel

class AppModule(appModuleHandler.AppModule):

	def event_gainFocus(self, obj, nextHandler):
		if not obj.name:  # and other checks you want
			obj.name = getLabel(obj)
		nextHandler()
```

Note: all examples here will be as AppModule, that is, a context where this module can have more predictable behaviors. But nothing prevents you to use it into a GlobalPlugin, if you adeguately restrict its action (e.g.: only on form fields into web pages).

## Default configuration and how to customize it

Sometimes, label search with default configuration fails, but you can customize it to better catch the correct label.

You can provide following parameters to SearchConfig:

* obj: object to label (if you want to pass just the config to getLabel);\
Default: focus object (or navigator object for web) retrieved via api; due to event processing or object building, passing the object (via getLabel or config) is strongly recomended;
* strategy: it can be "auto", "obj", "text" or "web" (but specify it should be a minimum impact on performance, it's mainly for internal behaviors);\
Default: "auto";
* labelContainer: the object containing the label (text and web strategy only);\
Default: None (algorithm goes up in ancestor tree, in bottom-top order);
* maxParent: the topmost limit under which to retrieve labels;\
Default: foreground object (or None for web, that practically means the first object with DOCUMENT role);
* directions: a SearchDirections class constants (LEFT, TOP, RIGHT, BOTTOM, HORIZONTAL, VERTICAL, LEFT_TOP, ALL), or any tuple defined like `(*SearchDirections.LEFT, *SearchDirections.TOP, *SearchDirections.BOTTOM)`;\
Default: SearchDirections.LEFT_TOP;
* maxHorizontalDistance: max horizontal distance between left/right point of object to label and relative point of the label;\
Default: 100 for obj and web, 8 for text strategy; if set to sys.maxsize, then it'll be the width of foreground object for obj and web, and 10000 for text strategy;
* maxVerticalDistance: max vertical distance between top/bottom point of object to label and relative point of the label;\
Default: 100 for obj and web, None for text strategy (it forces to use the character height); if set to sys.maxsize, then it'll be the height of foreground object for obj and web, and 10000 for text strategy.

In addition, you can also derive a config by a previous config, building as `SearchConfig(oldConfig=prevConfig)`.

So, if your label is on bottom, instead of default left or top, you can do:

```
import appModuleHandler
from .labelAutofinderCore import getLabel, SearchConfig, SearchDirections

class AppModule(appModuleHandler.AppModule):

	def event_gainFocus(self, obj, nextHandler):
		if not obj.name:  # and other checks you want
			config = SearchConfig(directions=SearchDirections.BOTTOM)
			obj.name = getLabel(obj, config)
		nextHandler()
```

## Script for testing

To better understand and explore your situation, it may be useful to use a script like this:

```
import api
import globalPluginHandler
import ui
from scriptHandler import script
from .labelAutofinderCore import getLabel, SearchConfig, SearchDirections

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = "Testing LabelAutofinder module"

	@script(
		description=_("tries to find and reports a label for current focused object")
	)
	def script_findLabel(self, gesture):
		tempObj = api.getNavigatorObject()
		if tempObj.treeInterceptor:
			obj = tempObj
		else:
			obj = api.getFocusObject()
		labelTuples = []
		baseConfig = SearchConfig(obj=obj)
		for direction in ("left", "top", "right", "bottom"):
			searchDirection = getattr(SearchDirections, direction.upper())
			directionConfig = SearchConfig(oldConfig=baseConfig, directions=searchDirection)
			# overview=True to get distance, in addition to label
			distanceAndLabel = getLabel(config=directionConfig, overview=True)
			if distanceAndLabel:
				labelTuples.append((direction, *distanceAndLabel,))
		if not labelTuples:
			ui.message(_("Unable to find any label"))
			return
		# sort for distance
		labelTuples.sort(key=lambda i: i[1])
		labelMsgs = []
		for direction, distance, label in labelTuples:
			labelMsg = "{distance} on {direction}: {label}".format(distance=distance, direction=direction, label=label)
			labelMsgs.append(labelMsg)
		msg = '; '.join(labelMsgs)
		ui.message(msg)
```

## ...and other info!

Even if it was born for labels, developing this module I was delighted to discover that it can be used in a small number of other cases.

One of these are the sliders. Usually from 0 to 100%, at screen, indeed, they could be presented as a completely different range, e.g. of KB/s, Decibel, and so on.

Now you can do something like:

```
import appModuleHandler
from controlTypes import Role as roles
from NVDAObjects.IAccessible import IAccessible
from .labelAutofinderCore import getLabel, SearchConfig, SearchDirections

class AppModule(appModuleHandler.AppModule):

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if not obj.name and obj.role == roles.SLIDER:
			clsList.insert(0, SliderWithUnit)

class SliderWithUnit(IAccessible):

	def _get_name(self):
		name = getLabel(self)
		return name

	def _get_value(self):
		config = SearchConfig(directions=SearchDirections.RIGHT)  # or any other direction in your situation
		value = getLabel(self, config)
		return value
```

## Notes and suggestions

### Include as Git submodule

If you include this module into your add-on, the best way is probably to add it as a Git submodule, under the appropriate path. E.g.:

```
>git submodule add https://github.com/ABuffEr/labelAutofinderCore addon/appModules/labelAutofinderCore
>git submodule init
>git submodule update
>git commit -m "Added labelAutofinderCore as submodule"
>git push --all
```

If you have problems running `git submodule update` the next times, try to see [here.](https://stackoverflow.com/questions/3336995/git-will-not-init-sync-update-new-submodules)

Regardless of path, please mantain the name of last folder as "labelAutofinderCore", so to guarantee a "opportunity check" by other add-ons (especially global plugins).

Moreover, I'll be very happy if you cite this work in your readme!

### When text disappears

When text strategy is required (you find labels with screen review only), you may notice a strange behavior when restart NVDA and in other situations: the text disappears completely, to appear again if you minimize or close and reopen the program/window.

It's not caused by this module, that nevertheless provides a solution.

Use something like this:

```
import appModuleHandler
from controlTypes import Role as roles
from .labelAutofinderCore import refreshTextContent

class AppModule(appModuleHandler.AppModule):

	def event_foreground(self, obj, nextHandler):
		# to fix text disappearing
		if obj.role == roles.PANE:  # or similar, but anyway the role of object containing text
			refreshTextContent(obj)
		nextHandler()
```

### Combobox and editable combobox

You may encounter situations with unlabelled combobox and editable combobox (I mean, with another child object as editable field).

I suggest to distinguish via event_gainFocus and event_focusEntered to avoid double labelling.

Something like this:

```
import appModuleHandler
from controlTypes import Role as roles
from .labelAutofinderCore import getLabel

class AppModule(appModuleHandler.AppModule):

	def event_gainFocus(self, obj, nextHandler):
		# to label simple edit and combo boxes
		if (
			(not obj.name)
			and
			(obj.role == roles.COMBOBOX or (obj.role == roles.EDITABLETEXT and obj.simpleParent.role != roles.COMBOBOX))
		):
			obj.name = getLabel(obj)
		nextHandler()

	def event_focusEntered(self, obj, nextHandler):
		# to label combo with edit boxes
		if not obj.name and obj.role == roles.COMBOBOX:
			obj.name = getLabel(obj)
		nextHandler()
```

### Avoid "big" edit boxes

There are anonymous edit boxes that have every reason to be such, like log reporting, main window of text editor, and so on.

A quick way to exclude these objects can be to refer to obj.location.width, setting a reasonable upper or lower limit (that may vary according to screen resolution, though), or to the presence of MULTILINE into states.
