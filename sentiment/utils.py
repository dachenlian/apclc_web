from pathlib import Path
import json
from collections import Counter

CURRENT_DIR = Path(__file__)

with open(f"{CURRENT_DIR.parent}/static/emo_pos.json") as fp:
    pos_list = set(json.load(fp))

with open(f"{CURRENT_DIR.parent}/static/emo_neg.json") as fp:
    neg_list = set(json.load(fp))


def calculate_sentiment(seg_posts):
    pos_count = 0
    neg_count = 0
    c = Counter()

    for post in seg_posts:
        c.update(post)

    for tok, count in c.items():
        if tok in pos_list:
            pos_count += count
        elif tok in neg_list:
            neg_count += count

    final_score = (pos_count - neg_count) / len(seg_posts)

    return final_score
