import pickle
from functools import partial
import logging
from collections import Counter
import string
import json

import zhon.hanzi
from gensim import corpora, models, similarities
import nltk
import re
import jieba
from opencc import OpenCC

from web.settings.base import BASE_DIR
from sentiment.utils import calculate_sentiment
from core.models import DcardPost, WeiboPost, WeiboFiveMilPost

PUNCTUATION = list(string.punctuation) + list(zhon.hanzi.punctuation) + ["##"]
punc_regex = re.compile(r"")
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

s2t = OpenCC('s2t')
t2s = OpenCC('t2s')

with open(f"{BASE_DIR}/static/misc/baidu_stopwords.txt") as fp:
    stop_cn = set(fp.read().split("\n"))
with open(f"{BASE_DIR}/static/misc/baidu_stopwords_trad.txt") as fp:
    stop_tw = set(fp.read().split("\n"))


def get_stats(dcard: DcardPost.objects, weibo: WeiboPost.objects, filter_stopwords=True, filter_punctuation=True):
    weibo_male = weibo.filter(user_gender__icontains='m').count()
    weibo_female = weibo.filter(user_gender__icontains='f').count()
    dcard_male = dcard.filter(user_gender__icontains='m').count()
    dcard_female = dcard.filter(user_gender__icontains='f').count()

    total_dcard_posts = dcard.count()
    total_weibo_posts = weibo.count()

    weibo_freq = Counter()
    for post in weibo:
        weibo_freq.update(post.cn_content_clean_seg)

    weibo_freq = weibo_freq.most_common()
    if filter_punctuation:
        weibo_freq = [tok for tok in weibo_freq if tok[0] not in PUNCTUATION]
    if filter_stopwords:
        weibo_freq = [tok for tok in weibo_freq if tok[0] not in stop_cn]

    dcard_freq = Counter()
    for post in dcard:
        dcard_freq.update(post.content_clean_seg)

    dcard_freq = dcard_freq.most_common()
    if filter_punctuation:
        dcard_freq = [tok for tok in dcard_freq if tok[0] not in PUNCTUATION]
    if filter_stopwords:
        dcard_freq = [tok for tok in dcard_freq if tok[0] not in stop_tw]

    weibo_average_post_length = sum([len(w.cn_content_clean_seg) for w in weibo]) / total_weibo_posts
    dcard_average_post_length = sum([len(d.content_clean_seg) for d in dcard]) / total_dcard_posts

    dcard_sentiment = calculate_sentiment([d.content_clean_seg for d in dcard])
    weibo_sentiment = calculate_sentiment([w.tw_content_clean_seg for w in weibo])

    stats = {
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
        'weibo_freq': weibo_freq[:100],
        'dcard_freq': dcard_freq[:100],
    }

    return stats


def get_similarities(tag, table, query, dcard, weibo):
    dcard_posts = [d.content_clean_seg for d in dcard]
    weibo_posts = [w.cn_content_clean_seg for w in weibo]
    if table == 'weibo':
        dictionary = corpora.Dictionary(dcard_posts)
    else:
        dictionary = corpora.Dictionary(weibo_posts)

    dictionary.save(f"{BASE_DIR}/static/gensim_files/{table}_{tag}.dict")
    corpus = [dictionary.doc2bow(text) for text in dcard_posts]
    corpora.MmCorpus.serialize(f"{BASE_DIR}/static/gensim_files/{table}_{tag}.mm", corpus)
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    # corpus_lsi = lsi[corpus_tfidf]
    lsi.save(f"{BASE_DIR}/static/gensim_files/{table}_{tag}.lsi")
    index = similarities.MatrixSimilarity(lsi[corpus])
    index.save(f"{BASE_DIR}/static/gensim_files/{table}_{tag}.index")

    if table == 'weibo':
        query = [s2t.convert(q) for q in query]
        posts = dcard_posts  # Dcard posts that are most similar to Weibo query
    else:
        query = [t2s.convert(q) for q in query]
        posts = weibo_posts  # Weibo posts that are most similar to Dcard query
    vec_bow = dictionary.doc2bow(query)
    vec_lsi = lsi[vec_bow]
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    similar_docs = []
    for sim in sims[:10]:
        similar_docs.append(["".join(posts[sim[0]]), str(round(sim[1]*100, 2)) + "%"])
    return similar_docs

