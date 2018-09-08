from django import forms


class InputForm(forms.Form):
    DCARD = 'Dcard'
    WEIBO = 'Weibo'
    FORUM_CHOICES = (
        (DCARD, 'Dcard'),
        (WEIBO, 'Weibo')
    )
    forum = forms.ChoiceField(choices=FORUM_CHOICES, initial=DCARD)
    tags = forms.CharField(initial="減肥", label="Tags", max_length=100)
    filter_stopwords = forms.BooleanField(initial=True, required=False)
    filter_punctuation = forms.BooleanField(initial=True, required=False)
