import datetime
from urllib import response

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() devuelve False para las preguntas
        cuyo pub_date están en el futuro
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
        
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() devuelve False para las preguntas
        cuyo pub_date tiene más de 1 día
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)
        
    def test_was_published_recently_with_recent_questiojn(self):
        """
        was_published_recently() devuelve True para las preguntas
        cuyo pub_date es dentro del ultimo día
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Crea una pregunta con el 'question_text' y publica el número de días 
    dado en 'days' a partir de hoy (negativo para las preguntas del pasado,
    positivo para las preguntas que aun no se han publicado).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewtext(TestCase):
    def test_no_question(self):
        """
        Si no exiten preguntas, se muestra un mensaje apropiado
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_question(self):
        """
        Las preguntas con pub_date del pasado son mostradas en el index
        """
        question = create_question(question_text='Past question.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])
    
    def test_future_question(self):
        """
        Las preguntas con pub_date del futuro no son mostradas en el index
        """
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_future_question_and_past_question(self):
        """
        Aunque existan preguntas pasadas y futuras, solo las pasadas son mostradas
        """
        question = create_question(question_text='Past question.', days=-30)
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            [question],
        )
    
    def test_two_past_questions(self):
        """
        El index puede mostrar multiples preguntas
        """
        question1 = create_question(question_text='Past question 1.', days=-30)
        question2 = create_question(question_text='Past question 2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            [question2, question1],
        )


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
        La vista detallada de una pregunta con pub_date del futuro devuelve '404 not found'
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        La vista dellada de una pregunta con pub_date del pasado
        muestra el texto de la pregunta
        """
        past_question = create_question(question_text='Past question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)