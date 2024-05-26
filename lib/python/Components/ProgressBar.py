# -*- coding: utf-8 -*-
from Components.GUIComponent import GUIComponent
from Components.VariableValue import VariableValue

from enigma import eSlider

# a general purpose progress bar


class ProgressBar(VariableValue, GUIComponent):
	def __init__(self):
		GUIComponent.__init__(self)
		VariableValue.__init__(self)
		self.__start = 0
		self.__end = 100

	GUI_WIDGET = eSlider

	def postWidgetCreate(self, instance):
		instance.setRange(self.__start, self.__end)

	def setRange(self, range):
		if self.instance is not None:
			self.__start, self.__end = range
			self.instance.setRange(self.__start, self.__end)

	def getRange(self):
		return (self.__start, self.__end)

	range = property(getRange, setRange)
