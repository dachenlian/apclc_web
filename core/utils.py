import pickle
from functools import partial
import logging
import random
from collections import Counter
import string

import zhon.hanzi
from gensim import corpora, models, similarities
import nltk
import re

from web.settings import BASE_DIR
from sentiment.utils import calculate_sentiment


PUNCTUATION = list(string.punctuation) + list(zhon.hanzi.punctuation) + ["##"]
punc_regex = re.compile(r"")
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

with open(f"{BASE_DIR}/static/misc/baidu_stopwords.txt") as fp:
    stop_cn = set(fp.read().split("\n"))
with open(f"{BASE_DIR}/static/misc/baidu_stopwords_trad.txt") as fp:
    stop_tw = set(fp.read().split("\n"))


def get_stats(tag, dcard, weibo, filter_stopwords=True, filter_punctuation=True):
    dcard_posts = []
    weibo_posts = []

    weibo_male = 0
    weibo_female = 0
    dcard_male = 0
    dcard_female = 0

    for post in dcard:
        if tag in post['tags']:
            dcard_posts.append(post)
    for post in weibo:
        if tag in post['tags_tw']:
            weibo_posts.append(post)

    for post in dcard_posts:
        if post["gender"].lower() == "m":
            dcard_male += 1
        else:
            dcard_female += 1

    for post in weibo_posts:
        if post["userGender"].lower() == "m":
            weibo_male += 1
        else:
            weibo_female += 1

    total_dcard_posts = len(dcard_posts)
    total_weibo_posts = len(weibo_posts)

    weibo_freq = Counter()
    for post in weibo_posts:
        weibo_freq.update(post['cleanText_seg_cn'])

    weibo_freq = weibo_freq.most_common()
    if filter_punctuation:
        weibo_freq = [tok for tok in weibo_freq if tok[0] not in PUNCTUATION]
    if filter_stopwords:
        weibo_freq = [tok for tok in weibo_freq if tok[0] not in stop_cn]

    dcard_freq = Counter()
    for post in dcard_posts:
        dcard_freq.update(post['content_seg'])

    dcard_freq = dcard_freq.most_common()
    if filter_punctuation:
        dcard_freq = [tok for tok in dcard_freq if tok[0] not in PUNCTUATION]
    if filter_stopwords:
        dcard_freq = [tok for tok in dcard_freq if tok[0] not in stop_tw]

    weibo_average_post_length = sum([len(w['cleanText_seg_cn']) for w in weibo_posts]) / len(weibo_posts)
    dcard_average_post_length = sum([len(d['content_seg']) for d in dcard_posts]) / len(dcard_posts)

    dcard_sentiment = calculate_sentiment([d['content_seg'] for d in dcard_posts])
    weibo_sentiment = calculate_sentiment([w['cleanText_seg_tw'] for w in weibo_posts])

    stats = {
        'dcard_posts': dcard_posts,
        'weibo_posts': weibo_posts,
        'dcard_sentiment': dcard_sentiment,
        'weibo_sentiment': weibo_sentiment,
        'weibo_average_post_length': weibo_average_post_length,
        'dcard_average_post_length': dcard_average_post_length,
        'total_dcard_posts': total_dcard_posts,
        'total_weibo_posts': total_weibo_posts,
        'weibo_male': weibo_male,
        'weibo_female': weibo_female,
        'dcard_male': dcard_male,
        'dcard_female': dcard_female,
        'weibo_freq': weibo_freq,
        'dcard_freq': dcard_freq,
    }

    return stats


def get_similarities(tag, dcard, weibo):
    dcard_posts = [d['content_seg'] for d in dcard]
    weibo_posts = [w['cleanText_seg_tw'] for w in weibo]
    dictionary = corpora.Dictionary(dcard_posts)
    dictionary.save(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.dict")
    corpus = [dictionary.doc2bow(text) for text in dcard_posts]
    corpora.MmCorpus.serialize(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.mm", corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    # corpus_lsi = lsi[corpus_tfidf]
    lsi.save(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.lsi")
    index = similarities.MatrixSimilarity(lsi[corpus])
    index.save(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.index")

    doc_index = random.randint(0, len(weibo_posts))
    doc_tw = weibo_posts[doc_index]
    doc_cn = weibo[doc_index]['cleanText_cn']
    vec_bow = dictionary.doc2bow(doc_tw)
    vec_lsi = lsi[vec_bow]
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    similar_docs = []
    for sim in sims[:100]:
        similar_docs.append(["".join(dcard_posts[sim[0]]), sim[1]])

    return doc_cn, similar_docs


def word_filter(token, *w):
    return token not in w


def get_collocates(token, table):
    bigram_measures = nltk.collocations.BigramAssocMeasures()

    if table == "dcard":
        with open(f"{BASE_DIR}/static/misc/dcard_bigram_collocation_finder.pkl", "rb") as fp:
            finder = pickle.load(fp)
    else:
        with open(f"{BASE_DIR}/static/misc/weibo_bigram_collocation_finder.pkl", "rb") as fp:
            finder = pickle.load(fp)

    w_filter = partial(word_filter, token)

    finder.apply_freq_filter(3)
    finder.apply_ngram_filter(w_filter)
    results = finder.nbest(bigram_measures.pmi, 100000000000000000)

    return results


