from Components.config import config, ConfigSlider, ConfigSelection, ConfigYesNo, ConfigEnableDisable, ConfigSubsection, ConfigBoolean, ConfigSelectionNumber, ConfigNothing, NoSave
from enigma import eAVControl, eDVBVolumecontrol
from Components.SystemInfo import BoxInfo, SystemInfo
from os.path import exists

model = BoxInfo.getItem("model")
brand = BoxInfo.getItem("brand")
platform = BoxInfo.getItem("platform")

MODULE_NAME = __name__.split(".")[-1]


class AVSwitch:
	def setInput(self, input):
		INPUT = {"ENCODER": 0, "SCART": 1, "AUX": 2}
		eAVControl.getInstance().setInput(str(INPUT[input]))

	def setColorFormat(self, value):
		eAVControl.getInstance().setColorFormat(str(value))

	def setAspectRatio(self, value):
		eAVControl.getInstance().setAspectRatio(value)

	def getOutputAspect(self):
		valstr = config.av.aspectratio.value
		if valstr in ("4_3_letterbox", "4_3_panscan"):  # 4:3
			return (4, 3)
		elif valstr == "16_9":  # auto ... 4:3 or 16:9
			try:
				print("[AVSwitch] Read /proc/stb/vmpeg/0/aspect")
				if "1" in open("/proc/stb/vmpeg/0/aspect").read().split('\n', 1)[0]:  # 4:3
					return (4, 3)
			except IOError:
				print("[AVSwitch] Read /proc/stb/vmpeg/0/aspect failed.")
		elif valstr in ("16_9_always", "16_9_letterbox"):  # 16:9
			pass
		elif valstr in ("16_10_letterbox", "16_10_panscan"):  # 16:10
			return (16, 10)
		return (16, 9)

	def getFramebufferScale(self):
		return (1, 1)

	def getAspectRatioSetting(self):
		valstr = config.av.aspectratio.value
		if valstr == "4_3_letterbox":
			val = 0
		elif valstr == "4_3_panscan":
			val = 1
		elif valstr == "16_9":
			val = 2
		elif valstr == "16_9_always":
			val = 3
		elif valstr == "16_10_letterbox":
			val = 4
		elif valstr == "16_10_panscan":
			val = 5
		elif valstr == "16_9_letterbox":
			val = 6
		return val

	def setAspectWSS(self, aspect=None):
		if not config.av.wss.value:
			value = 2  # auto(4:3_off)
		else:
			value = 1  # auto
		eAVControl.getInstance().setWSS(value)


