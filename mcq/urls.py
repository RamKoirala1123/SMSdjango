from django.urls import path

from mcq.views import MCQView, MCQDetailView, MCQAnswerView, MCQQuestionsView, MCQQuestionsDetailView
urlpatterns = [
    path('', MCQView.as_view(), name='mcq'),
    path('<int:mcqid>/', MCQDetailView.as_view(), name='mcq_detail_view'),
    path('<int:mcqid>/questions/', MCQQuestionsView.as_view(),
         name='mcq_questions_detail_view'),
    path('<int:mcqid>/questions/<int:questionid>/',
         MCQQuestionsDetailView.as_view(), name='mcq_question_detail_view'),
    path('<int:mcqid>/questions/<int:questionid>/<str:username>/',
         MCQAnswerView.as_view(), name='mcq_q')
]
