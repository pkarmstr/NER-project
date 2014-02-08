#!/usr/bin/python
"""
Compute the accuracy of an NE tagger:
    - Overall precision, recall, and F-Measure
    - Precision, recall, and F-Measure for each label
"""

#usage: evaluate-per-label.py [gold_file][output_file]

import sys, re

if len(sys.argv) != 3:
    sys.exit("usage: evaluate-per-label.py [gold_file][output_file]")

#gold standard file
goldfh = open(sys.argv[1], 'r')
#system output
testfh = open(sys.argv[2], 'r')

gold_tag_list = []
test_tag_list = []

emptyline_pattern = re.compile(r'^\s*$')

gold_tags_for_line = []
test_tags_for_line = []

for gline in goldfh.readlines():
    if emptyline_pattern.match(gline):
        if len(gold_tags_for_line) > 0:
            gold_tag_list.append(gold_tags_for_line)
        gold_tags_for_line = []
    else:
        parts = gline.split()
        #print parts
        gold_tags_for_line.append(parts[-1])

for tline in testfh.readlines():
    if  emptyline_pattern.match(tline):
        if len(test_tags_for_line) > 0:
            test_tag_list.append(test_tags_for_line)
        test_tags_for_line = []
    else:
        parts = tline.split()
        #print parts
        test_tags_for_line.append(parts[-1])

#dealing with the last line
if len(gold_tags_for_line) > 0:
    gold_tag_list.append(gold_tags_for_line)

if len(test_tags_for_line) > 0:
    test_tag_list.append(test_tags_for_line)


test_total = 0
gold_total = 0
correct = 0


label_dict = {
    'B-PER':{'test_total':0,'gold_total':0, 'correct':0},
    'I-PER':{'test_total':0,'gold_total':0, 'correct':0},
    'B-ORG':{'test_total':0,'gold_total':0, 'correct':0},
    'I-ORG':{'test_total':0,'gold_total':0, 'correct':0},
    'B-GPE':{'test_total':0,'gold_total':0, 'correct':0},
    'I-GPE':{'test_total':0,'gold_total':0, 'correct':0}
    }


#print gold_tag_list
#print test_tag_list

for i in range(len(gold_tag_list)):
    #print gold_tag_list[i]
    #print test_tag_list[i]
    for j in range(len(gold_tag_list[i])):
        gold_tag = gold_tag_list[i][j]
        test_tag = test_tag_list[i][j]
        if gold_tag != 'O':            
            gold_total += 1
            label_dict[gold_tag]['gold_total'] += 1
        if test_tag != 'O':
            test_total += 1
            label_dict[test_tag]['test_total'] += 1
        if gold_tag != 'O' and gold_tag == test_tag:
            correct += 1
            label_dict[gold_tag]['correct'] += 1


precision_all = float(correct) / test_total
recall_all = float(correct) / gold_total
f_all = precision_all * recall_all * 2 / (precision_all + recall_all)

print
print "          " + "\t" + "Precision\t" + "Recall\t" + "F-Measure"
print "OVERALL" + "\t\t" + str(round(precision_all,2)) + "\t\t"+ \
      str(round(recall_all,2)) + "\t"+ str(round(f_all,2))

for label in sorted(label_dict.keys()):

    if label_dict[label]['test_total'] != 0:
        p = \
           float(label_dict[label]['correct']) / label_dict[label]['test_total']
    else:
        p = 0.0

    if label_dict[label]['gold_total'] != 0:
        r = \
           float(label_dict[label]['correct']) / label_dict[label]['gold_total']
    else:
        r = 0.0

    if (p + r) != 0:
        f = p * r * 2 / (p + r)
    else:
        f = 0.0       

    print label + "\t\t" + str(round(p,2)) + "\t\t"+ \
      str(round(r,2)) + "\t"+ str(round(f,2))


            
    
