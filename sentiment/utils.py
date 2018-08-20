from pathlib import Path
import json

CURRENT_DIR = Path(__file__)

with open(f"{CURRENT_DIR.parent}/static/emo_pos.json") as fp:
    pos_list = set(json.load(fp))

with open(f"{CURRENT_DIR.parent}/static/emo_neg.json") as fp:
    neg_list = set(json.load(fp))


def calculate_sentiment(seg_posts):
    scores = []

    for post in seg_posts:
        pos_count = 0
        neg_count = 0
        for tok in post:
            if tok in pos_list:
                pos_count += 1
            elif tok in neg_list:
                neg_count += 1
        post_score = (pos_count - neg_count) / len(post)
        scores.append(post_score)

    final_score = sum(scores) / len(seg_posts)

    return final_score
