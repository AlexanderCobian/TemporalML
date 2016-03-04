
from tree_learning import *
import random

class Simple_Example(object):

	def __init__(self,label,weight=1.0):
		self.label = label
		self.weight = weight
		self.features = dict()

class Simple_Feature(object):

	def __init__(self,name):
		self.feature_name = name
	
	def query(self,simple_example):
		return simple_example.features[self.feature_name]
	
	def __repr__(self):
		return self.feature_name

examples = []
for i in range(100):
	examples.append(Simple_Example("+"))
for i in range(100):
	examples.append(Simple_Example("-"))


features = []
for i in range(1,21):
	correlation = float(i) / 100.0
	feature_name = "Correlation_{0}%".format(int(correlation*100))
	features.append(Simple_Feature(feature_name))
	for example in examples:
		random_value = random.random()
		feature_value = correlation + ((1.0-correlation)*random_value)
		if example.label == "-":
			feature_value = 1.0-feature_value
		example.features[feature_name] = feature_value

print build_classification_tree(features,examples,verbosity=1).tree_summary(max_depth=5)