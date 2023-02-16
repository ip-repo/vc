import sys, os
from app_objects.workers_and_signals import VolumeChecker
from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtGui import QCloseEvent, QShortcut, QKeySequence, QWheelEvent, QPixmap, QHideEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QProgressBar



class Widget(QWidget):
	"""
	Widget object is the gui part of the app.
	The user will see a gui window, label ,proggress bar and button.
	The information that user see is the default sink data.
	
	Widgets:
		The label show the sink sate.
		The proggress bar show the current sink volume.
		The button show the current volume and allow user to mute or unmute.
	
	"""
	#inits
	def __init__(self) -> None:
		"""
		__init__ create the app widgets, call other init methods and start the worker.
		"""
		super().__init__()

		self.screen_size = self.screen().availableSize()

		self.state_label = QLabel("")
		self.state_label.setAlignment(Qt.AlignCenter)

		self.proggress_bar = QProgressBar()
		self.proggress_bar.setRange(0,100)
		self.proggress_bar.setTextVisible(False)

		self.volume_button = QPushButton("")

		self.init_ui()
		self.init_shortcuts()

		self.volume_button.clicked.connect(self.mute)	
		
		self.thread_pool = QThreadPool()
		
		self.worker = VolumeChecker()
		self.worker.signals.data_signal.connect(self.update_gui)
		
		self.thread_pool.start(self.worker)

	def init_ui(self) -> None:
		"""
		init_ui adjust widget size and set the widget layout.
		"""
		self.setFixedSize(self.screen_size.width() * 0.183, self.screen_size.height() * 0.048)
		self.state_label.setFixedSize(self.width() * 0.15,self.height() * 0.7)
		self.proggress_bar.setFixedSize(self.width() * 0.66 ,self.height() * 0.7)
		self.volume_button.setFixedSize(self.width() * 0.12,self.height() * 0.7)

		horizontal_layout = QHBoxLayout()
		horizontal_layout.setContentsMargins(2,2,2,2)
		horizontal_layout.addWidget(self.state_label)
		horizontal_layout.addWidget(self.proggress_bar)
		horizontal_layout.addWidget(self.volume_button)
		self.setLayout(horizontal_layout)

	def init_shortcuts(self) -> None:
		"""
		init_shortcut create shortcut functionality for the widget.
		mute: press M to mute or unmute.
		vol_down: press Left arrow for volume down.
		vol_up: press Right arrow for volume up.
		hide: press H to hide the app window.
		quit: press Q to quit the app.

		"""
		#shortcuts
		self.sh_mute = QShortcut(QKeySequence(Qt.Key_M), self)
		self.sh_vol_down = QShortcut(QKeySequence(Qt.Key.Key_Left),self)
		self.sh_vol_up = QShortcut(QKeySequence(Qt.Key.Key_Right),self)
		self.sh_hide = QShortcut(QKeySequence(Qt.Key_H), self)
		self.sh_quit = QShortcut(QKeySequence(Qt.Key_Q), self)
		#shortcuts signals
		self.sh_mute.activated.connect(self.mute)
		self.sh_vol_down.activated.connect(self.volume_down)
		self.sh_vol_up.activated.connect(self.volume_up)
		self.sh_hide.activated.connect(self.hide)
		self.sh_quit.activated.connect(self.force_quit)
		self.shortcut_tip = """Shortcuts:\n\tM - mute/unmute\n\tWheel Down/Left Arrow - volume down 5/10\n\tWheel Up/Right Arrow - volume up 5/10\
		\n\tH - hide window\n\tQ - terminate app"""
	
	#recive data from worker
	def update_gui(self, *data) -> None:
		"""
		update_gui is called everytime that the worker send a data_signal.
		this method update the label, proggress bar and button values.
		the sink data is saved under self.sink_data for later use.
		widgets tool tips are also defined. 

		Args:
			data(tupel): data = (sink_data(dict), )

		"""
		state_tool_tip = "Default Sink Info:\n"
		sink_data = data[0]

		state_tool_tip += "\tName: " + sink_data["name"] + "\n"
		#self.setWindowTitle(sink_data["name"])
		self.setWindowTitle("System Volume")
		
		state_tool_tip += "\tState: " + sink_data["state"] + "\n"
		self.state_label.setText(sink_data["state"])
		
		
		self.proggress_bar.setValue(sink_data["volume"][1])
		self.proggress_bar.setToolTip(sink_data["volume"][0].replace("\t"," ").strip())

		if sink_data["mute"] == False:
			state_tool_tip +="\tMuted: " + "no" + "\n"
			self.volume_button.setText(str(sink_data["volume"][1]))
			self.volume_button.setToolTip("Click to mute")
		
		else:
			state_tool_tip +="\tMuted: " + "yes" + "\n"
			self.volume_button.setText("X")
			self.volume_button.setToolTip("Click to unmute")
		state_tool_tip += "\tVolume: " + sink_data["volume"][0] + "\n"
		state_tool_tip += self.shortcut_tip
		self.state_label.setToolTip(state_tool_tip)

		self.sink_data = sink_data
						
	#event modification
	def closeEvent(self, event: QCloseEvent)-> None:
		"""
		when close event occur the widget window is closed and app terminate.
		to avoid the termination the QCloseEvent is ignored.
		then hide is called to hide the window.
		"""
		event.ignore()
		return super().hide()

	def wheelEvent(self, event: QWheelEvent) -> None:
		"""
		when user use the wheel the sink volume will be updated according to wheel direction and intravel value.
		wheel up: increase volume by 5.
		wheel down: decrease volume by 5.
		"""
		if self.volume_button.text() == "muted":
			return super().wheelEvent(event)

		wheel_direction = event.angleDelta().y()
		current_value = int(self.volume_button.text())
		interval = 5
		if wheel_direction < 0:
			new = current_value - interval
			if new < 0:
				new = 0
			command = "pactl set-sink-volume" + " "  + self.sink_data["name"] + " " + str(new) + "%"
			os.system(command)
		else:
			new = current_value + interval
			if new > 100:
				new = 100
			command = "pactl set-sink-volume" + " "  + self.sink_data["name"] + " " + str(new) + "%"
			os.system(command)
		return super().wheelEvent(event)

	#class methods
	def volume_down(self) -> None:
		"""
		volume_down is called every time user press on Left arrow and will decrease sink volume by 10.
		"""
		current_value = int(self.volume_button.text())
		interval = 10
		new = current_value - interval
		if new < 0:
			new = 0
		command = "pactl set-sink-volume" + " "  + self.sink_data["name"] + " " + str(new) + "%"
		os.system(command)
	
	def volume_up(self) -> None:
		"""
		volume_up is called every time user press on Right arrow and will increase sink volume by 10.
		"""
		current_value = int(self.volume_button.text())
		interval = 10
		new = current_value + interval
		if new > 100:
			new = 100
		command = "pactl set-sink-volume" + " "  + self.sink_data["name"] + " " + str(new) + "%"
		os.system(command)

	def mute(self) -> None:
		"""
		mute function is executed every time volume_button is clicked and
		its goal is to mute or unmute the sink.
		to achive that functionality the 'pactl get-sink-mute SINKNAME' command give
		a result that can be parsed to know if sink is muted.
		"""
		command = "pactl get-sink-mute " + self.sink_data["name"]
		result = os.popen(command).read().split(":")[1].strip()
		if result == "no":
			command = "pactl set-sink-mute " + self.sink_data["name"] + " true"
			os.system(command)
		else:
			command = "pactl set-sink-mute " + self.sink_data["name"] + " false"
			os.system(command)

	def force_quit(self) -> None:
		"""
		force_quit is called when the 'Quit' action is clicked and terminate the app.
		"""
		self.worker.do_work_flag = False
		sys.exit()