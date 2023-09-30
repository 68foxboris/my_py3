from os import system, listdir, rename, path, mkdir
from os.path import exists
from time import sleep
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigText, ConfigSelection, ConfigInteger, ConfigClock, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Sources.Boolean import Boolean
from Components.Pixmap import Pixmap
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists


class CronTimers(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		if not exists("/usr/script"):
			mkdir("/usr/script", 0o755)
		Screen.setTitle(self, _("Cron Manager"))
		self.onChangedEntry = []
		self["lab1"] = Label(_("Autostart:"))
		self["labactive"] = Label(_("Active"))
		self["labdisabled"] = Label(_("Disabled"))
		self["lab2"] = Label(_("Current Status:"))
		self["labstop"] = Label(_("Stopped"))
		self["labrun"] = Label(_("Running"))
		self["labrun"].hide()
		self["labactive"].hide()
		self.summary_running = ""
		self["key"] = Label(_("H: = Hourly / D: = Daily / W: = Weekly / M: = Monthly"))
		self.Console = Console()
		self.my_crond_active = False
		self.my_crond_run = False

		self["key_red"] = Label(_("Delete"))
		self["key_green"] = Label(_("Add"))
		self["key_yellow"] = StaticText(_("Start"))
		self["key_blue"] = Label(_("Autostart"))
		self.list = []
		self["list"] = List(self.list)
		self["actions"] = ActionMap(["WizardActions", "ColorActions", "MenuActions"], {"ok": self.info, "back": self.uninstallCheck, "red": self.delcron, "green": self.addtocron, "yellow": self.crondStart, "blue": self.autostart})
		if not self.selectionChanged in self["list"].onSelectionChanged:
			self["list"].onSelectionChanged.append(self.selectionChanged)
		self.service_name = "cronie"
		self.installCheck()

	def installCheck(self):
		self.Console.ePopen("/usr/bin/opkg list_installed " + self.service_name, self.checkNetworkState)

	def checkNetworkState(self, str, retval, extra_args):
		if "Collected errors" in str:
			self.session.openWithCallback(self.close, MessageBox, _("Seems a background update check is in progress, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif not str:
			self.session.openWithCallback(self.InstallPackage, MessageBox, _("Do you want to install \"%s\" ?") % self.service_name, MessageBox.TYPE_YESNO)
		else:
			self.updateList()

	def installPackage(self, val):
		if val:
			self.doInstall(self.installComplete, self.service_name)
		else:
			self.feedscheck.close()
			self.close()

	def installPackageFailed(self, val):
		self.feedscheck.close()
		self.close()

	def doInstall(self, callback, pkgname):
		self.message = self.session.open(MessageBox, _("Please wait..."), MessageBox.TYPE_INFO, enable_input=False)
		self.message.setTitle(_("Installing Service"))
		self.Console.ePopen("/usr/bin/opkg install " + pkgname, callback)

	def installComplete(self, result=None, retval=None, extra_args=None):
		self.message.close()
		self.feedscheck.close()
		self.updateList()

	def uninstallCheck(self):
		if not self.my_crond_run:
			self.Console.ePopen("/usr/bin/opkg list_installed " + self.service_name, self.removedataAvail)
		else:
			self.close()

	def removedataAvail(self, result, retval, extra_args):
		if result:
			self.session.openWithCallback(self.removePackage, MessageBox, _("Ready to remove \"%s\" ?") % self.service_name)
		else:
			self.close()

	def removePackage(self, val):
		if val:
			self.doRemove(self.removeComplete, self.service_name)
		else:
			self.close()

	def doRemove(self, callback, pkgname):
		self.message = self.session.open(MessageBox, _("Please wait..."), MessageBox.TYPE_INFO, enable_input=False)
		self.message.setTitle(_("Removing Service"))
		self.Console.ePopen("/usr/bin/opkg remove " + pkgname + " --force-remove --autoremove", callback)

	def removeComplete(self, result=None, retval=None, extra_args=None):
		self.message.close()
		self.close()

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		try:
			if self["list"].getCurrent():
				name = str(self["list"].getCurrent()[0])
			else:
				name = ""
		except:
			name = ""
		desc = _("Current status:") + " " + self.summary_running
		for cb in self.onChangedEntry:
			cb(name, desc)

	def crondStart(self):
		if not self.my_crond_run:
			self.Console.ePopen("/etc/init.d/crond start", self.startStopCallback)
		elif self.my_crond_run:
			self.Console.ePopen("/etc/init.d/crond stop", self.startStopCallback)

	def startStopCallback(self, result=None, retval=None, extra_args=None):
		sleep(3)
		self.updateList()

	def autostart(self):
		if fileExists("/etc/rc2.d/S90crond"):
			self.Console.ePopen("update-rc.d -f crond remove")
		else:
			self.Console.ePopen("update-rc.d -f crond defaults 90 60")
		sleep(3)
		self.updateList()

	def addtocron(self):
		self.session.openWithCallback(self.updateList, CronTimersConfig)

	def updateList(self, result=None, retval=None, extra_args=None):
		import process
		p = process.ProcessList()
		crond_process = str(p.named("crond")).strip("[]")
		self["labrun"].hide()
		self["labstop"].hide()
		self["labactive"].hide()
		self["labdisabled"].hide()
		self.my_crond_active = False
		self.my_crond_run = False
		if exists("/etc/rc3.d/S90crond"):
			self["labdisabled"].hide()
			self["labactive"].show()
			self.my_crond_active = True
		else:
			self["labactive"].hide()
			self["labdisabled"].show()
		if crond_process:
			self.my_crond_run = True
		if self.my_crond_run:
			self["labstop"].hide()
			self["labrun"].show()
			self["key_yellow"].setText(_("Stop"))
			self.summary_running = _("Running")
		else:
			self["labstop"].show()
			self["labrun"].hide()
			self["key_yellow"].setText(_("Start"))
			self.summary_running = _("Stopped")

		self.list = []
		if exists("/etc/cron/crontabs/root"):
			f = open("/etc/cron/crontabs/root")
			for line in f.readlines():
				parts = line.strip().split(maxsplit=5)
				if parts and len(parts) == 6 and not parts[0].startswith("#"):
					if parts[1] == "*":
						line2 = "H: 00:" + parts[0].zfill(2) + "\t" + parts[5]
						res = (line2, line)
						self.list.append(res)
					elif parts[2] == "*" and parts[4] == "*":
						line2 = "D: " + parts[1].zfill(2) + ":" + parts[0].zfill(2) + "\t" + parts[5]
						res = (line2, line)
						self.list.append(res)
					elif parts[3] == "*":
						if parts[4] == "*":
							line2 = "M:  Day " + parts[2] + "  " + parts[1].zfill(2) + ":" + parts[0].zfill(2) + "\t" + parts[5]
						header = "W:  "
						day = ""
						if str(parts[4]).find("0") >= 0:
							day = "Sun "
						if str(parts[4]).find("1") >= 0:
							day += "Mon "
						if str(parts[4]).find("2") >= 0:
							day += "Tues "
						if str(parts[4]).find("3") >= 0:
							day += "Wed "
						if str(parts[4]).find("4") >= 0:
							day += "Thurs "
						if str(parts[4]).find("5") >= 0:
							day += "Fri "
						if str(parts[4]).find("6") >= 0:
							day += "Sat "
						if day:
							line2 = header + day + parts[1].zfill(2) + ":" + parts[0].zfill(2) + "\t" + parts[5]
						res = (line2, line)
						self.list.append(res)
			f.close()
		self["list"].list = self.list
		self["actions"].setEnabled(True)

	def delcron(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			parts = self.sel[0]
			parts = parts.split("\t")
			message = _("Are you sure you want to delete this:\n ") + parts[1]
			ybox = self.session.openWithCallback(self.doDelCron, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Remove Confirmation"))

	def doDelCron(self, answer):
		if answer:
			mysel = self["list"].getCurrent()
			if mysel:
				myline = mysel[1]
				open("/etc/cron/crontabs/root.tmp", "w").writelines([l for l in open("/etc/cron/crontabs/root").readlines() if myline not in l])
				rename("/etc/cron/crontabs/root.tmp", "/etc/cron/crontabs/root")
				rc = system("crontab /etc/cron/crontabs/root -c /etc/cron/crontabs")
				self.updateList()

	def info(self):
		mysel = self["list"].getCurrent()
		if mysel:
			myline = mysel[1]
			self.session.open(MessageBox, _(myline), MessageBox.TYPE_INFO)

config.crontimers = ConfigSubsection()
config.crontimers.commandtype = NoSave(ConfigSelection(choices=[
	("custom", _("Custom")),
	("predefined", _("Predefined"))
]))
config.crontimers.cmdtime = NoSave(ConfigClock(default=0))
config.crontimers.cmdtime.value, mytmpt = ([0, 0], [0, 0])
config.crontimers.user_command = NoSave(ConfigText(fixed_size=False))
config.crontimers.runwhen = NoSave(ConfigSelection(default="Daily", choices=[
	("Hourly", _("Hourly")),
	("Daily", _("Daily")),
	("Weekly", _("Weekly")),
	("Monthly", _("Monthly"))
]))
config.crontimers.dayofweek = NoSave(ConfigSelection(default="Monday", choices=[
	("Monday", _("Monday")),
	("Tuesday", _("Tuesday")),
	("Wednesday", _("Wednesday")),
	("Thursday", _("Thursday")),
	("Friday", _("Friday")),
	("Saturday", _("Saturday")),
	("Sunday", _("Sunday"))
]))
config.crontimers.dayofmonth = NoSave(ConfigInteger(default=1, limits=(1, 31)))


class CronTimersConfig(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Cron Manager"))
		self.skinName = "Setup"
		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
		self["key_red"] = Label(_("Close"))
		self["key_green"] = Label(_("Save"))
		self["actions"] = ActionMap(["WizardActions", "ColorActions", "VirtualKeyboardActions", "MenuActions"], {"red": self.close, "green": self.checkentry, "back": self.close, "showVirtualKeyboard": self.keyText})
		self["VKeyIcon"] = Boolean(False)
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["footnote"] = Label()
		self["description"] = Label()
		self.createSetup()

	def createSetup(self):
		predefinedlist = []
		f = listdir("/usr/script")
		if f:
			for line in f:
				parts = line.split()
				path = "/usr/script/"
				pkg = parts[0]
				description = path + parts[0]
				if pkg.find(".sh") >= 0:
					predefinedlist.append((description, pkg))
			predefinedlist.sort()
		config.crontimers.predefined_command = NoSave(ConfigSelection(choices=predefinedlist))
		self.editListEntry = None

		self.list = []
		self.list.append((_("Run how often?"), config.crontimers.runwhen))
		if config.crontimers.runwhen.value != "Hourly":
			self.list.append((_("Time to execute command or script"), config.crontimers.cmdtime))
		if config.crontimers.runwhen.value == "Weekly":
			self.list.append((_("What day of week?"), config.crontimers.dayofweek))
		if config.crontimers.runwhen.value == "Monthly":
			self.list.append((_("What day of month?"), config.crontimers.dayofmonth))
		self.list.append((_("Command type"), config.crontimers.commandtype))
		if config.crontimers.commandtype.value == "custom":
			self.list.append((_("Command to run"), config.crontimers.user_command))
		else:
			self.list.append((_("Command to run"), config.crontimers.predefined_command))
		self["config"].list = self.list
		self["config"].setList(self.list)

	# for summary:
	def changedEntry(self):
		if self["config"].getCurrent()[0] == _("Run how often?") or self["config"].getCurrent()[0] == _("Command type"):
			self.createSetup()
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def keyText(self):
		sel = self["config"].getCurrent()
		if sel:
			self.vkvar = sel[0]
			if self.vkvar == _("Command to run"):
				from Screens.VirtualKeyBoard import VirtualKeyBoard
				self.session.openWithCallback(self.virtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

	def virtualKeyBoardCallback(self, callback=None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def checkentry(self):
		msg = ""
		if (config.crontimers.commandtype.value == "predefined" and config.crontimers.predefined_command.value == "") or config.crontimers.commandtype.value == "custom" and config.crontimers.user_command.value == "":
			msg = _("You must set at least one command!")
		if msg:
			self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR)
		else:
			self.saveMycron()

	def saveMycron(self):
		hour = "%02d" % config.crontimers.cmdtime.value[0]
		minutes = "%02d" % config.crontimers.cmdtime.value[1]
		if config.crontimers.commandtype.value == "predefined" and config.crontimers.predefined_command.value != "":
			command = config.crontimers.predefined_command.value
		else:
			command = config.crontimers.user_command.value
		if config.crontimers.runwhen.value == "Hourly":
			newcron = "%s * * * * %s\n" % (minutes, command.strip())
		elif config.crontimers.runwhen.value == "Daily":
			newcron = "%s %s * * * %s\n" % (minutes, hour, command.strip())
		elif config.crontimers.runwhen.value == "Weekly":
			if config.crontimers.dayofweek.value == "Sunday":
				newcron = "%s %s * * 0 %s\n" % (minutes, hour, command.strip())
			elif config.crontimers.dayofweek.value == "Monday":
				newcron = "%s %s * * 1 %s\n" % (minutes, hour, command.strip())
			elif config.crontimers.dayofweek.value == "Tuesday":
				newcron = "%s %s * * 2 %s\n" % (minutes, hour, command.strip())
			elif config.crontimers.dayofweek.value == "Wednesday":
				newcron = "%s %s * * 3 %s\n" % (minutes, hour, command.strip())
			elif config.crontimers.dayofweek.value == "Thursday":
				newcron = "%s %s * * 4 %s\n" % (minutes, hour, command.strip())
			elif config.crontimers.dayofweek.value == "Friday":
				newcron = "%s %s * * 5 %s\n" % (minutes, hour, command.strip())
			elif config.crontimers.dayofweek.value == "Saturday":
				newcron = "%s %s * * 6 %s\n" % (minutes, hour, command.strip())
		elif config.crontimers.runwhen.value == "Monthly":
			newcron = "%s %s %s * * %s\n" % (minutes, hour, str(config.crontimers.dayofmonth.value), command.strip())
		else:
			command = config.crontimers.user_command.value

		out = open("/etc/cron/crontabs/root", "a")
		out.write(newcron)
		out.close()
		rc = system("crontab /etc/cron/crontabs/root -c /etc/cron/crontabs")
		config.crontimers.predefined_command.value = "None"
		config.crontimers.user_command.value = "None"
		config.crontimers.runwhen.value = "Daily"
		config.crontimers.dayofweek.value = "Monday"
		config.crontimers.dayofmonth.value = 1
		config.crontimers.cmdtime.value, mytmpt = ([0, 0], [0, 0])
		self.close()
