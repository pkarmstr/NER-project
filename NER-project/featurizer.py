import re

__author__ = "Julia B.G. and Keelan A."

FUNCTION_WORDS = set(open("resources/function_words.txt","r").readlines())
NOUN_SUFFIXES = set(open("resources/noun_suffixes.txt","r").readlines())
ADJ_SUFFIXES = set(open("resources/adj_suffixes.txt","r").readlines())
VERB_SUFFIXES = set(open("resources/verbal_suffixes.txt","r").readlines())


def read_input(file_path):
    """
    return list of tuples (index,token, pos,bio)
    """
    data = []
    with open(file_path, "rb") as f_in:
        sentence = []
        for line in f_in:
            features = line.split("\t")
            if len(features) == 4:
                sentence.append(features)
            else:
                data.append(sentence)
                sentence = []
    return data


def get_features(tuple_list,output_path):

    f=open(output_path,"w")
    for (i,(j,token, pos,bio)) in enumerate(tuple_list):
        #start with index, token, and pos-tag.
        feat=["token="+token,"POS="+pos,j]

        #features of token. Comment out features you don't want included.

        feat.append("init_caps="+str(init_caps(token)))
        feat.append("allCaps="+str(allCaps(token)))
        feat.append("mixedCaps="+str(mixedCaps(token)))
        feat.append("containsDigit="+str(containsDigit(token)))
        feat.append("containsNonAlphaNum="+str(containsNonAlphaNum(token)))
        feat.append("is_within_quotes="+str(is_within_quotes(token)))
        feat.append("isFunctionWord="+str(isFunctWord(token)))
        feat.append("noun_suffix="+str(has_noun_suffix(token)))
        feat.append("verbal_suffix="+str(has_verbal_suffix(token)))
        feat.append("adj_suffix="+str(has_adj_suffix(token)))

        #features involving other tokens (previous, next)

        if i!=len(tuple_list)-1: #features that look ahead
            feat.append("nextInitCaps="+str(init_caps(tuple_list[i+1][1])))

            if i>0: #if it isn't the first word of the whole file, look previous
                feat.append("prev_curr_nextInitCaps="+str(prev_curr_nextInitCaps(i,j,tuple_list)))
                feat.append("otherOccurSamePrevious="+str(otherOccurSamePrevious(i,tuple_list)))
            else: #first word of the whole file, features involving previous are false.
                feat.append("prev_curr_nextInitCaps=False")
                feat.append("otherOccurSamePrevious=False")

        else: #last word of file, features involving next word are false.
            feat.append("nextInitCaps=False")
            feat.append("prev_curr_nextInitCaps=False")
            feat.append("otherOccurSamePrevious=False")


        #label
        feat.append(bio)

        #write
        f.write(("\t".join(feat))+"\n")

    f.close()

####################
# unigram features #
####################

def init_caps(token):
    return "init_caps={}".format(token.istitle())

def all_caps(t):
    return "all_caps={}".format(t.isupper())

def mixed_caps(t):
    return "mixed_caps={}".format(not t.islower() and\
                                  not t.isupper() and\
                                  t.isalpha())

def contains_digit(t):
    return "contains_digit={}".format(bool(re.match("\d",t)))

def contains_non_alpha_num(t):
    return "contains_non_alpha_num={}".format(bool(re.match("\W",t)))

def is_funct_word(t):
    return "is_funct_word={}".format(t.lower() in FUNCTION_WORDS)

def has_noun_suffix(t):
    return "has_noun_suffix={}".fomat(t[-3:].lower() in NOUN_SUFFIXES)

def has_verbal_suffix(t):
    return "has_verbal_suffix={}".format(t[-3:].lower() in VERB_SUFFIXES)

def has_adj_suffix(t):
    return "has_adj_suffix={}".format(t[-3:].lower() in ADJ_SUFFIXES)

##################
# local features #
##################

def is_within_quotes(t):
    return (len(re.findall("\"",t))>0)

###################
# global features #
###################

def otherOccurSamePrevious(curr_index,tuple_list): #need global context
    prev=tuple_list[curr_index-1][1]
    curr_w = tuple_list[curr_index][1]

    found=False
    j_prev=""
    for (j,(i,token,pos,bio)) in enumerate(tuple_list[curr_index+1:]): #search in the rest of the doc
        if token.startswith("NYT") or token.startswith("APW"): #new document, we only focus in the scope of that article
            break
        if token==curr_w and j_prev == prev:
            found=True
            break
        j_prev = token
    return found




if __name__=="__main__":
    tuple_list=read_input('train.gold')
    get_features(tuple_list,"resources/new_train_gold.txt")



