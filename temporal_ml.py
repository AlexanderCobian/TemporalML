
import datetime

class Example(object):

	def __init__(self,id):
		self.id = id
		self.static_values = dict()
		self.events = dict()

	def add_event(self,event_name,event_time):
		if event_name not in self.events:
			self.events[event_name] = []
		self.events[event_name].append(event_time)
	
	def create_example_moment(self,moment):
		return Example_Moment(self,moment)

class Example_Moment(object):
	
	def __init__(self,example,moment):
		self.example = example
		self.moment = moment
	
	def times_since_occurrence(self,event):
		differences = [self.moment-occurrence for occurrence in self.example.events[event]]
		
		# convert timedeltas to day integers so that absolute and relative times can both be used
		if type(self.moment) == datetime.timedelta:
			differences = [x.days for x in differences]
			
		return [float(x) for x in differences]

class Feature(object):
	
	def __init__(self,feature_name,feature_type):
		self.feature_name = feature_name
		self.feature_type = feature_type

class Feature_Static(Feature):

	def __init__(self,feature_name,static_name):
		Feature.__init__(self,feature_name,"Static")
		self.static_name = static_name
	
	def query(self,example_moment):
		return example_moment.example.static_values[self.static_name]

class Feature_LastOccurrence(Feature):
	
	def __init__(self,feature_name,*event_names):
		Feature.__init__(self,feature_name,"LastOccurrence")
		self.event_names = event_names
	
	def query(self,example_moment):
		result = float("Inf")
		for event in self.event_names:
			times_since = example_moment.times_since_occurrence(event)
			pos_times_since = [x for x in times_since if x >= 0.0]
			if len(pos_times_since) > 0:
				result = min(result,min(pos_times_since))
		return result

# obviously, this feature type should only be used for example-moments with
# date or datetime moments
class Feature_MonthDay(Feature):
	
	# monthday_to_value should be a dict mapping tuples to floats
	def __init__(self,feature_name,monthday_to_value):
		Feature.__init__(self,feature_name,"Monthday")
		self.monthday_to_value
	
	def query(self,example_moment):
		month = example_moment.moment.month
		day = example_moment.moment.day
		return self.monthday_to_value[(month,day)]

class Feature_NextOccurrence(Feature):

	def __init__(self,feature_name,*event_names):
		Feature.__init__(self,feature_name,"NextOccurrence")
		self.event_names = event_names
	
	def query(self,example_moment):
		result = float("Inf")
		for event in self.event_names:
			times_since = example_moment.times_since_occurrence(event)
			pos_times_until = [-x for x in times_since if x <= 0.0]
			if len(pos_times_until) > 0:
				result = min(result,min(pos_times_until))
		return result