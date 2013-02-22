from operator import mul
from math import log, exp
import re
import os
import glob

# ---- Feature class
# ------------------

class Feature:
    ham_count = 0
    spam_count = 0
    name = 'undefined'
    def __init__(self, fname):
        self.name = fname

    def __str__(self):
        return "Feature(ham_count = %s, spam_count = %s, name = %s)" % (self.ham_count, self.spam_count, self.name)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __add__(self, other):
        f = Feature(self.name)
        f.spam_count += (other.spam_count + self.spam_count)
        f.ham_count  += (other.ham_count + self.ham_count)
        return f

# ---- Extracting features
# ------------------------

def extract_words( text ):
    reobj = re.finditer( "[a-zA-Z]{2,}", text )
    all_words = map(lambda m : m.group(0), reobj )
    return list(set(all_words))

def extract_features( text ):
    "returns set"
    return set(map( Feature, extract_words( text ) ))

def inc_spam( feat_set ):
    def f(feat):
        feat.spam_count += 1
        return feat
    return set( map( f, feat_set ))

def inc_ham( feat_set ):
    def f(feat):
        feat.ham_count += 1
        return feat
    return set( map( f, feat_set ))

def add_overlapped(f1, f2):
    "maps first set of features and if feature from the first set is in the second one add value to the first, returns the first set"
    def f(feat):
        feat1 = filter(lambda f: f.name == feat.name, f2)
        if (feat1 == []):
            return feat
        else:
            return feat1[0] + feat
    return set(map(f, f1))

def merge_features(f1, f2):
    return set(list(add_overlapped(f2,f1)) + [feat for feat in f1 if not(feat in f2)])

# ---- Training
# -------------
total_spams = 0
total_hams = 0

def train(train_dir = "../data/training"):
    all_features = {}
    for spam_f in glob.glob(train_dir+"/spam/*.txt"):
        with open(spam_f, 'r') as content_file:
            content = content_file.read()
            spam_feats = inc_spam( extract_features( content ) )
            all_features = merge_features( all_features, spam_feats )
            global total_spams
            total_spams += 1

    for ham_f in glob.glob(train_dir+"/ham/*.txt"):
        with open(ham_f, 'r') as content_file:
            content = content_file.read()
            ham_feats = inc_ham( extract_features( content ) )
            all_features = merge_features( all_features, ham_feats )
            global total_hams
            total_hams += 1

    return all_features

# ---- Testing
# ------------

def test(test_dir = "../data/testing"):
    all_features = train()
    for spam_f in glob.glob(test_dir+"/spam/*.txt"):
        with open(spam_f, 'r') as content_file:
            content = content_file.read()
            print "spam message '%s' was classified as '%s'" % (spam_f, classify( content, all_features ))

    for ham_f in glob.glob(test_dir+"/ham/*.txt"):
        with open(ham_f, 'r') as content_file:
            content = content_file.read()
            print "ham message '%s' was classified as '%s'" % (ham_f, classify( content, all_features ))

# ---- Classification
# -------------------

def classification( score ):
    if score > 0.5:      return "spam"
    elif score < 0.5:    return "ham"
    else:                return "undefined"

def classify (text, all_features):
    feats = add_overlapped( extract_features( text ), all_features )
    return classification( score( feats ))

def spam_probability (feature):
    sc = feature.spam_count
    hc = feature.ham_count
    spam_frequency = (sc / max( 1, total_spams ))
    ham_frequency =  (hc / max( 1, total_hams ))
    return spam_frequency / (ham_frequency + spam_frequency)

def bayesian_spam_probability (feature, assumed_probability = 0.5, weight = 1):
    basic_probability = spam_probability( feature )
    data_points = feature.spam_count + feature.ham_count
    return (((weight * assumed_probability) + (data_points * basic_probability))
            / (weight + data_points))

def score (features):
    spam_probs = []
    ham_probs = []
    number_of_probs = 0
    for feature in features:
        if not untrained_p( feature ):
            spam_prob = float (bayesian_spam_probability( feature ))#, 0.0d0)
            spam_probs.append(spam_prob)
            ham_probs.append(1.0 - spam_prob)
            number_of_probs = number_of_probs + 1
    h = 1 - fisher( spam_probs, number_of_probs )
    s = 1 - fisher( ham_probs, number_of_probs )
    return ((1 - h) + s) / 2.0

def fisher (probs, number_of_probs):
  "The Fisher computation described by Robinson."
  return inverse_chi_square(
          -2 * reduce(mul, map(log, probs), 1),
           2 * number_of_probs)

def inverse_chi_square (value, degrees_of_freedom):
    assert ( degrees_of_freedom % 2 == 0 )
    m = value / 2
    acc = 0
    prob = exp(-m)
    for i in range(1, degrees_of_freedom / 2):
        prob *= (m/i)
        acc  += prob
    return min(1, acc)

def untrained_p( feature ):
    return feature.spam_count == 0 and feature.ham_count == 0
