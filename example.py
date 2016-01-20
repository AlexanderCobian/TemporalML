
class Example(object):

	def __init__(self,id,left_cutoff_date=None,right_cutoff_date=None):
		self.id = id
		self.static_features = dict()
		self.events = dict()
		self.left_cutoff_date = left_cutoff_date
		self.right_cutoff_date = right_cutoff_date

	def add_event(self,event_name,start_date,end_date=None):
		# set end date to start date for single-date events
		if end_date == None:
			end_date == start_date
		if event_name not in self.events:
			self.events[event_name] = []
		self.events[event_name].append((start_date,end_date))
	
	def create_example_moment(self,moment):
		return Example_Moment(self,moment)

class Example_Moment(object):
	
	def __init__(self,example,moment):
		self.example = example
		self.moment = moment