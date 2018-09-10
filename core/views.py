from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.http import JsonResponse

from .forms import InputForm
from .utils import get_stats, get_similarities, get_collocates
from .models import DcardPost, WeiboPost


# with open(os.path.join(BASE_DIR, 'static/json/weibo_punc_unique_20180820.json')) as fp:
#     weibo = json.load(fp)
# with open(os.path.join(BASE_DIR, 'static/json/dcard_punc_unique_20180818.json')) as fp:
#     dcard = json.load(fp)


class HomeView(FormView):
    template_name = "core/index.html"
    form_class = InputForm
    success_url = "/"

    # def form_valid(self, form):
    #     tags = form.cleaned_data.get('tags')
    #     filter_stopwords = form.cleaned_data.get('filter_stopwords')
    #     filter_punctuation = form.cleaned_data.get('filter_punctuation')
    #     # stats = get_stats(tags, dcard, weibo,
    #     #                   filter_stopwords=filter_stopwords, filter_punctuation=filter_punctuation)
    #     query_doc, similar_docs = get_similarities(tags, stats['dcard_posts'],
    #                                                stats['weibo_posts'])

    # return self.render_to_response(
    #     self.get_context_data(
    #         stats=True,
    #         dcard_posts=stats['dcard_posts'],
    #         weibo_posts=stats['weibo_posts'],
    #         dcard_sentiment=stats['dcard_sentiment'],
    #         weibo_sentiment=stats['weibo_sentiment'],
    #         weibo_average_post_length=stats['weibo_average_post_length'],
    #         dcard_average_post_length=stats['dcard_average_post_length'],
    #         total_weibo_posts=stats['total_weibo_posts'],
    #         total_dcard_posts=stats['total_dcard_posts'],
    #         weibo_male=stats['weibo_male'],
    #         weibo_female=stats['weibo_female'],
    #         dcard_male=stats['dcard_male'],
    #         dcard_female=stats['dcard_female'],
    #         weibo_freq=stats['weibo_freq'][:200],
    #         dcard_freq=stats['dcard_freq'][:200],
    #         query_doc=query_doc,
    #         similar_docs=similar_docs,
    #     )
    # )


class SearchListView(ListView):
    template_name = 'core/searchlistview.html'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = self.request.GET.get('tags').split(" ")
        filter_punctuation = self.request.GET.get('filter_punctuation')
        filter_stopwords = self.request.GET.get('filter_stopwords')
        dcard = DcardPost.objects.filter(tags__contains=tags).order_by('id')
        weibo = WeiboPost.objects.filter(tw_tags__contains=tags).order_by('id')
        stats = get_stats(dcard=dcard, weibo=weibo,
                          filter_punctuation=filter_punctuation, filter_stopwords=filter_stopwords)

        context['stats'] = stats
        context['tags'] = " ".join(tags)
        return context

    def get_queryset(self):
        tags = self.request.GET.get('tags')
        tags = tags.split(" ")
        forum = self.request.GET.get('forum')
        if forum == 'Dcard':
            self.model = DcardPost
            self.context_object_name = 'dcard'
            return DcardPost.objects.filter(tags__contains=tags)
        else:
            self.model = WeiboPost
            self.context_object_name = 'weibo'
            return WeiboPost.objects.filter(tw_tags__contains=tags)


def collocation_view(request):
    token = request.GET.get('token', None)
    table = request.GET.get('table', None)
    print(f"Got {token, table}")

    results = get_collocates(token, table)
    data = {
        'results': results
    }

    return JsonResponse(data)


def similarity_view(request):
    table = request.GET.get('table')
    query = request.GET.get('query')
    if table == 'weibo':
        query = WeiboPost.objects.get(id=query).cn_content_clean_seg
    else:
        query = DcardPost.objects.get(id=query).content_clean_seg
    tags = request.GET.get('tags')
    dcard = DcardPost.objects.filter(tags__icontains=tags)
    weibo = WeiboPost.objects.filter(tw_tags__icontains=tags)
    similar_docs = get_similarities(tag=tags, table=table, query=query, dcard=dcard, weibo=weibo)
    return JsonResponse({'similar_docs': similar_docs})
