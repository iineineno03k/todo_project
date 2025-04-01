# DjangoでTODOアプリを作成しRenderにデプロイする手順

この記事では、Djangoを使用してシンプルなTODOアプリケーションを作成し、Renderにデプロイするまでの手順を解説します。

## 目次
1. [開発環境のセットアップ](#1-開発環境のセットアップ)
2. [Djangoプロジェクトの作成](#2-djangoプロジェクトの作成)
3. [TODOアプリの実装](#3-todoアプリの実装)
4. [ローカル環境での動作確認](#4-ローカル環境での動作確認)
5. [Renderへのデプロイ準備](#5-renderへのデプロイ準備)
6. [Renderへのデプロイ](#6-renderへのデプロイ)
7. [トラブルシューティング](#7-トラブルシューティング)
8. [データベースについての補足](#8-データベースについての補足)
9. [その他の参考情報](#9-その他の参考情報)

## 1. 開発環境のセットアップ

### 仮想環境の作成と有効化

```bash
# 仮想環境の作成
python -m venv todo_env

# 仮想環境の有効化（macOS/Linux）
source todo_env/bin/activate

# 仮想環境の有効化（Windows）
# todo_env\Scripts\activate
```

### 必要なパッケージのインストール

```bash
pip install django
```

## 2. Djangoプロジェクトの作成

### プロジェクトの作成

```bash
django-admin startproject todo_project
cd todo_project
```

### アプリケーションの作成

```bash
python manage.py startapp todo_app
```

### settings.pyの設定

`todo_project/settings.py`にアプリケーションを追加します。

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'todo_app',  # 追加
]

# 言語と時間帯の設定
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
```

### URLの設定

`todo_project/urls.py`を編集して、TODOアプリのURLを設定します。

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo_app.urls')),
]
```

## 3. TODOアプリの実装

### モデルの作成

`todo_app/models.py`にTodoモデルを定義します。

```python
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
```

### フォームの作成

`todo_app/forms.py`を作成し、Todoモデル用のフォームを定義します。

```python
from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'status', 'priority', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
```

### ビューの作成

`todo_app/views.py`に必要なビューを実装します。

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Todo
from .forms import TodoForm

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
```

### URLの設定

`todo_app/urls.py`を作成し、ビューとURLのマッピングを定義します。

```python
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
```

### テンプレートの作成

テンプレートディレクトリとファイルを作成します。

```bash
mkdir -p todo_app/templates/todo_app
```

`todo_app/templates/todo_app/base.html`（基本テンプレート）:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TODOアプリ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <header class="mb-4">
            <h1><a href="{% url 'todo_list' %}" class="text-decoration-none">TODOアプリ</a></h1>
        </header>
        
        {% if messages %}
        <div class="messages">
            {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">
                {{ message }}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <main>
            {% block content %}
            {% endblock %}
        </main>
        
        <footer class="mt-5 text-center text-muted">
            <p>Django TODO App</p>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

その他必要なテンプレートファイル（リスト表示、詳細表示、フォーム、削除確認など）も作成します。

### データベースのマイグレーション

```bash
python manage.py makemigrations
python manage.py migrate
```

### 管理サイトの設定

`todo_app/admin.py`を編集して管理サイトにTodoモデルを登録します。

```python
from django.contrib import admin
from .models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')
```

## 4. ローカル環境での動作確認

### 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ にアクセスして動作を確認します。

### 管理者アカウントの作成

```bash
python manage.py createsuperuser
```

プロンプトに従って、ユーザー名、メールアドレス、パスワードを入力します。
作成後、http://127.0.0.1:8000/admin/ にアクセスして管理サイトにログインできます。

## 5. Renderへのデプロイ準備

### 必要なファイルの作成

#### requirements.txt

プロジェクトの依存関係を記述するファイルを作成します。

```
asgiref==3.8.1
Django==5.1.7
sqlparse==0.5.3
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
python-dotenv==1.0.1

# PostgreSQLは使用しないので削除
# psycopg2-binary==2.9.9
```

#### Procfile

Renderがアプリケーションを起動するためのコマンドを記述します。

```
web: gunicorn todo_project.wsgi
```

#### runtime.txt

使用するPythonのバージョンを指定します。

```
python-3.13.0
```

#### .gitignore

バージョン管理から除外するファイルを指定します。

```
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
*.sqlite3
.DS_Store
staticfiles/
.env.local
.env.development.local
.env.test.local
.env.production.local
```

### settings.pyの修正

本番環境向けに`todo_project/settings.py`を修正します。

```python
import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-=h0s7pk9e+#ixlm&aru9#0vg#hv$$!s+fbe6f3da37kb)-^nko')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # 開発中はTrueに、本番環境ではFalseに設定

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']

# ... (他の設定)

# 静的ファイルの設定
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ミドルウェアにWhiteNoiseを追加
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 追加
    # ... (他のミドルウェア)
]

# データベース設定（SQLite）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# セキュリティ設定
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1年
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 静的ファイルの収集

```bash
python manage.py collectstatic
```

## 6. Renderへのデプロイ

### Renderアカウントの作成

Renderの[公式サイト](https://render.com/)にアクセスし、アカウントを作成します。

### 新しいWebサービスの作成

1. ダッシュボードから「New +」→「Web Service」を選択
2. GitHubのリポジトリを接続（事前にGitHubにコードをプッシュしておく必要があります）
3. 以下の設定を行います：

- **Name**: `todo-project`（任意の名前）
- **Environment**: `Python`
- **Region**: お近くのリージョンを選択
- **Branch**: `main`（または使用するブランチ）
- **Build Command**: 
```
pip install -r requirements.txt && python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput
```
- **Start Command**: 
```
gunicorn todo_project.wsgi
```
- **Plan**: 無料プラン（Free）を選択

### 環境変数の設定

「Environment」タブで以下の環境変数を設定します：

- **SECRET_KEY**: 安全な秘密鍵（以下のコマンドで生成できます）
  ```python
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

### デプロイの開始

「Create Web Service」ボタンをクリックしてデプロイを開始します。
ビルドとデプロイのプロセスが完了するまで待ちます（数分かかる場合があります）。

デプロイが完了すると、`https://todo-project-xxxx.onrender.com`のようなURLが生成されます。
このURLにアクセスして、アプリケーションが正常に動作することを確認します。

## 7. トラブルシューティング

### デバッグモードの有効化

エラーが発生した場合、一時的にDEBUGモードを有効にしてエラーメッセージを確認できます：

```python
# settings.py
DEBUG = True
```

### データベースの問題

よくある問題として「no such table」エラーがあります。これはマイグレーションが正しく適用されていない場合に発生します。
ビルドコマンドに`python manage.py makemigrations`と`python manage.py migrate`が含まれていることを確認してください。

### 静的ファイルの問題

静的ファイルが正しく表示されない場合は、以下を確認してください：

1. `STATIC_ROOT`が正しく設定されているか
2. `STATICFILES_STORAGE`に`whitenoise.storage.CompressedManifestStaticFilesStorage`が設定されているか
3. `collectstatic`コマンドがビルド時に実行されているか

## 8. データベースについての補足

### Renderでの永続的なデータベース

Renderでは、デフォルトではファイルシステムがデプロイごとにリセットされるため、SQLiteデータベースのデータは失われます。永続的なデータを保存するには、以下のいずれかの方法を選択します：

1. **PostgreSQLやMySQLの使用（推奨）**

    外部のミドルウェアを利用します。RenderではPostgreSQLも提供されているため、そちらを利用するのがベターです。
    詳しい設定方法は後述します。

2. **ディスクの追加**

   Renderのダッシュボードで永続的なディスクを追加し、そこにSQLiteデータベースを保存する方法もあります。
   
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join('/opt/render/project/database', 'db.sqlite3'),
       }
   }
   ```

3. **デプロイごとにマイグレーションを実行**

   小規模なプロジェクトやデモでは、デプロイごとに新しいデータベースを作成する方法も使えます。
   この方法ではデータは永続的ではありませんが、設定がシンプルです。

### MySQLを使用する場合の設定

もしRenderでMySQLを使用したい場合は、外部のMySQLサービス（例：Amazon RDS、PlanetScaleなど）と接続する必要があります。以下に設定例を示します：

1. **必要なパッケージのインストール**

   ```bash
   pip install mysqlclient
   ```

   そして`requirements.txt`に追加します：

   ```
   mysqlclient==2.2.2
   ```

2. **settings.pyの設定**

   ```python
   # 環境変数または.envファイルから接続情報を取得
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ.get('DB_NAME', 'todo_db'),
           'USER': os.environ.get('DB_USER', 'root'),
           'PASSWORD': os.environ.get('DB_PASSWORD', ''),
           'HOST': os.environ.get('DB_HOST', 'localhost'),
           'PORT': os.environ.get('DB_PORT', '3306'),
           'OPTIONS': {
               'charset': 'utf8mb4',
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }
   ```

3. **環境変数の設定**

   Renderのダッシュボードで以下の環境変数を設定します：
   - `DB_NAME`: データベース名
   - `DB_USER`: ユーザー名
   - `DB_PASSWORD`: パスワード
   - `DB_HOST`: MySQLサーバーのホスト名
   - `DB_PORT`: ポート番号（通常は3306）

### PostgreSQLを使用する場合の最適設定

RenderのマネージドPostgreSQLサービスを使用する場合の最適な設定です：

1. **データベースの作成**
   
   Renderダッシュボードから「New +」→「PostgreSQL」を選択し、新しいデータベースを作成します。
   作成後、接続情報（特に`DATABASE_URL`）が提供されます。

2. **Webサービスとデータベースの接続**

   作成したWebサービスの「Environment」タブで、「Add Internal Database」をクリックし、先ほど作成したPostgreSQLデータベースを選択します。
   これにより、自動的に`DATABASE_URL`環境変数が設定されます。

3. **settings.pyの設定**

   ```python
   import dj_database_url

   # DATABASE_URLが設定されていればそれを使用
   if 'DATABASE_URL' in os.environ:
       DATABASES = {
           'default': dj_database_url.config(
               conn_max_age=600,
               conn_health_checks=True,
           )
       }
   else:
       # ローカル開発用のSQLite設定
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'db.sqlite3',
           }
       }
   ```

4. **必要なパッケージの追加**

   ```
   psycopg2-binary==2.9.9
   ```

この設定により、ローカル開発ではSQLiteを使用し、Render上ではPostgreSQLを使用するハイブリッド構成が実現できます。

## 9. その他の参考情報

### RenderでのPython環境とDocker環境の違い

Renderでは、Pythonアプリケーションをデプロイする方法として「Python」環境と「Docker」環境の2つのオプションがあります。それぞれの特徴を比較してみましょう。

#### Python環境（Native Environment）

**メリット:**
- 設定が簡単で、Python特有の知識だけで十分
- Renderによって最適化されたPython実行環境
- `requirements.txt`ファイルのみでパッケージ管理が可能
- ビルドが高速（通常、Dockerビルドより速い）
- Renderによる自動的な環境のアップグレードと保守

**デメリット:**
- カスタマイズの自由度がやや低い
- Pythonアプリケーション専用（他の言語との混在が難しい）
- システムレベルの依存関係のインストールが限定的

**設定例:**
```
# Build Command
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput

# Start Command
gunicorn todo_project.wsgi
```

#### Docker環境

**メリット:**
- 完全なカスタマイズが可能（どんなコンテナイメージも使用可能）
- 複雑な依存関係や特殊なシステムパッケージのインストールが可能
- 開発と本番環境の完全な一貫性を確保できる
- 複数の言語や技術を組み合わせたアプリケーションに適している
- 特定のPythonバージョンや特殊なライブラリの使用が容易

**デメリット:**
- Dockerfileの作成と管理が必要（学習コストが高い）
- ビルド時間が長くなる場合がある
- イメージサイズの管理が必要
- 設定ミスによるデバッグが複雑になることがある

**Dockerfile例:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "todo_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### どちらを選ぶべきか？

- **Python環境が適している場合:**
  - 標準的なDjangoアプリケーション
  - Docker知識がない、または学習中の場合
  - シンプルな依存関係を持つプロジェクト
  - 迅速なデプロイを優先する場合

- **Docker環境が適している場合:**
  - カスタムシステムパッケージが必要な場合
  - 特殊なPython拡張や特定バージョンのPythonが必要な場合
  - マイクロサービスアーキテクチャを採用している場合
  - 複数の言語やサービスを組み合わせている場合
  - チーム内にDocker経験者がいる場合

今回のTODOアプリケーションのような比較的シンプルなDjangoアプリケーションでは、Python環境を選択するのが最も簡単で効率的です。より複雑なプロジェクトや特殊な要件がある場合は、Docker環境を検討することをおすすめします。

### まとめ

この記事では、DjangoでTODOアプリケーションを作成し、Renderにデプロイする方法を解説しました。
基本的なCRUD操作を持つアプリケーションを構築し、本番環境にデプロイするまでの手順を学びました。

さらに、異なるデータベース（SQLite, PostgreSQL, MySQL）の設定方法や、RenderでのPython環境とDocker環境の違いについても解説しました。

Djangoは強力なWebフレームワークであり、さまざまなWebアプリケーションの開発に利用できます。
Renderは、簡単にPythonアプリケーションをデプロイできるプラットフォームで、個人プロジェクトや小規模なアプリケーションの公開に適しています。

ぜひこの記事を参考に、自分だけのWebアプリケーションを開発してみてください！ 