import json
import os

from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import InputForm
from .utils import get_stats, get_similarities, get_collocates
from web.settings import BASE_DIR
# class Home(TemplateView):
#     template_name = "core/index.html"

with open(os.path.join(BASE_DIR, 'static/json/weibo_punc_unique_20180818.json')) as fp:
    weibo = json.load(fp)
with open(os.path.join(BASE_DIR, 'static/json/dcard_punc_unique_20180818.json')) as fp:
    dcard = json.load(fp)


class HomeView(FormView):
    template_name = "core/index.html"
    form_class = InputForm
    success_url = "/"

    def form_valid(self, form):
        tags = form.cleaned_data.get('tags')
        filter_stopwords = form.cleaned_data.get('filter_stopwords')
        filter_punctuation = form.cleaned_data.get('filter_punctuation')
        stats = get_stats(tags, dcard, weibo,
                          filter_stopwords=filter_stopwords, filter_punctuation=filter_punctuation)
        query_doc, similar_docs = get_similarities(tags, stats['dcard_posts'],
                                                   stats['weibo_posts'])

        return self.render_to_response(
            self.get_context_data(
                stats=True,
                dcard_posts=stats['dcard_posts'],
                weibo_posts=stats['weibo_posts'],
                weibo_average_post_length=stats['weibo_average_post_length'],
                dcard_average_post_length=stats['dcard_average_post_length'],
                total_weibo_posts=stats['total_weibo_posts'],
                total_dcard_posts=stats['total_dcard_posts'],
                weibo_male=stats['weibo_male'],
                weibo_female=stats['weibo_female'],
                dcard_male=stats['dcard_male'],
                dcard_female=stats['dcard_female'],
                weibo_freq=stats['weibo_freq'][:200],
                dcard_freq=stats['dcard_freq'][:200],
                query_doc=query_doc,
                similar_docs=similar_docs,
            )
        )


def collocation_view(request):
    token = request.GET.get('token', None)
    table = request.GET.get('table', None)
    print(f"Got {token, table}")

    results = get_collocates(token, table)
    data = {
        'results': results
    }

    return JsonResponse(data)



