
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
		# moment - occurrence, so PAST occurrences are positive
		differences = [self.moment-occurrence for occurrence in self.example.events[event]]
		
		# convert timedeltas to day integers so that absolute and relative times can both be used
		if type(self.moment) == datetime.timedelta:
			differences = [x.days for x in differences]
			
		return [float(x) for x in differences if x >= 0.0]
	
	def times_until_occurrence(self,event):
		# occurrence - moment, so FUTURE occurrences are positive
		differences = [occurrence-self.moment for occurrence in self.example.events[event]]
		
		# convert timedeltas to day integers so that absolute and relative times can both be used
		if type(self.moment) == datetime.timedelta:
			differences = [x.days for x in differences]
		
		return [float(x) for x in differences if x >= 0.0]
	
	def compute_label_and_weight(self,classlabel_feature):
		(self.label,self.weight) = classlabel_feature.query(self)

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
			for time_since in example_moment.times_since_occurrence(event):
				result = min(result,time_since)
		return result

class Feature_2ndLastOccurrence(Feature):
	
	def __init__(self,feature_name,*event_names):
		Feature.__init__(self,feature_name,"2ndLastOccurrence")
		self.event_names = event_names
	
	def query(self,example_moment):
		result = float("Inf")
		all_times_since = []
		for event in self.event_names:
			times_since = example_moment.times_since_occurrence(event)
			all_times_since += times_since
		if len(all_times_since) >= 2:
			all_times_since.remove(min(all_times_since))
			result = min(all_times_since)
		return result


# "salience" here being a measure that combines event frequency and recency via exponential decay

class Feature_Salience(Feature):
	
	def __init__(self,feature_name,decay_rate,*event_names_and_weights):
		Feature.__init__(self,feature_name,"Salience")
		self.decay_rate = decay_rate
		self.event_names = []
		self.event_weights = []
		while len(event_names_and_weights) > 0:
			self.event_names.append(event_names_and_weights.pop(0))
			self.event_weights.append(float(event_names_and_weights.pop(0)))
	
	def query(self,example_moment):
		time_weight_pairs = []
		
		for i in range(len(self.event_names)):
			event_name = self.event_names[i]
			event_weight = self.event_weights[i]
			for occurrence in example_moment.times_since_occurrence(event_name):
				time_weight_pairs.append((occurrence,event_weight))
		
		sorted_time_weight_pairs = sorted(time_weight_pairs,reverse=True)
		
		weights = [x[1] for x in sorted_time_weight_pairs]
		time_gaps = []
		i = 1
		while i < len(sorted_time_weight_pairs):
			time_gaps.append(sorted_time_weight_pairs[i-1][0] - sorted_time_weight_pairs[i][0])
		if len(sorted_time_weight_pairs) > 0:
			time_gaps.append(sorted_time_weight_pairs[-1][0])
		
		salience = 0.0
		for i in range(len(weights)):
			
			# additive increase
			salience += weights[i]
			
			# exponential decay
			multiplicative_factor = (1 - self.decay_rate) ** time_gaps[i]
			salience *= multiplicative_factor
		
		return salience

class Feature_OccurrenceCount(Feature):
	
	def __init__(self,feature_name,*event_names):
		Feature.__init__(self,feature_name,"OccurrenceCount")
		self.event_names = event_names
	
	def query(self,example_moment):
		all_count = 0
		for event in self.event_names:
			count += len(example_moment.times_since_occurrence(event))
		return all_count

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

# querying a ClassLabel Feature returns a (label,weight) pair, label in {+,-}, weight 0.0+
# ClassLabel features are unweighted (all weights 1.0) unless otherwise specified

class Feature_ClassLabel_ImpendingEvent(Feature):

	def __init__(self,feature_name,future_threshold,*event_names):
		Feature.__init__(self,feature_name,"ClassLabel_ImpendingEvent")
		self.future_threshold = future_threshold
		self.event_names = event_names
	
	def query(self,example_moment):
		next_occurrence = float("Inf")
		for event in self.event_names:
			for time_until in example_moment.times_until_occurrence(event):
				next_occurrence = min(next_occurrence,time_until)
		if next_occurrence <= self.future_threshold:
			return ("+",1.0)
		else:
			return ("-",1.0)

class Feature_ClassLabel_ImpendingEvent_LinearWeight(Feature):

	def __init__(self,feature_name,zero_weight_threshold,*event_names):
		Feature.__init__(self,feature_name,"ClassLabel_ImpendingEvent_LinearWeight")
		self.zero_weight_threshold = zero_weight_threshold
		self.event_names = event_names
	
	def query(self,example_moment):
		next_occurrence = float("Inf")
		for event in self.event_names:
			for time_until in example_moment.times_until_occurrence(event):
				next_occurrence = min(next_occurrence,time_until)
		if next_occurrence >= zero_weight_threshold * 2:
			return ("-",1.0)
		elif next_occurrence >= zero_weight_threshold:
			weight = (next_occurrence-zero_weight_threshold)/(zero_weight_threshold)
			return ("-",weight)
		else:
			weight = (zero_weight_threshold-next_occurrence)/(zero_weight_threshold)
			return ("+",weight)
		