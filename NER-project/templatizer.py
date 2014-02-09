import csv
from collections import namedtuple

HEADER =  ["name", "column", "turned_on", "previous", "forward", "composite_others", "composite_self"]
CSVRow = namedtuple("CSVRow", HEADER)

def create_blank_csv(ordered_features, file_path):
    with open(file_path, "w") as f_out:
        writer = csv.writer(f_out, dialect='excel')
        writer.writerow(HEADER)
        writer.writerow(["token", 0])
        writer.writerow(["tag", 1])
        writer.writerow(["sent_pos", 2])
        for i,feature_func in enumerate(ordered_features):
            feat_name = str(feature_func).split()[1]
            writer.writerow([feat_name, i+3])

def read_in_csv(file_path):
    data = []
    with open(file_path, "rb") as f_in:
        reader = csv.reader(f_in, dialect='excel')
        for name,column,turned_on,previous,forward,composite_others,composite_self in reader:
            if name != "name":
                column = int(column)
                turned_on = bool(int(turned_on))
                previous = -(int(previous))
                forward = int(forward)
                composite_others = map(int, composite_others.split())
                composite_self = map(int, composite_self.split())
                data.append(CSVRow(name,column,turned_on, previous,
                                   forward,composite_others, composite_self))
                
    return data

def create_template(data, file_path, bigram=True):
    unigram_feature = 1
    template_features = []
    tappend = template_features.append

    for feature in data:
        if feature.turned_on:
            curr_feat = "%x[{:d},{:d}]".format(0, feature.column)
            tappend("U{:02d}:{:s}".format(unigram_feature, curr_feat))
            unigram_feature += 1
            for i in xrange(feature.previous, 0):
                template_row = "U{:02d}:%x[{:d},{:d}]".format(unigram_feature, 
                                                              i, feature.column)
                tappend(template_row)
                unigram_feature += 1
            
            for i in xrange(1, feature.forward+1):
                template_row = "U{:02d}:%x[{:d},{:d}]".format(unigram_feature, 
                                                              i, feature.column)
                tappend(template_row)
                unigram_feature += 1
            
            for col_id in feature.composite_others:
                if col_id == -1:
                    break
                
                template_row = "U{:02d}:{:s}/%x[{:d},{:d}]".format(unigram_feature, 
                                                        curr_feat, 0, col_id)
                tappend(template_row)
                unigram_feature += 1
                
            for row_id in feature.composite_self:
                if row_id == 0:
                    break
                
                template_row = "U{:02d}:{:s}".format(unigram_feature, curr_feat)
                if row_id < 0:
                    for i in xrange(row_id, 0):
                        template_row += "/%x[{:d},{:d}]".format(i, feature.column)
                else:
                    for i in xrange(1, row_id+1):
                        template_row += "/%x[{:d},{:d}]".format(i, feature.column)
                        
                tappend(template_row)
                unigram_feature += 1
               
    if bigram:
        tappend("")
        tappend("B")
        
    with open(file_path, "wb") as f_out:
        f_out.write("\n".join(template_features))
            
if __name__ == "__main__":
    """
    data = read_in_csv("resources/for_template.csv")
    create_template(data, "train_test/template1")
    print "created template!"
    """
    