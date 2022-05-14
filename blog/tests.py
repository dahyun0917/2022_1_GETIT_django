from multiprocessing import AuthenticationError
from urllib import response
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category,Tag

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_dahyun = User.objects.create_user(username='dahyun',password='pass4321')
        
        self.category_movie = Category.objects.create(name='movie',slug='movie')
        
        self.tag_python_kor = Tag.objects.create(name="파이썬 공부", slug="파이썬-공부")
        self.tag_python = Tag.objects.create(name="python", slug="python")
        self.tag_hello = Tag.objects.create(name="hello", slug="hello")
        
        
        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content = 'category가 없을 수도 있죠',
            author=self.user_dahyun
        )
        
        self.post_001.tags.add(self.tag_hello)
        
        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content = 'Hello World. We are the world.',
            category=self.category_movie,
            author=self.user_dahyun
        )
        
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content = '안녕하세요',
            category=self.category_movie,
            author=self.user_dahyun
        )
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor) 
    
    def category_card_test(self,soup):
        categories_card = soup.find('div',id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(
            f'{self.category_movie.name} ({self.category_movie.post_set.count()})',
            categories_card.text
        ) 
        self.assertIn(f'미분류 (1)',categories_card.text)
        
    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)
        
        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')
        
        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')
        
        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')
        
        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')
    
    def test_post_list(self):
        
        self.assertEqual(Post.objects.count(),3)
        #1. 포스트 목록 페이지
        response = self.client.get('/blog/')
        #2. 정상적으로 페이지가 로드되는 것
        self.assertEqual(response.status_code, 200)
        #3. 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        #4. 내비게이션 바 존재한다.
        #5. Blog, About Me 라는 문구가 내비게이션 바에 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        #1. 메인 영역에 게시물이 하나도 없다면
        #self.assertEqual(Post.objects.count(), 0)
        #2. '아직 게시물이 없습니다.' 라는 문구가 보인다.
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        
        #1. 게시물이 2개 있다면
        post_001_card = main_area.find('div',id='post-1')
        self.assertIn('미분류',post_001_card.text)
        self.assertIn(self.post_001.title,post_001_card.text)
        self.assertIn(self.tag_hello.name,post_001_card.text)
        self.assertNotIn(self.tag_python.name,post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name,post_001_card.text)
        
        post_002_card = main_area.find('div',id='post-2')
        self.assertIn(self.post_002.title,post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name,post_002_card.text)
        self.assertNotIn(self.tag_python.name,post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name,post_002_card.text)
        
        post_003_card = main_area.find('div',id='post-3')
        self.assertIn(self.post_003.title,post_003_card.text)
        self.assertIn(self.post_002.category.name, post_003_card.text)
        self.assertNotIn(self.tag_hello.name,post_003_card.text)
        self.assertIn(self.tag_python.name,post_003_card.text)
        self.assertIn(self.tag_python_kor.name,post_003_card.text)
        
        

        self.assertIn(self.user_dahyun.username.upper(),main_area.text)
        
        
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup=BeautifulSoup(response.content,'html.parser')
        main_area=soup.find('div',id='main-area')
        self.assertIn('아직 게시물이 없습니다',main_area.text)
     
        
    def test_post_detail(self):
        #1.포스트가 하나 있다
        # post_001 = Post.objects.create (
        #     title='첫 번째 포스트입니다.',
        #     content='Hello World. We are the world',
        #     author=self.user_dahyun
        # )
        #2.그 포스트의 url 은 '/blog/1/'이다.
        self.assertEqual(self.post_002.get_absolute_url(), '/blog/2/')
        
        #1. 첫 번째 포스트의 상세 페이지 테스트
        #2. 첫 번째 포스트의 url 로 접근하면 정상적으로 작동한다. (status code : 200)
        response= self.client.get(self.post_002.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        #3. 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        
        #4. 첫 번째 포스트의 제목이 웹 브라우저 타이틀에 들어있다.
        self.assertIn(self.post_002.title, soup.title.text)
        
        #5. 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_002.title, post_area.text)
        self.assertIn(self.category_movie.name,post_area.text)
        
        #6. 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다 (아직 구현할 수 없음)
        #아직 작성 불가
        
        #7. 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_002.content, post_area.text)
        
        self.assertNotIn(self.tag_hello.name,post_area.text)
        self.assertNotIn(self.tag_python.name,post_area.text)
        self.assertNotIn(self.tag_python_kor.name,post_area.text)
        
        self.assertIn(self.user_dahyun.username.upper(),post_area.text)

        
    def test_category_page(self):
        response = self.client.get(self.category_movie.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup=BeautifulSoup(response.content,'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        self.assertIn(self.category_movie.name, soup.h1.text)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_movie.name, main_area.text)
        self.assertIn(self.post_002.title,main_area.text)
        self.assertNotIn(self.post_001.title,main_area.text)
        
        