# def get_similarities(tag, table, query, dcard, weibo):
#     dcard_posts = [d.content_clean_seg for d in dcard]
#     weibo_posts = [w.tw_content_clean_seg for w in weibo]
#     dictionary = corpora.Dictionary(dcard_posts)
#     dictionary.save(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.dict")
#     corpus = [dictionary.doc2bow(text) for text in dcard_posts]
#     corpora.MmCorpus.serialize(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.mm", corpus)
#     tfidf = models.TfidfModel(corpus)
#     corpus_tfidf = tfidf[corpus]
#     lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
#     # corpus_lsi = lsi[corpus_tfidf]
#     lsi.save(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.lsi")
#     index = similarities.MatrixSimilarity(lsi[corpus])
#     index.save(f"{BASE_DIR}/static/gensim_files/dcard_{tag}.index")
#
#     doc_index = random.randint(0, len(weibo_posts))
#     doc_tw = weibo_posts[doc_index]
#     doc_cn = weibo[doc_index]['cleanText_cn']
#     vec_bow = dictionary.doc2bow(doc_tw)
#     vec_lsi = lsi[vec_bow]
#     sims = index[vec_lsi]
#     sims = sorted(enumerate(sims), key=lambda item: -item[1])
#
#     similar_docs = []
#     for sim in sims[:100]:
#         similar_docs.append(["".join(dcard_posts[sim[0]]), sim[1]])
#
#     return similar_docs


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


def dcard_save_to_db(file):
    with open(file) as fp:
        dcard = json.load(fp)

    for d in dcard:
        DcardPost(
            _id=d.get('_id'),
            school=d.get('school'),
            department=d.get('department'),
            forum_name=d.get('forumName'),
            forum_alias=d.get('forumAlias'),
            title=d.get('title'),
            content_raw=d.get('content_raw'),
            content_clean=d.get('content_clean'),
            content_clean_seg=d.get('content_seg'),
            tags=d.get('tags'),
            created_at=d.get('createdAt'),
            user_gender=d.get('gender'),
            like_count=d.get('likeCount'),
            comment_count=d.get('commentCount'),
            topics=d.get('topics'),
            has_images=d.get('withImages'),
            has_videos=d.get('withVideos'),
            links=d.get('links')
        ).save()


def weibo_save_to_db(file):
    with open(file) as fp:
        weibo = json.load(fp)

    for w in weibo:
        WeiboPost(
            _id=w.get('_id'),
            content_raw=w.get('rawText'),
            cn_content_clean=w.get('cleanText_cn'),
            cn_content_clean_seg=w.get('cleanText_seg_cn'),
            tw_content_clean=w.get('cleanText_tw'),
            tw_content_clean_seg=w.get('cleanText_seg_tw'),
            cn_tags=w.get('tags_cn'),
            tw_tags=w.get('tags_tw'),
            is_long_text=w.get('isLongText'),
            created_at=w.get('createdAt'),
            user_gender=w.get('userGender'),
            user_screen_name=w.get('userScreenName'),
            user_followers_count=w.get('userFollowersCount'),
            user_profile_url=w.get('userProfileUrl'),
            user_profile_image_url=w.get('userProfileImageUrl'),
            comments_count=w.get('commentsCount')
        ).save()


def weibo_five_mil_save_to_db(file):
    print("Starting...")
    openCC = OpenCC('s2t')
    hashtag_regex = re.compile(r"#(\w+)#")
    clean_regex = re.compile(r"[(\s)|(\u200b)]+")
    html_regex = re.compile(r'(www|http)\S+', flags=re.MULTILINE)
    null_regex = re.compile(r'\x00')
    with open(file) as fp:
        for i in range(1820000):
            fp.readline()  # skip headers
        for idx, line in enumerate(fp, 1820000):
            if idx % 10000 == 0:
                print(f"{idx} posts...")
            post = line.split("\t")
            try:
                weibo_id = int(post[0])
                if WeiboFiveMilPost.objects.filter(weibo_id=weibo_id).exists():
                    continue
                else:
                    try:
                        attitudes_count = int(post[1])
                        comments_count = int(post[3])
                        created_at = post[4]
                        _id = int(post[7])
                        content_raw = post[18]
                        content_raw = null_regex.sub("", content_raw)
                        cn_content_clean = clean_regex.sub("", content_raw)
                        cn_content_clean = html_regex.sub("LINK", cn_content_clean)
                        cn_content_clean_seg = list(jieba.cut(cn_content_clean))
                        tw_content_clean = openCC.convert(cn_content_clean)
                        tw_content_clean_seg = [openCC.convert(c) for c in cn_content_clean_seg]
                        cn_tags = hashtag_regex.findall(cn_content_clean)
                        if cn_tags:
                            tw_tags = [openCC.convert(t) for t in cn_tags]
                        else:
                            tw_tags = []
                        reposts_count = int(post[16])
                        source = post[17]
                        WeiboFiveMilPost(
                            weibo_id=weibo_id,
                            attitudes_count=attitudes_count,
                            comments_count=comments_count,
                            created_at=created_at,
                            _id=_id,
                            content_raw=content_raw,
                            cn_content_clean=cn_content_clean,
                            cn_content_clean_seg=cn_content_clean_seg,
                            tw_content_clean=tw_content_clean,
                            tw_content_clean_seg=tw_content_clean_seg,
                            cn_tags=cn_tags,
                            tw_tags=tw_tags,
                            source=source,
                            reposts_count=reposts_count
                        ).save()
                    except ValueError as err:
                        print(err)
                        continue
            except ValueError as err:
                print(err)
