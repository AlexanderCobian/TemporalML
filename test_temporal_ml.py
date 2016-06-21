
from temporal_ml import *

'''
0123456789
A   A A A
 B  BB  B
  C  CC C
'''

example = Example("test_example")
for tick in [0,4,6,8]:
	example.add_event("A",tick)
for tick in [1,4,5,8]:
	example.add_event("B",tick)
for tick in [2,5,6,8]:
	example.add_event("C",tick)

last_a = Feature_LastOccurrence("Last A","A")
last_b = Feature_LastOccurrence("Last B","B")
last_c = Feature_LastOccurrence("Last C","C")
last_ab = Feature_LastOccurrence("Last A/B","A","B")
last_ac = Feature_LastOccurrence("Last A/C","A","C")
last_bc = Feature_LastOccurrence("Last B/C","B","C")

next_a = Feature_NextOccurrence("Next A","A")

second_last_a = Feature_2ndLastOccurrence("2nd Last A","A")

salience_b = Feature_Intensity("Intensity B",.01,"B",1.0)

freq_a = Feature_Frequency("Freq A",0,"A")

recent_freq_a = Feature_Recent_Frequency("Recent Freq A",3,"A")

window_a = Feature_TemporalWindow("Window A (2)",2,"A")

impending_a = Feature_ClassLabel_ImpendingEvent("Impending A",2,"A")
impending_weighted_a = Feature_ClassLabel_ImpendingEvent_LinearWeight("Impending Weighted A",1,"A")

recent_a = Feature_ClassLabel_RecentEvent("Recent A",2,"A")
recent_weighted_a = Feature_ClassLabel_RecentEvent_LinearWeight("Recent Weighted A",1,"A")

moment = Feature_Moment("Moment")

tick_0 = example.create_example_moment(0)
tick_1 = example.create_example_moment(1)
tick_2 = example.create_example_moment(2)
tick_3 = example.create_example_moment(3)
tick_4 = example.create_example_moment(4)
tick_5 = example.create_example_moment(5)
tick_6 = example.create_example_moment(6)
tick_7 = example.create_example_moment(7)
tick_8 = example.create_example_moment(8)
tick_9 = example.create_example_moment(9)
