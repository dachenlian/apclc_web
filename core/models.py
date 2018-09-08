from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class DcardPost(models.Model):
    _id = models.IntegerField()
    school = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    forum_name = models.CharField(max_length=255)
    forum_alias = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content_raw = models.TextField()
    content_clean = models.TextField()
    content_clean_seg = ArrayField(models.TextField())
    tags = ArrayField(models.CharField(max_length=225))
    created_at = models.CharField(max_length=255)
    user_gender = models.CharField(max_length=255)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    topics = ArrayField(models.TextField(),
                        blank=True,
                        null=True)
    has_images = models.BooleanField(default=False, null=True)
    has_videos = models.BooleanField(default=False, null=True)
    links = JSONField()

    def __str__(self):
        return f"{self._id}"


class WeiboPost(models.Model):
    _id = models.BigIntegerField()
    content_raw = models.TextField()
    cn_content_clean = models.TextField()
    cn_content_clean_seg = ArrayField(models.TextField())
    tw_content_clean = models.TextField()
    tw_content_clean_seg = ArrayField(models.TextField())
    cn_tags = ArrayField(models.CharField(max_length=255))
    tw_tags = ArrayField(models.CharField(max_length=255))
    is_long_text = models.BooleanField(default=False)
    created_at = models.CharField(max_length=255)
    user_gender = models.CharField(max_length=255)
    user_screen_name = models.CharField(max_length=255)
    user_followers_count = models.IntegerField()
    user_profile_url = models.CharField(max_length=255)
    user_profile_image_url = models.CharField(max_length=255)
    comments_count = models.IntegerField()

    def __str__(self):
        return f"{self._id}"


class WeiboFiveMilPost(models.Model):
    weibo_id = models.BigIntegerField()
    attitudes_count = models.IntegerField(blank=True, null=True)
    comments_count = models.IntegerField(blank=True, null=True)
    created_at = models.CharField(max_length=255)
    _id = models.BigIntegerField()
    content_raw = models.TextField()
    cn_content_clean = models.TextField()
    cn_content_clean_seg = ArrayField(models.TextField())
    tw_content_clean = models.TextField()
    tw_content_clean_seg = ArrayField(models.TextField())
    cn_tags = ArrayField(models.CharField(max_length=255))
    tw_tags = ArrayField(models.CharField(max_length=255))
    source = models.CharField(max_length=255, blank=True)
    reposts_count = models.CharField(max_length=255, blank=True)
