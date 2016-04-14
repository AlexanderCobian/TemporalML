
import random
import math

# epsilon value prevents splitting when splitting would only reduce entropy by
# an amount explainable by rounding error
ENTROPY_EPSILON = 0.001

class Tree_Node(object):

	def __init__(self,path="X"):
		self.path = path
	
	def depth(self):
		return len(self.path)-1
	
	def process_leaf(self,pos_weight,neg_weight):
		self.leaf = True
		self.pos_weight = pos_weight
		self.neg_weight = neg_weight
	
	def process_nonleaf(self,split_feature,split_value):
		self.leaf = False
		self.split_feature = split_feature
		self.split_value = split_value
		self.left_child = Tree_Node(self.path+"L")
		self.right_child = Tree_Node(self.path+"R")
		return (self.left_child,self.right_child)
	
	# returned as (pos_weight,neg_weight)
	def subtree_weight(self):
		if self.leaf:
			return (self.pos_weight,self.neg_weight)
		else:
			left_subtree_weights = self.left_child.subtree_weight()
			right_subtree_weights = self.right_child.subtree_weight()
			pos_weights = left_subtree_weights[0] + right_subtree_weights[0]
			neg_weights = left_subtree_weights[1] + right_subtree_weights[1]
			return (pos_weights,neg_weights)
	
	def prediction(self):
		(pos_weight,neg_weight) = self.subtree_weight()
		return pos_weight/(pos_weight+neg_weight)
	
	def query(self,query_instance):
		if self.leaf:
			return self.prediction()
		else:
			if self.split_feature.query(query_instance) <= self.split_value:
				return self.left_child.query(query_instance)
			else:
				return self.right_child.query(query_instance)
	
	def tree_summary(self,max_depth=10):
		if self.leaf:
			return "{0} | Leaf: {1}\n".format(self.path,self.prediction())
		else:
			if self.depth() >= max_depth:
				tree_text = "{0} | ...\n".format(self.path)
				return tree_text
			tree_text = "{0} | {1} <= {2}\n".format(self.path,self.split_feature,self.split_value)
			tree_text += self.left_child.tree_summary(max_depth)
			tree_text += self.right_child.tree_summary(max_depth)
			return tree_text

