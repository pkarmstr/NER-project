#!/usr/bin/python
#compute the accuracy of an NE tagger

#usage: evaluate-head.py [gold_file][output_file]

import sys, re

if len(sys.argv) != 3:
    sys.exit("usage: evaluate-head.py [gold_file][output_file]")

#gold standard file
goldfh = open(sys.argv[1], 'r')
#system output
testfh = open(sys.argv[2], 'r')

gold_tag_list = []
#gold_word_list = []
test_tag_list = []

emptyline_pattern = re.compile(r'^\s*$')

gold_tags_for_line = []
#gold_words_for_line = []
test_tags_for_line = []

for gline in goldfh.readlines():
    if emptyline_pattern.match(gline):
        if len(gold_tags_for_line) > 0:
            gold_tag_list.append(gold_tags_for_line)
        gold_tags_for_line = []
        #gold_word_list.append(gold_words_for_line)
        #gold_words_for_line = []
    else:
        parts = gline.split()
        #print parts
        gold_tags_for_line.append(parts[-1])
        #gold_words_for_line.append(parts[0])

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

#print gold_tag_list
#print test_tag_list

for i in range(len(gold_tag_list)):
    #print gold_tag_list[i]
    #print test_tag_list[i]
    for j in range(len(gold_tag_list[i])):
        if gold_tag_list[i][j] != 'O':
            gold_total += 1
        if test_tag_list[i][j] != 'O':
            test_total += 1
        if gold_tag_list[i][j] != 'O' and gold_tag_list[i][j] == test_tag_list[i][j]:
            correct += 1


precision = float(correct) / test_total
recall = float(correct) / gold_total
f = precision * recall * 2 / (precision + recall)

#print correct, gold_total, test_total
print 'p =', precision, 'r =', recall, 'f =', f
