import time, os
from PySide6.QtCore import QObject, Signal, QRunnable, Slot


class Signals(QObject):
	"""
	Signals:
		data_signals(dict): emit a dict.

	"""

	data_signal = Signal(dict)
	

class VolumeChecker(QRunnable):
	"""
	VolumeChecker class is a QRunnable that will work in the background while the app is alive.

	run : contain a while loop and for every instance the default sink data is emited to the gui part.
	
	"""
	def __init__(self):
		"""
		__init__ will create a Signals object a flag for the run while loop and some variables to keep data.
		"""
		super(VolumeChecker, self).__init__()
		self.signals = Signals()
		self.do_work_flag = True
		self.sinks_data = None
		self.default_sink = None
		self.data_to_emit = None

	@Slot()
	def run(self) -> None:
		"""
		run is basically a while loop that calls other methods that prepare sink data to be emitted
		and then using the data_signal the collected sink data is emitted to main_widget.
		"""
		while self.do_work_flag:
			self.update_default_sink_name()
			self.update_sinks_data()
			self.prepare_data_to_emit()
		
			try:
				self.signals.data_signal.emit(self.data_to_emit)
				...
			except RuntimeError:
				print("RuntimeError")	
			finally:
				time.sleep(0.3)
				continue
					
	def update_default_sink_name(self) -> None:
		"""
		update_default_sink_name update the sink name stored at self.default_sink
		"""
		self.default_sink = os.popen("pactl get-default-sink").read().strip()
		
	def update_sinks_data(self) -> None:
		"""
		update_sinks_data is used to parse the output of the command 'pactl list sinks' into a dict and then
		this dict will be the new value of self.sinks_data.
		"""
		new_data = {}
		sink_counter = 0
		sinks_list = os.popen('pactl list  sinks').read()
		for sink in sinks_list.split("\n"):
			if "Sink #" in sink:
				new_data[sink_counter] = []
			if "State:" in sink:
				new_data[sink_counter].append(sink.split(":")[1].strip())
			if "Name:" in sink:
				new_data[sink_counter].append(sink.split(":")[1].strip())
			if "Mute:" in sink:		
				new_data[sink_counter].append(sink.split(":")[1].strip())
			if "Volume:" in sink:
				self.volume = sink
				new_data[sink_counter].append(sink)
			if "Format:" in sink:
				sink_counter +=1
		self.sinks_data = new_data
	
	def prepare_data_to_emit(self) -> None:
		"""
		prepare_data_to_emit create a new dict that will contain the default sink data 
		under self.data_to_emit.
		"""
		data_to_emit = {}
		for sink in self.sinks_data.keys():
			#print(self.sinks_data[sink])
			if self.sinks_data[sink][1] == self.default_sink:
				for i in range(len(self.sinks_data[sink])):
					if i == 0:
						data_to_emit["state"] = self.sinks_data[sink][i]
					if i == 1:
						data_to_emit["name"] = self.sinks_data[sink][i]
					if i == 2:
						if self.sinks_data[sink][i].lower() == 'yes':
							data_to_emit["mute"] = True
						else:
							data_to_emit["mute"] = False
					if i == 3:
						volume = int([elem.strip(" ")[:-1] for elem in self.sinks_data[sink][i].split("/") if "%" in elem][0])
						data_to_emit["volume"] = [self.sinks_data[sink][i],volume]
						break
				break
			else:
				continue
		self.data_to_emit = data_to_emit


					
 