# verbosity levels:
# 	1: print depth levels as they are reached
# 	2: print node paths and weight amounts when they are constructed
# 	3: print features as they are considered for splits
def build_classification_tree(features,instances,max_depth=-1,candidate_feature_proportion=.2,minimum_node_weight=0.0,verbosity=0,random_seed=None):
	
	if random_seed != None:
		random.seed(random_seed)
		
	
	root_node = Tree_Node()
	worklist = [(root_node,instances)]
	
	max_depth_reached = 0
	
	while worklist:
		
		(current_node, current_instances) = worklist.pop(0)
				
		if verbosity >= 1 and current_node.depth() > max_depth_reached:
			max_depth_reached = current_node.depth()
			print "Building depth {0}...".format(current_node.depth())
		
		pos_weight = 0.0
		neg_weight = 0.0
		for instance in current_instances:
			if instance.label == "+":
				pos_weight += instance.weight
			else:
				neg_weight += instance.weight
		
		if verbosity >= 2:
			print "Building node {0}, +{1}, -{2}...".format(current_node.path,pos_weight,neg_weight)
		
		# leaf because max depth? process and continue
		if current_node.depth() == max_depth:
			if verbosity >= 2:
				print "{0}: Leaf node, max depth reached".format(current_node.path)
			current_node.process_leaf(pos_weight,neg_weight)
			continue
		
		num_candidate_features = min(len(features),int(1+candidate_feature_proportion*len(features)))
		candidate_features = random.sample(features,num_candidate_features)
		
		best_split_entropy = entropy(pos_weight,neg_weight) - ENTROPY_EPSILON
		best_split_feature = None
		
		for candidate_feature_index in range(len(candidate_features)):
		
			candidate_feature = candidate_features[candidate_feature_index]
			
			if verbosity >= 3:
				print "{0}: Evaluating feature {1}/{2}: {3}".format(current_node.path,candidate_feature_index+1,len(candidate_features),candidate_feature)
			
			pos_left_weight = 0.0
			neg_left_weight = 0.0
			pos_right_weight = pos_weight
			neg_right_weight = neg_weight
			
			sorted_instances = sorted(current_instances,key=lambda x: candidate_feature.query(x))
			si_index = 0
			while si_index < len(sorted_instances):
			
				next_value = candidate_feature.query(sorted_instances[si_index])
				if sorted_instances[si_index].label == "+":
					pos_right_weight -= sorted_instances[si_index].weight
					pos_left_weight += sorted_instances[si_index].weight
				else:
					neg_right_weight -= sorted_instances[si_index].weight
					neg_left_weight += sorted_instances[si_index].weight
				si_index += 1
				
				# include any additional batch elements
				while si_index < len(sorted_instances) and candidate_feature.query(sorted_instances[si_index]) == next_value:
					if sorted_instances[si_index].label == "+":
						pos_right_weight -= sorted_instances[si_index].weight
						pos_left_weight += sorted_instances[si_index].weight
					else:
						neg_right_weight -= sorted_instances[si_index].weight
						neg_left_weight += sorted_instances[si_index].weight
					si_index += 1
				
				# check to make sure we haven't put everything in left
				if si_index < len(sorted_instances):
					new_entropy = weighted_entropy(pos_left_weight,neg_left_weight,pos_right_weight,neg_right_weight)
					if new_entropy < best_split_entropy:
						best_split_entropy = new_entropy
						best_split_feature = candidate_feature
						best_split_value = mean([next_value,candidate_feature.query(sorted_instances[si_index])])
						best_split_left_instances = sorted_instances[:si_index]
						best_split_right_instances = sorted_instances[si_index:]
		
		
		# leaf because no split? process and continue
		if best_split_feature == None:
			if verbosity >= 2:
				print "{0}: Leaf node, no split reduces entropy".format(current_node.path)
			current_node.process_leaf(pos_weight,neg_weight)
			continue
		
		# leaf because split creates small children? process and continue
		best_split_left_weight = sum([x.weight for x in best_split_left_instances])
		best_split_right_weight = sum([x.weight for x in best_split_right_instances])
		if best_split_left_weight < minimum_node_weight or best_split_right_weight < minimum_node_weight:
			if verbosity >= 2:
				print "{0}: Leaf node, best split creates overly light child nodes".format(current_node.path)
			current_node.process_leaf(pos_weight,neg_weight)
			continue
		
		# otherwise nonleaf
		if verbosity >= 2:
			print "{0}: Split {1}|{2}, feature {3} <= {4}".format(current_node.path,best_split_left_weight,best_split_right_weight,best_split_feature.feature_name,best_split_value)
		current_node.process_nonleaf(best_split_feature,best_split_value)
		
		worklist.append((current_node.left_child,best_split_left_instances))
		worklist.append((current_node.right_child,best_split_right_instances))

	return root_node

def mean(values):
	return float(sum(values))/len(values)

def weighted_entropy(pos_left_weight,neg_left_weight,pos_right_weight,neg_right_weight):
	left_proportion = (pos_left_weight + neg_left_weight) / (pos_left_weight + neg_left_weight + pos_right_weight + neg_right_weight)
	right_proportion = 1.0 - left_proportion
	return (left_proportion * entropy(pos_left_weight,neg_left_weight)) + (right_proportion * entropy(pos_right_weight,neg_right_weight))

def entropy(pos_weight,neg_weight):
	all_weight = pos_weight + neg_weight
	if all_weight <= 0.0: # in case of floating point error
		return 0.0
	return -xlnx(pos_weight/all_weight) - xlnx(neg_weight/all_weight)

def xlnx(x):
	if x <= 0.0: # in case of floating point error
		return 0.0
	else:
		return x * math.log(x,2.0)