# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
r1_done_1, 1
r3_done_1, 1
r6_done_1, 1 
r8_done_1, 1 
all_done_1, 1
r1_done_2, 1
r3_done_2, 1
r6_done_2, 1 
r8_done_2, 1 
all_done_2, 1
r1_done_3, 1
r3_done_3, 1
r6_done_3, 1 
r8_done_3, 1 
all_done_3, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: False
synthesizer: jtlv
fastslow: True
decompose: True

CurrentConfigName:
three_robots_patrol

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
eight_regions.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p5
r5 = p4
r6 = p3
r7 = p2
r1 = p8
r2 = p7
r3 = p6
r8 = p1
others = 

Spec: # Specification in structured English
visit r1

