
import math
import random
from temporal_ml import *

class LogReg_Model:

	def __init__(self,features):
		self.intercept_weight = 0.0
		self.features = features
		self.feature_weights = dict()
		for name in [x.feature_name for x in features]:
			self.feature_weights[name] = 0.0
	
	def train(self,training_examples,tuning_examples,learning_rate = 0.01,learning_rate_decay_rate = 0.01):
		
		
		
		tuning_error_rates = [float("inf")]
		tuning_error_rates.append(self.compute_average_error(tuning_examples))
		training_error_rates = []
		training_error_rates.append(self.compute_average_error(training_examples))
		
		current_learning_rate = learning_rate
		
		print "Iter\tTrainErr\tTuneErr"
		print "0\t{0}\t{1}".format(training_error_rates[-1],tuning_error_rates[-1])
		
		iteration_count = 0
		
		while tuning_error_rates[-1] < tuning_error_rates[-2]:
			self.training_iteration(training_examples,current_learning_rate)
			current_learning_rate = current_learning_rate * (1.0-learning_rate_decay_rate)
			tuning_error_rates.append(self.compute_average_error(tuning_examples))
			training_error_rates.append(self.compute_average_error(training_examples))
			iteration_count += 1
			print "{0}\t{1}\t{2}".format(iteration_count,training_error_rates[-1],tuning_error_rates[-1])
		
	def training_iteration(self,training_examples,iteration_learning_rate):
		
		example_indexes = range(len(training_examples))
		random.shuffle(example_indexes)
		
		for example_index in example_indexes:
			
			example = training_examples[example_index]
			
			prediction = self.query(example)
			error = target(example) - prediction
			
			# update weights based on example error
			self.incercept_weight = self.intercept_weight + (iteration_learning_rate * error * prediction * (1.0-prediction))
			for feature_index in range(len(self.feature_weights)):
				feature_name = self.features[feature_index].feature_name
				self.feature_weights[feature_name] = self.feature_weights[feature_name] + (iteration_learning_rate * error * prediction * (1.0-prediction) * self.features[feature_index].query(example))
	
	def compute_average_error(self,tuning_examples):
		sum_tuning_error = 0.0
		for example in tuning_examples:
			prediction = self.query(example)
			error = abs(target(example) - prediction)
			sum_tuning_error += error
		return sum_tuning_error/len(tuning_examples)
	
	def query(self,query_instance):
		output = self.intercept_weight
		for feature in self.features:
			x = feature.query(query_instance)
			w = self.feature_weights[feature.feature_name]
			
			output += x*w
		prediction = 1.0 / (1.0 + math.exp(-output))
		return prediction
	
def target(example):
	if example.label == "+":
		target = 0.5 + (example.weight*0.5)
	elif example.label == "-":
		target = 0.5 - (example.weight*0.5)
	return target