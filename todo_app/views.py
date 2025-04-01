from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Todo
from .forms import TodoForm

# Create your views here.

class TodoListView(ListView):
    model = Todo
    template_name = 'todo_app/todo_list.html'
    context_object_name = 'todos'

class TodoDetailView(DetailView):
    model = Todo
    template_name = 'todo_app/todo_detail.html'
    context_object_name = 'todo'

class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo_app/todo_form.html'
    success_url = reverse_lazy('todo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'タスクを作成しました。')
        return super().form_valid(form)

class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo_app/todo_form.html'
    success_url = reverse_lazy('todo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'タスクを更新しました。')
        return super().form_valid(form)

class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todo_app/todo_confirm_delete.html'
    success_url = reverse_lazy('todo_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'タスクを削除しました。')
        return super().delete(request, *args, **kwargs)

def change_status(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    
    if todo.status == '未完了':
        todo.status = '進行中'
    elif todo.status == '進行中':
        todo.status = '完了'
    else:
        todo.status = '未完了'
    
    todo.save()
    messages.success(request, f'「{todo.title}」のステータスを「{todo.status}」に変更しました。')
    return redirect('todo_list')
