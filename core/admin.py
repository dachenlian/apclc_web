from django.contrib import admin
from .models import WeiboPost, DcardPost, WeiboFiveMilPost

# Register your models here.

admin.site.register(WeiboPost)
admin.site.register(DcardPost)
admin.site.register(WeiboFiveMilPost)