def InitAVSwitch():
	config.av = ConfigSubsection()
	if model == "vuduo" or brand == "Medi@link":
		config.av.yuvenabled = ConfigBoolean(default=False)
	else:
		config.av.yuvenabled = ConfigBoolean(default=True)
	colorformat_choices = {"cvbs": "CVBS"}

	# when YUV, Scart or S-Video is not support by HW, don't let the user select it
	if BoxInfo.getItem("yuv"):
		colorformat_choices["yuv"] = "YPbPr"
	if BoxInfo.getItem("scart"):
		colorformat_choices["rgb"] = "RGB"
	if SystemInfo["HasSVideo"]:
		colorformat_choices["svideo"] = "S-Video"

	config.av.colorformat = ConfigSelection(choices=colorformat_choices, default="cvbs")
	config.av.aspectratio = ConfigSelection(choices={
		"4_3_letterbox": _("4:3 Letterbox"),
		"4_3_panscan": _("4:3 PanScan"),
		"16_9": _("16:9"),
		"16_9_always": _("16:9 always"),
		"16_10_letterbox": _("16:10 Letterbox"),
		"16_10_panscan": _("16:10 PanScan"),
		"16_9_letterbox": _("16:9 Letterbox")},
		default="16_9")
	config.av.aspect = ConfigSelection(choices={
		"4_3": _("4:3"),
		"16_9": _("16:9"),
		"16_10": _("16:10"),
		"auto": _("Automatic")},
		default="auto")
	policy2_choices = {
		# TRANSLATORS: (aspect ratio policy: black bars on top/bottom) in doubt, keep english term.
		"letterbox": _("Letterbox"),
		# TRANSLATORS: (aspect ratio policy: cropped content on left/right) in doubt, keep english term
		"panscan": _("Pan&scan"),
		# TRANSLATORS: (aspect ratio policy: scale as close to fullscreen as possible)
		"scale": _("Just scale")}
	if exists("/proc/stb/video/policy2_choices"):
		try:
			if "full" in open("/proc/stb/video/policy2_choices").read().split('\n', 1)[0]:
				# TRANSLATORS: (aspect ratio policy: display as fullscreen, even if the content aspect ratio does not match the screen ratio)
				policy2_choices.update({"full": _("Full screen")})
		except:
			print("[AVSwitch] Read /proc/stb/video/policy2_choices failed.")
		try:
			if "auto" in open("/proc/stb/video/policy2_choices").read().split('\n', 1)[0]:
				# TRANSLATORS: (aspect ratio policy: automatically select the best aspect ratio mode)
				policy2_choices.update({"auto": _("Auto")})
		except:
			print("[AVSwitch] Read /proc/stb/video/policy2_choices failed.")
	config.av.policy_169 = ConfigSelection(choices=policy2_choices, default="scale")
	policy_choices = {
		# TRANSLATORS: (aspect ratio policy: black bars on left/right) in doubt, keep english term.
		"pillarbox": _("Pillarbox"),
		# TRANSLATORS: (aspect ratio policy: cropped content on left/right) in doubt, keep english term
		"panscan": _("Pan&scan"),
		# TRANSLATORS: (aspect ratio policy: scale as close to fullscreen as possible)
		"scale": _("Just scale")}
	if exists("/proc/stb/video/policy_choices"):
		try:
			if "nonlinear" in open("/proc/stb/video/policy_choices").read().split('\n', 1)[0]:
				# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching the left/right)
				policy_choices.update({"nonlinear": _("Nonlinear")})
		except:
			print("[AVSwitch] Read /proc/stb/video/policy_choices failed.")
		try:
			if "full" in open("/proc/stb/video/policy_choices").read().split('\n', 1)[0]:
				# TRANSLATORS: (aspect ratio policy: display as fullscreen, even if the content aspect ratio does not match the screen ratio)
				policy_choices.update({"full": _("Full screen")})
		except:
			print("[AVSwitch] Read /proc/stb/video/policy_choices failed.")
		try:
			if "auto" in open("/proc/stb/video/policy_choices").read().split('\n', 1)[0]:
				# TRANSLATORS: (aspect ratio policy: automatically select the best aspect ratio mode)
				policy_choices.update({"auto": _("Auto")})
		except:
			print("[AVSwitch] Read /proc/stb/video/policy_choices failed.")
	config.av.policy_43 = ConfigSelection(choices=policy_choices, default="scale")
	config.av.tvsystem = ConfigSelection(choices={"pal": "PAL", "ntsc": "NTSC", "multinorm": "multinorm"}, default="pal")
	config.av.wss = ConfigEnableDisable(default=True)
	config.av.generalAC3delay = ConfigSelectionNumber(-1000, 1000, 5, default=0)
	config.av.generalPCMdelay = ConfigSelectionNumber(-1000, 1000, 5, default=0)
	config.av.vcrswitch = ConfigEnableDisable(default=False)

	iAVSwitch = AVSwitch()

	def setColorFormat(configElement):
		if model == "et6x00":
			map = {"cvbs": 3, "rgb": 3, "svideo": 2, "yuv": 3}
		elif model == "gb7356" or model.startswith('et'):
			map = {"cvbs": 0, "rgb": 3, "svideo": 2, "yuv": 3}
		else:
			map = {"cvbs": 0, "rgb": 1, "svideo": 2, "yuv": 3}
		iAVSwitch.setColorFormat(map[configElement.value])

	def setAspectRatio(configElement):
		map = {"4_3_letterbox": 0, "4_3_panscan": 1, "16_9": 2, "16_9_always": 3, "16_10_letterbox": 4, "16_10_panscan": 5, "16_9_letterbox": 6}
		iAVSwitch.setAspectRatio(map[configElement.value])

	def setWSS(configElement):
		iAVSwitch.setAspectWSS()

	# this will call the "setup-val" initial
	config.av.colorformat.addNotifier(setColorFormat)
	config.av.aspectratio.addNotifier(setAspectRatio)

	config.av.wss.addNotifier(setWSS)

	iAVSwitch.setInput("ENCODER")  # init on startup
	if model in ("gb7356", "et5x00", "et6x00", "ixussone", "ixusszero", "axodin", "axase3", "optimussos1", "optimussos2", "gb800seplus", "gb800ueplus", "gbultrase", "gbultraue", "gbultraueh", "twinboxlcd"):
		detected = False
	else:
		detected = eAVControl.getInstance().hasScartSwitch()

	SystemInfo["ScartSwitch"] = detected

	if SystemInfo["HasBypassEdidChecking"]:
		choices = [
			("00000000", _("Off")),
			("00000001", _("On"))
		]
		default = "00000000"

		def setEDIDBypass(configElement):
			open(SystemInfo["HasBypassEdidChecking"], "w").write("00000001" if configElement.value else "00000000")
		config.av.bypass_edid_checking = ConfigSelection(choices=choices, default=default)
		config.av.bypass_edid_checking.addNotifier(setEDIDBypass)
	else:
		config.av.bypass_edid_checking = ConfigNothing()

	if SystemInfo["HasColorspace"]:
		if SystemInfo["HasColorspaceSimple"]:
			choices = [
				("Edid(Auto)", _("Auto")),
				("Hdmi_Rgb", _("RGB")),
				("444", _("YCbCr444")),
				("422", _("YCbCr422")),
				("420", _("YCbCr420"))
			]
			default = "Edid(Auto)"
		else:
			if model in ("vuzero4k", "dm900", "dm920"):
				choices = [
					("Edid(Auto)", _("Auto")),
					("Hdmi_Rgb", _("RGB")),
					("Itu_R_BT_709", _("BT709")),
					("DVI_Full_Range_RGB", _("Full Range RGB")),
					("FCC", _("FCC 1953")),
					("Itu_R_BT_470_2_BG", _("BT470 BG")),
					("Smpte_170M", _("SMPTE 170M")),
					("Smpte_240M", _("SMPTE 240M")),
					("Itu_R_BT_2020_NCL", _("BT2020 NCL")),
					("Itu_R_BT_2020_CL", _("BT2020 CL")),
					("XvYCC_709", _("BT709 XvYCC")),
					("XvYCC_601", _("BT601 XvYCC"))
				]
				default = "Edid(Auto)"
			else:
				choices = [
					("auto", _("Auto")),
					("rgb", _("RGB")),
					("420", "420"),
					("422", "422"),
					("444", "444")
				]
				default = "auto"

		def setHDMIColorspace(configElement):
			open(SystemInfo["HasColorspace"], "w").write(configElement.value)
		if SystemInfo["HasColorspaceChoices"] and SystemInfo["CanProc"]:
			with open(SystemInfo["HasColorspaceChoices"]) as hdmicolorspace:
				hdmicolorspace.read().split('\n', 1)[0]
		config.av.hdmicolorspace = ConfigSelection(choices=choices, default=default)
		config.av.hdmicolorspace.addNotifier(setHDMIColorspace)
	else:
		config.av.hdmicolorspace = ConfigNothing()

	if SystemInfo["HasColorimetry"]:
		choices = [
			("auto", _("Auto")),
			("bt2020ncl", _("BT 2020 NCL")),
			("bt2020cl", _("BT 2020 CL")),
			("bt709", _("BT 709"))
		]
		default = "auto"

		def setHDMIColorimetry(configElement):
			open(SystemInfo["HasColorimetry"], "w").write(configElement.value)
		if SystemInfo["HasColorimetryChoices"] and SystemInfo["CanProc"]:
			with open(SystemInfo["HasColorimetryChoices"]) as hdmicolorimetry:
				hdmicolorimetry.read().split('\n', 1)[0]
		config.av.hdmicolorimetry = ConfigSelection(choices=choices, default=default)
		config.av.hdmicolorimetry.addNotifier(setHDMIColorimetry)
	else:
		config.av.hdmicolorimetry = ConfigNothing()

	if SystemInfo["HasColordepth"]:
		choices = [
			("auto", _("Auto")),
			("8bit", _("8 bit")),
			("10bit", _("10 bit")),
			("12bit", _("12 bit"))
		]
		default = "auto"

		def setHdmiColordepth(configElement):
			open(SystemInfo["HasColordepth"], "w").write(configElement.value)
		if SystemInfo["HasColordepthChoices"] and SystemInfo["CanProc"]:
			with open(SystemInfo["HasColordepthChoices"]) as hdmicolordepth:
				hdmicolordepth.read().split('\n', 1)[0]
		config.av.hdmicolordepth = ConfigSelection(choices=choices, default=default)
		config.av.hdmicolordepth.addNotifier(setHdmiColordepth)
	else:
		config.av.hdmicolordepth = ConfigNothing()

	if SystemInfo["HasHdrType"]:
		def setHdmiHdrType(configElement):
			try:
				with open(SystemInfo["HasHdrType"], "w") as hdmihdrtype:
					hdmihdrtype.write(configElement.value)
			except (IOError, OSError):
				print("[AVSwitch] Write to /proc/stb/video/hdmi_hdrtype failed!")
		config.av.hdmihdrtype = ConfigSelection(choices={
			"auto": _("Auto"),
			"dolby": _("Dolby"),
			"none": _("SDR"),
			"hdr10": _("HDR10"),
			"hlg": _("HLG")
		}, default="auto")
		config.av.hdmihdrtype.addNotifier(setHdmiHdrType)
	else:
		config.av.hdmihdrtype = ConfigNothing()

	if SystemInfo["HasHDMIpreemphasis"]:
		def setHDMIpreemphasis(configElement):
			open(SystemInfo["HasHDMIpreemphasis"], "w").write("on" if configElement.value else "off")
		config.av.hdmipreemphasis = ConfigYesNo(default=False)
		config.av.hdmipreemphasis.addNotifier(setHDMIpreemphasis)

	if SystemInfo["HDRSupport"]:
		config.av.hlg_support = ConfigSelection(default="auto(EDID)", choices=[
			("auto(EDID)", _("Controlled by HDMI")),
			("yes", _("Force enabled")),
			("no", _("Force disabled"))
		])

		def setHlgSupport(configElement):
			try:
				open("/proc/stb/hdmi/hlg_support", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/hdmi/hlg_support failed!")
		config.av.hlg_support.addNotifier(setHlgSupport)

		config.av.hdr10_support = ConfigSelection(default="auto(EDID)", choices=[
			("auto(EDID)", _("Controlled by HDMI")),
			("yes", _("Force enabled")),
			("no", _("Force disabled"))
		])

		def setHdr10Support(configElement):
			try:
				open("/proc/stb/hdmi/hdr10_support", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/hdmi/hdr10_support failed!")
		config.av.hdr10_support.addNotifier(setHdr10Support)

		def setDisable12Bit(configElement):
			try:
				open("/proc/stb/video/disable_12bit", "w").write("1" if configElement.value else "0")
			except:
				print("[AVSwitch] Write to /proc/stb/video/disable_12bit failed!")
		config.av.allow_12bit = ConfigYesNo(default=False)
		config.av.allow_12bit.addNotifier(setDisable12Bit)

		def setDisable10Bit(configElement):
			try:
				open("/proc/stb/video/disable_10bit", "w").write("1" if configElement.value else "0")
			except:
				print("[AVSwitch] Write to /proc/stb/video/disable_10bit failed!")
		config.av.allow_10bit = ConfigYesNo(default=False)
		config.av.allow_10bit.addNotifier(setDisable10Bit)

	if SystemInfo["HDMIAudioSource"]:
		config.av.hdmi_audio_source = ConfigSelection(default="pcm", choices={
			"pcm": _("PCM"),
			"spdif": _("SPDIF")
		})

		def setAudioSource(configElement):
			try:
				with open(SystemInfo["HDMIAudioSource"], "w") as hdmi_audio_source:
					hdmi_audio_source.write(configElement.value)
					hdmi_audio_source.close()
			except (IOError, OSError):
				pass
		config.av.hdmi_audio_source.addNotifier(setAudioSource)
	else:
		config.av.hdmi_audio_source = ConfigNothing()

	if SystemInfo["CanSyncMode"]:
		config.av.sync_mode = ConfigSelection(default="slow", choices={
			"slow": _("Slow motion"),
			"hold": _("Hold first frame"),
			"black": _("Black screen")
		})

		def setSyncMode(configElement):
			try:
				with open(SystemInfo["CanSyncMode"], "w") as syncmode:
					syncmode.write(configElement.value)
			except (IOError, OSError):
				print("[AVSwitch] Write to /proc/stb/video/sync_mode_choices failed!")
		config.av.sync_mode.addNotifier(setSyncMode)
	else:
		config.av.sync_mode = ConfigNothing()

	if SystemInfo["HasMultichannelPCM"]:
		def setPCMMultichannel(configElement):
			open(SystemInfo["HasMultichannelPCM"], "w").write(configElement.value and "enable" or "disable")
		config.av.multichannel_pcm = ConfigYesNo(default=False)
		config.av.multichannel_pcm.addNotifier(setPCMMultichannel)

	if SystemInfo["CanDownmixAC3"]:
		default = "downmix"
		choices = [
			("downmix", _("Downmix")),
			("passthrough", _("Passthrough"))
		]

		def setAC3Downmix(configElement):
			with open("/proc/stb/audio/ac3", "w") as trackac3:
				trackac3.write(configElement.value)
				trackac3.close()
			if SystemInfo.get("HasMultichannelPCM", False) and configElement.value == "passthrough":
				SystemInfo["CanPcmMultichannel"] = True
			else:
				SystemInfo["CanPcmMultichannel"] = False

		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/ac3_choices") as ac3_choices:
				ac3_choices.read().split('\n', 1)[0]
		config.av.downmix_ac3 = ConfigSelection(choices=choices, default=default)
		config.av.downmix_ac3.addNotifier(setAC3Downmix)

	if SystemInfo["CanDownmixAAC"]:
		choices = [
			("downmix", _("Downmix")),
			("passthrough", _("Passthrough"))
		]
		default = "downmix"

		def setAACDownmix(configElement):
			try:
				open("/proc/stb/audio/aac", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/aac failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/aac_choices") as aac_choices:
				aac_choices.read().split('\n', 1)[0]
		config.av.downmix_aac = ConfigSelection(choices=choices, default=default)
		config.av.downmix_aac.addNotifier(setAACDownmix)

	if SystemInfo["CanDownmixAACPlus"]:
		choices = [
			("downmix", _("Downmix")),
			("passthrough", _("Passthrough")),
			("multichannel", _("Convert to multi-channel PCM")),
			("force_ac3", _("Convert to AC3")),
			("force_dts", _("Convert to DTS")),
			("use_hdmi_cacenter", _("Use HDMI cacenter")),
			("wide", _("Wide")),
			("extrawide", _("Extra wide"))
		]
		default = "downmix"

		def setAACDownmixPlus(configElement):
			try:
				open("/proc/stb/audio/aacplus", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/aacplus failed!")
		if SystemInfo["CanProc"]:
			with open(SystemInfo["CanDownmixAACPlus"]) as aacplus_choices:
				aacplus_choices.read().split('\n', 1)[0]
		config.av.downmix_aacplus = ConfigSelection(choices=choices, default=default)
		config.av.downmix_aacplus.addNotifier(setAACDownmixPlus)

	if SystemInfo["CanDownmixDTS"]:
		choices = [
			("downmix", _("Downmix")),
			("passthrough", _("Passthrough"))
		]
		default = "downmix"

		def setDTSDownmix(configElement):
			try:
				open("/proc/stb/audio/dts", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/dts failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/dts_choices") as dts_choices:
				dts_choices.read().split('\n', 1)[0]
		config.av.downmix_dts = ConfigSelection(choices=choices, default=default)
		config.av.downmix_dts.addNotifier(setDTSDownmix)

	if SystemInfo["CanDTSHD"]:
		if model not in ("dm7080", "dm820"):
			choices = [
				("downmix", _("Downmix")),
				("force_dts", _("Convert to DTS")),
				("use_hdmi_caps", _("Controlled by HDMI")),
				("multichannel", _("Convert to multi-channel PCM")),
				("hdmi_best", _("Use best / Controlled by HDMI"))
			]
			default = "downmix"
		else:
			choices = [
				("use_hdmi_caps", _("Controlled by HDMI")),
				("force_dts", _("Convert to DTS"))
			]
			default = "use_hdmi_caps"

		def setDTSHD(configElement):
			try:
				open("/proc/stb/audio/dtshd", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/dtshd failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/dtshd_choices") as dtshd_choices:
				dtshd_choices.read().split('\n', 1)[0]
		config.av.dtshd = ConfigSelection(choices=choices, default=default)
		config.av.dtshd.addNotifier(setDTSHD)

	if SystemInfo["CanAACTranscode"]:
		choices = [
			("off", _("Off")),
			("ac3", _("AC3")),
			("dts", _("DTS"))
		]
		default = "off"

		def setAACTranscode(configElement):
			try:
				open("/proc/stb/audio/aac_transcode", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/aac_transcode failed!")
		if SystemInfo["CanProc"]:
			with open(SystemInfo["CanAACTranscode"]) as aac_transcode_choices:
				aac_transcode_choices.read().split('\n', 1)[0]
		config.av.transcodeaac = ConfigSelection(choices=choices, default=default)
		config.av.transcodeaac.addNotifier(setAACTranscode)
	else:
		config.av.transcodeaac = ConfigNothing()

	if SystemInfo["CanAC3PlusTranscode"]:
		if not SystemInfo["DreamBoxAudio"] and model not in ("gb7252", "gb72604"):
			choices = [
				("use_hdmi_caps", _("Controlled by HDMI")),
				("force_ac3", _("Convert to AC3"))
			]
			default = "force_ac3"
		elif SystemInfo["DreamBoxAudio"]:
			choices = [
				("use_hdmi_caps", _("Controlled by HDMI")),
				("force_ac3", _("Convert to AC3")),
				("multichannel", _("Convert to multi-channel PCM")),
				("hdmi_best", _("Use best / Controlled by HDMI")),
				("force_ddp", _("Force AC3+"))
			]
			default = "force_ac3"
		else:
			choices = [
				("downmix", _("Downmix")),
				("passthrough", _("Passthrough")),
				("force_ac3", _("Convert to AC3")),
				("multichannel", _("Convert to multi-channel PCM")),
				("force_dts", _("Convert to DTS"))
			]
			default = "force_ac3"

		def setAC3plusTranscode(configElement):
			try:
				open("/proc/stb/audio/ac3plus", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/ac3plus failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/ac3plus_choices") as ac3plus_choices:
				ac3plus_choices.read().split('\n', 1)[0]
		config.av.transcodeac3plus = ConfigSelection(choices=choices, default=default)
		config.av.transcodeac3plus.addNotifier(setAC3plusTranscode)

	if SystemInfo["CanWMAPRO"]:
		choices = [
			("downmix", _("Downmix")),
			("passthrough", _("Passthrough")),
			("multichannel", _("Convert to multi-channel PCM")),
			("hdmi_best", _("Use best / Controlled by HDMI"))
		]
		default = "downmix"

		def setWMAPRO(configElement):
			open(SystemInfo["CanWMAPRO"], "w").write(configElement.value)
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/wmapro_choices") as wmapro_choices:
				wmapro_choices.read().split('\n', 1)[0]
		config.av.wmapro = ConfigSelection(choices=choices, default=default)
		config.av.wmapro.addNotifier(setWMAPRO)

	if SystemInfo["CanAudioDelay"]:
		def setAudioDelay(configElement):
			try:
				with open("/proc/stb/audio/audio_delay", "w") as fd:
					fd.write(format(configElement.value * 90, "x"))
			except:
				SystemInfo["CanAudioDelay"] = False
		config.av.audiodelay = ConfigSelectionNumber(-1000, 1000, 5, default=0)
		config.av.audiodelay.addNotifier(setAudioDelay)
	else:
		config.av.audiodelay = ConfigNothing()

	if SystemInfo["CanBTAudio"]:
		choices = [
			("off", _("Off")),
			("on", _("On"))
		]
		default = "off"

		def setBTAudio(configElement):
			open(SystemInfo["CanBTAudio"], "w").write(configElement.value)
		config.av.btaudio = ConfigSelection(choices=choices, default="off")
		config.av.btaudio.addNotifier(setBTAudio)
	else:
		config.av.btaudio = ConfigNothing()

	if SystemInfo["CanBTAudioDelay"]:
		def setBTAudioDelay(configElement):
			try:
				with open("/proc/stb/audio/btaudio_delay", "w") as fd:
					fd.write(format(configElement.value * 90, "x"))
			except:
				SystemInfo["CanBTAudioDelay"] = False
		config.av.btaudiodelay = ConfigSelectionNumber(-1000, 1000, 5, default=0)
		config.av.btaudiodelay.addNotifier(setBTAudioDelay)
	else:
		config.av.btaudiodelay = ConfigNothing()

	if SystemInfo["Has3DSurround"]:
		choices = [
			("none", _("Off")),
			("hdmi", _("HDMI")),
			("spdif", _("SPDIF")),
			("dac", _("DAC"))
		]
		default = "none"

		def set3DSurround(configElement):
			try:
				open("/proc/stb/audio/3d_surround", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/3d_surround failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/3d_surround_choices") as surround:
				surround.read().split('\n', 1)[0]
		config.av.surround_3d = ConfigSelection(choices=choices, default=default)
		config.av.surround_3d.addNotifier(set3DSurround)
	else:
		config.av.surround_3d = ConfigNothing()

	if SystemInfo["Has3DSpeaker"]:
		choices = [
			("center", _("Center")),
			("wide", _("Wide")),
			("extrawide", _("Extra wide"))
		]
		default = "center"

		def set3DPosition(configElement):
			try:
				open("/proc/stb/audio/3d_surround_speaker_position", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/3d_surround_speaker_position failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/3d_surround_speaker_position_choices") as speaker:
				speaker.read().split('\n', 1)[0]
		config.av.speaker_3d = ConfigSelection(choices=choices, default=default)
		config.av.speaker_3d.addNotifier(set3DPosition)
	else:
		config.av.speaker_3d = ConfigNothing()

	if SystemInfo["Has3DSurroundSpeaker"]:
		choices = [
			("disabled", _("Off")),
			("center", _("Center")),
			("wide", _("Wide")),
			("extrawide", _("Extra wide"))
		]
		default = "disabled"

		def set3DPositionDisable(configElement):
			try:
				open("/proc/stb/audio/3dsurround", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/3dsurround failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/3dsurround_choices") as surroundspeaker:
				surroundspeaker.read().split('\n', 1)[0]
		config.av.surround_3d_speaker = ConfigSelection(choices=choices, default=default)
		config.av.surround_3d_speaker.addNotifier(set3DPositionDisable)
	else:
		config.av.surround_3d_speaker = ConfigNothing()

	if SystemInfo["HasAutoVolume"]:
		choices = [
			("none", _("Off")),
			("hdmi", _("HDMI")),
			("spdif", _("SPDIF")),
			("dac", _("DAC"))
		]
		default = "none"

		def setAutoVolume(configElement):
			try:
				open("/proc/stb/audio/avl", "w").write(configElement.value)
			except:
				print("[AVSwitch] Write to /proc/stb/audio/avl failed!")
		if SystemInfo["CanProc"]:
			with open("/proc/stb/audio/avl_choices") as avl_choices:
				avl_choices.read().split('\n', 1)[0]
		config.av.autovolume = ConfigSelection(choices=choices, default=default)
		config.av.autovolume.addNotifier(setAutoVolume)
	else:
		config.av.autovolume = ConfigNothing()

	if SystemInfo["HasAutoVolumeLevel"]:
		def setAutoVolumeLevel(configElement):
			try:
				open("/proc/stb/audio/autovolumelevel_choices", "w").write("enabled" if configElement.value else "disabled")
			except:
				print("[AVSwitch] Write to /proc/stb/audio/autovolumelevel_choices failed!")
		config.av.autovolumelevel = ConfigYesNo(default=False)
		config.av.autovolumelevel.addNotifier(setAutoVolumeLevel)

	if SystemInfo["ScalerSharpness"]:
		def setScaler_sharpness(config):
			myval = int(config.value)
			try:
				print("--> setting scaler_sharpness to: %0.8X" % myval)
				print("[AVSwitch] Write to /proc/stb/vmpeg/0/pep_scaler_sharpness")
				open("/proc/stb/vmpeg/0/pep_scaler_sharpness", "w").write("%0.8X" % myval)
				print("[AVSwitch] Write to /proc/stb/vmpeg/0/pep_apply")
				open("/proc/stb/vmpeg/0/pep_apply", "w").write("1")
			except IOError:
				print("[AVSwitch] Couldn't write pep_scaler_sharpness or pep_apply")

		if platform == "gb7356":
			config.av.scaler_sharpness = ConfigSlider(default=5, limits=(0, 26))
		else:
			config.av.scaler_sharpness = ConfigSlider(default=13, limits=(0, 26))
		config.av.scaler_sharpness.addNotifier(setScaler_sharpness)
	else:
		config.av.scaler_sharpness = NoSave(ConfigNothing())

	if SystemInfo["Has3DSurroundSoftLimiter"]:
		def set3DSurroundSoftLimiter(configElement):
			try:
				open("/proc/stb/audio/3dsurround_softlimiter", "w").write(configElement.value and "enabled" or "disabled")
			except:
				print("[AVSwitch] Write to /proc/stb/audio/3dsurround_softlimiter failed!")
		config.av.surround_softlimiter_3d = ConfigYesNo(default=False)
		config.av.surround_softlimiter_3d.addNotifier(set3DSurroundSoftLimiter)

	def setVolumeStepsize(configElement):
		eDVBVolumecontrol.getInstance().setVolumeSteps(int(configElement.value))
	config.av.volume_stepsize = ConfigSelectionNumber(1, 10, 1, default=5)
	config.av.volume_stepsize.addNotifier(setVolumeStepsize)

	if SystemInfo["CanChangeOsdAlpha"]:
		def setAlpha(config):
			try:
				open("/proc/stb/video/alpha", "w").write(str(config.value))
			except:
				print("[AVSwitch] Write to /proc/stb/video/alpha failed!")
		config.av.osd_alpha = ConfigSlider(default=255, limits=(0, 255))
		config.av.osd_alpha.addNotifier(setAlpha)

	if SystemInfo["CanChangeOsdPlaneAlpha"]:
		def setOSDPlaneAlpha(config):
			try:
				open("/sys/class/graphics/fb0/osd_plane_alpha", "w").write(hex(config.value))
			except:
				print("[AVSwitch] Write to /sys/class/graphics/fb0/osd_plane_alpha failed!")
		config.av.osd_planealpha = ConfigSlider(default=255, limits=(0, 255))
		config.av.osd_planealpha.addNotifier(setOSDPlaneAlpha)
