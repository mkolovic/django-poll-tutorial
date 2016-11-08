from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Question, Choice

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions, not including those to be
        published in the future or those without choices available.
        """

        return (Question.objects.annotate(num_choice=Count('choice'))
                                .filter(pub_date__lte=timezone.now(),
                                        num_choice__gt=0)
                                .order_by('-pub_date')[:5])


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Return the last five published questions, not including those to be
        published in the future or those without choices available.
        """
        return (Question.objects.annotate(num_choice=Count('choice'))
                                .filter(pub_date__lte=timezone.now(),
                                        num_choice__gt=0))

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Return the last five published questions, not including those to be
        published in the future or those without choices available.
        """
        return (Question.objects.annotate(num_choice=Count('choice'))
                                .filter(pub_date__lte=timezone.now(),
                                        num_choice__gt=0))


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html',
                      {'question': question,
                       'error_message': "You didn't select a choice.",})
    else:
        selected_choice.votes += 1
        selected_choice.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
