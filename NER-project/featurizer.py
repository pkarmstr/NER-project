import re
import sys
from collections import namedtuple, defaultdict

__author__ = "Julia B.G. and Keelan A."

FUNCTION_WORDS = set(open("resources/function_words.txt","r").readlines())
NOUN_SUFFIXES = set(open("resources/noun_suffixes.txt","r").readlines())
ADJ_SUFFIXES = set(open("resources/adj_suffixes.txt","r").readlines())
VERB_SUFFIXES = set(open("resources/verbal_suffixes.txt","r").readlines())
CORP_SUFFIXES = set(open("resources/corporate_suffix_list.txt","r").readlines())
LOCATIONS = set(open("resources/loc_list.txt","r").readlines())
NAMES = set(open("resources/name_list.txt","r").readlines())
ORGANIZATIONS = set(open("resources/org_list.txt","r").readlines())
PERSON_PREFIXES = set(open("resources/person_prefix_list.txt","r").readlines())
ALL_BIGRAMS = defaultdict(set) #treating these two like they're 'final', but in
FREQ_DIST = defaultdict(int)   #reality, we're building them up in the set up


FeatureSet = namedtuple("FeatureSet", ["global_index", "sentence_index", "token", 
                                       "POS_tag", "BIO_tag"])

FeatureSetTest = namedtuple("FeatureSetTest", ["global_index", "sentence_index", 
                                               "token", "POS_tag"])

def open_bigrams_file():
    try:
        with open("resources/all_bigrams.txt", "r") as f_in:
            for line in f_in:
                word,prev_tokens_str = line[:-1].split("\t")
                prev_tokens = set(prev_tokens_str.split())
                ALL_BIGRAMS[word] = prev_tokens
    except IOError:
        pass
    
def write_bigrams():
    with open("resources/all_bigrams.txt", "w") as f_out:
        for word, prev_token_set in ALL_BIGRAMS.iteritems():
            out_str = "{}\t{}\n".format(word, " ".join(prev_token_set))
            f_out.write(out_str)

def read_and_prepare_input(file_path, test=False):
    open_bigrams_file()
    data = []
    if test:
        correct_len = 3
        FS = FeatureSetTest
    else:
        correct_len = 4
        FS = FeatureSet
    with open(file_path, "rb") as f_in:
        global_index = 0
        sentence_index = 0 #sentence index isn't always correct, we'll keep track
        sentence = []
        prev_token = "__START__"
        for line in f_in:
            features = line[:-1].split("\t")
            if len(features) == correct_len:
                token = features[1]
                all_features = [global_index, sentence_index]+features[1:]
                sentence.append(FS(*all_features))
                ALL_BIGRAMS[prev_token].add(token)
                FREQ_DIST[token] += 1
                prev_token = token
                sentence_index += 1
            else:
                data.append(sentence)
                sentence = []
                prev_token = "__START__"
                global_index += 1
                sentence_index = 0
    write_bigrams()
    return data


def build_feature_set(original_features, unigram_features=[], 
                      local_features=[], global_features=[]):
    new_feature_sequence = []
    nfseqappend = new_feature_sequence.append
    for sentence in original_features:
        for feature_set in sentence:
            new_features = [feature_set.token, 
                            feature_set.POS_tag, 
                            str(feature_set.sentence_index)]
            nfappend = new_features.append
            for uni_feat in unigram_features:
                nfappend(uni_feat(feature_set))
            
            for local_feat in local_features:
                nfappend(local_feat(feature_set, sentence))
                
            for global_feat in global_features:
                nfappend(global_feat(feature_set, original_features))
                
            try:
                nfappend(feature_set.BIO_tag)
            except AttributeError:
                continue
            
            nfseqappend("\t".join(new_features))
            
        nfseqappend("")
        
    return "\n".join(new_feature_sequence)


####################
# unigram features #
####################

def init_caps(fs):
    return "init_caps={}".format(fs.token.istitle())

def all_caps(fs):
    return "all_caps={}".format(fs.token.isupper())

def mixed_caps(fs):
    return "mixed_caps={}".format(not fs.token.islower() and\
                                  not fs.token.isupper() and\
                                  fs.token.isalpha())

def contains_digit(fs):
    return "contains_digit={}".format(bool(re.match("\d",fs.token)))

def contains_non_alpha_num(fs):
    return "contains_non_alpha_num={}".format(bool(re.match("\W",fs.token)))

def is_funct_word(fs):
    return "is_funct_word={}".format(fs.token.lower() in FUNCTION_WORDS)

def has_noun_suffix(fs):
    return "has_noun_suffix={}".format(fs.token[-3:].lower() in NOUN_SUFFIXES)

def has_verbal_suffix(fs):
    return "has_verbal_suffix={}".format(fs.token[-3:].lower() in VERB_SUFFIXES)

def has_adj_suffix(fs):
    return "has_adj_suffix={}".format(fs.token[-3:].lower() in ADJ_SUFFIXES)

def is_weekday(fs):
    re_day ="(Thurs|Tues|Wednes|Mon|Fri|Satur|Sun)day" 
    return "is_weekday={}".format(bool(re.match(re_day,fs.token)))

