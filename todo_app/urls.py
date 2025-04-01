from django.urls import path
from . import views

urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo_list'),
    path('todo/<int:pk>/', views.TodoDetailView.as_view(), name='todo_detail'),
    path('todo/new/', views.TodoCreateView.as_view(), name='todo_new'),
    path('todo/<int:pk>/edit/', views.TodoUpdateView.as_view(), name='todo_edit'),
    path('todo/<int:pk>/delete/', views.TodoDeleteView.as_view(), name='todo_delete'),
    path('todo/<int:pk>/change_status/', views.change_status, name='change_status'),
] 