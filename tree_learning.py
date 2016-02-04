
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
			return self.prediction
		else:
			if self.split_feature.query(query_instance) <= self.split_value:
				return self.left_child.query(query_instance)
			else:
				return self.right_child.query(query_instance)
	
	def tree_summary(self):
		if self.leaf:
			return "{0} | Leaf: {1}\n".format(self.path,self.prediction)
		else:
			tree_text = "{0} | {1} <= {2}\n".format(self.path,self.split_feature.feature_name,self.split_value)
			tree_text += self.left_child.tree_summary()
			tree_text += self.right_child.tree_summary()
			return tree_text

# verbosity levels:
# 	1: print depth levels as they are reached
# 	2: print node paths when they are constructed
def build_classification_tree(features,instances,max_depth=-1,candidate_feature_proportion=.2,minimum_node_weight=0.0,verbosity=0):
	
	root_node = Tree_Node()
	worklist = [(root_node,instances,max_depth)]
	
	max_depth_reached = 0
	
	while worklist:
		
		(current_node, current_instances, max_depth) = worklist.pop(0)
		
		if verbosity >= 1 and current_node.depth() > max_depth_reached:
			max_depth_reached = current_node.depth()
			print "Building depth {0}...".format(current_node.depth())
		if verbosity >= 2:
			print "Building node {0}...".format(current_node.path)
		
		pos_weight = 0.0
		neg_weight = 0.0
		for instance in instances:
			if instance.label == "+":
				pos_weight += instance.weight
			else:
				neg_weight += instance.weight
		
		
		

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