import datetime

from django.utils import timezone
from django.urls import reverse
from django.test import TestCase

from .models import Question

# Create your tests here.
def create_question(question_text, days):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text, votes):
    """
    Create a choice related to the given question with a set number of votes.
    Return the given question.
    """
    return question.choice_set.create(choice_text=choice_text, votes=votes)


class IndexTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question_with_a_choice(self):
        """
        Questions with a pub_date in the past and at least one choice
        should be displayed on the index page.
        """
        q = create_question(question_text="Past question.", days=-30)
        create_choice(q, choice_text="Past choice.", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question.>'])

    def test_index_view_with_a_past_question_with_no_choice(self):
        """
        Questions with a pub_date in the past but no choices should not be
        displayed on the index page.
        """
        create_question(question_text="Past question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_index_view_with_a_future_question_with_a_choice(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        q = create_question(question_text="Future question.", days=30)
        create_choice(q, choice_text="Future choice.", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_future_question_with_no_choice(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        qp = create_question(question_text="Past question.", days=-30)
        create_choice(qp, choice_text="Past choice.", votes=0)
        qf = create_question(question_text="Future question.", days=30)
        create_choice(qf, choice_text="Future choice.", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question.>'])

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        q1 = create_question(question_text="Past question 1.", days=-30)
        create_choice(q1, choice_text="Past choice 1.", votes=0)
        q2 = create_question(question_text="Past question 2.", days=-5)
        create_choice(q2, choice_text="Past choice 2.", votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question 2.>',
                                  '<Question: Past question 1.>'])


class QuestionDetailTests(TestCase):
    def test_detail_view_with_a_future_question_with_a_choice(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        create_choice(future_question, choice_text="Future choice", votes=0)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question_with_a_choice(self):
        """
        The detail view of a question with a pub_date in the past and at least
        should one choice should display the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        past_question.choice_set.create(choice_text="Past choice.", votes=0)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        self.assertContains(response, past_question.choice_set.all()[0].choice_text)

    def test_detail_view_with_a_past_question_with_no_choice(self):
        """
        The detail view should return 404 not found if a question does not
        have choices.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultsTests(TestCase):
    def test_results_view_with_future_question(self):
        """
        The results view for a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        future_question.choice_set.create(choice_text="Future choice.")
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionMethodTests(TestCase):

    def test_recent_publish_with_old_question(self):
        """
        recent_publish() should return False for questions whose
        pub_date is older than 1 day.
        """

        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)

        self.assertIs(old_question.recent_publish(), False)

    def test_recent_publish_with_recent_question(self):
        """
        recent_publish() should return True for questions whose
        pub_date is within the last day.
        """

        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)

        self.assertIs(recent_question.recent_publish(), True)

    def test_recent_publish_with_future_question(self):
        """
        recent_publish() should return False for questions whose
        pub_date is in the future.
        """

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.recent_publish(), False)
