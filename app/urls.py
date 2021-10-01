from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard.as_view(), name='dashboard'),
    path('<tagname>', views.htmlView.as_view(), name='htmlview'),
    path('teacher-view/<id>', views.teacherView.as_view(), name='teacherview')
]