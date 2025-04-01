from django.db import models
from django.utils import timezone

class Todo(models.Model):
    STATUS_CHOICES = (
        ('未完了', '未完了'),
        ('進行中', '進行中'),
        ('完了', '完了'),
    )
    
    title = models.CharField('タイトル', max_length=100)
    description = models.TextField('詳細', blank=True)
    status = models.CharField('ステータス', max_length=10, choices=STATUS_CHOICES, default='未完了')
    priority = models.IntegerField('優先度', default=0)
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    due_date = models.DateField('期限', null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'