def is_hyphenated_both_init_caps(fs):
    if len(re.findall("-",fs.token))>0:
        return "is_hyphenated_both_init_caps={}".format(all([w.istitle() for w in fs.token.split("-")]))
    else:
        return "is_hyphenated_both_init_caps=False"

def is_common_word(fs):
    return "is_common_word={}".format(FREQ_DIST[fs.token]>=5)

def is_person_prefix(fs):
    return "is_person_prefix={}".format(fs.token.lower() in PERSON_PREFIXES)

def is_corp_suffix(fs):
    return "is_corp_suffix={}".format(fs.token in CORP_SUFFIXES)

def is_location(fs):
    return "is_location={}".format(fs.token in LOCATIONS)

def is_name(fs):
    return "is_name={}".format(fs.token in NAMES)

def is_org(fs):
    return "is_org={}".format(fs.token in ORGANIZATIONS)

##################
# local features #
##################

def is_within_quotes(fs, sentence):
    within_quote = False
    feature_string = "is_within_quotes"
    for _,local_index,token,_,_ in sentence:
        if token == "``":
            within_quote = True
        elif token.endswith("\'\'"):
            within_quote = False
        elif within_quote and local_index == fs.sentence_index:
            return "{}=True".format(feature_string)


    return "{}=False".format(feature_string)

def acronym_begin(fs, sentence):
    if fs.token.istitle():
        acronym=fs.token[0]
        i=fs.sentence_index+1
        while i<len(sentence)-1 and sentence[i][2].istitle():
            acronym+=sentence[i][2][0]
            i+=1
        return "acronym_begin={}".format(ALL_BIGRAMS.has_key(acronym) and len(acronym)>1)
    return "acronym_begin=False"


def acronym_inside(fs, sentence):
    i = fs.sentence_index
    acronym=""
    while i>=0: ##check initials to the left
        if sentence[i][2].istitle():
            acronym=sentence[i][2][0]+acronym
            i-=1
        else:
            break
    if len(acronym)>1: #check initials to the right
        i = fs.sentence_index+1
        while i<len(sentence):
            if sentence[i].token.istitle():
                acronym=acronym+sentence[i].token[0]
                i+=1
            else:
                break
    return "acronym_inside={}".format(ALL_BIGRAMS.has_key(acronym) and len(acronym)>1)

def inside_NNP_sequence(fs, sentence):
    i=fs.sentence_index
    if i>0:
        previous_NNP = sentence[i-1].POS_tag=="NNP"
        return "inside_NNP_sequence={}".format(fs.POS_tag == "NNP" and previous_NNP)
    else:
        return "inside_NNP_sequence=False"

def first_in_NNP_sequence(fs, sentence):
    i = fs.sentence_index
    if i<len(sentence)-1: 
        begin = inside_NNP_sequence(fs,sentence).endswith("False") and\
        inside_NNP_sequence(sentence[i+1],sentence).endswith("True")
        return "first_in_NNP_sequence={}".format(begin)
    else:
        return "first_in_NNP_sequence=False"

###################
# global features #
###################

def sometimes_occur_same_previous(fs, original_sequence):
    try:
        prev_token = original_sequence[fs.global_index][fs.sentence_index-1]
    except IndexError:
        prev_token = "__START__"
    return "sometimes_occur_same_previous={}".format(prev_token in ALL_BIGRAMS[fs.token])

def always_occur_same_previous(fs, original_sequence):
    return "always_occur_same_previous={}".format(len(ALL_BIGRAMS[fs.token]) == 1)

def always_init_caps(fs, original_sequence):
    return "always_init_caps={}".format(fs.token.istitle() and\
                                        not ALL_BIGRAMS.has_key(fs.token.lower()))
    
def main():
    if len(sys.argv) != 3:
        print "Usage: featurizer.py [original_file] [output]"
        sys.exit(1)
    print "beginning everything"
    original_feature_set = read_and_prepare_input(sys.argv[1])
    print "read in file, prepared some stuff"
    """
    #the original features
    unigram_features = [init_caps, all_caps, mixed_caps, contains_digit, 
                        contains_non_alpha_num, is_funct_word, has_noun_suffix,
                        has_verbal_suffix, has_adj_suffix]
    local_features = [is_within_quotes]
    global_features = [sometimes_occur_same_previous, always_occur_same_previous, 
                       always_init_caps]
    """
    unigram_features = [init_caps, all_caps, mixed_caps, contains_digit, 
                        contains_non_alpha_num, is_funct_word, has_noun_suffix,
                        has_verbal_suffix, has_adj_suffix, is_weekday, 
                        is_hyphenated_both_init_caps, is_common_word,
                        is_person_prefix, is_corp_suffix, is_location,
                        is_name, is_org]
    local_features = [is_within_quotes, acronym_begin, acronym_inside, 
                      inside_NNP_sequence, first_in_NNP_sequence]
    global_features = [sometimes_occur_same_previous, always_occur_same_previous, 
                       always_init_caps]
    print "building your new feature sets!"
    new_feats = build_feature_set(original_feature_set, unigram_features, 
                                  local_features, global_features)
    print "writing to file"
    with open(sys.argv[2], "w") as f_out:
        f_out.write(new_feats)
    print "done!!"

if __name__=="__main__":
    main()