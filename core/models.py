from django.db import models
from django.contrib.postgres.fields import ArrayField


class DcardPost(models.Model):
    _id = models.IntegerField()
    school = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    forum_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    content_raw = models.TextField()
    content_clean = models.TextField()
    content_clean_seg = ArrayField(models.CharField(max_length=255))
    tags = ArrayField(models.CharField(max_length=225))
    create_at = models.CharField(max_length=255)
    user_gender = models.CharField(max_length=255)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    topics = ArrayField(models.CharField(max_length=255),
                        blank=True,
                        null=True)
    has_images = models.BooleanField(default=False)
    has_videos = models.BooleanField(default=False)


class WeiboPost(models.Model):
    _id = models.IntegerField()
    content_raw = models.TextField()
    cn_content_clean = models.TextField()
    cn_content_clean_seg = ArrayField(models.CharField(max_length=255))
    tw_content_clean = models.TextField()
    tw_content_clean_seg = ArrayField(models.CharField(max_length=255))
    cn_tags = ArrayField(models.CharField(max_length=255))
    tw_tags = ArrayField(models.CharField(max_length=255))
    is_long_text = models.BooleanField(default=False)
    created_at = models.CharField(max_length=255)
    user_gender = models.CharField(max_length=255)
    user_screen_name = models.CharField(max_length=255)
    user_followers_count = models.IntegerField()
    user_profile_url = models.CharField(max_length=255)
    user_profile_image_url = models.CharField(max_length=255)

