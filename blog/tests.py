from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_post_list(self):
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
        
        #1. 메인 영역에 게시물이 하나도 없다면
        self.assertEqual(Post.objects.count(), 0)
        #2. '아직 게시물이 없습니다.' 라는 문구가 보인다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)
        
        #1. 게시물이 2개 있다면
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content = 'Hello World. We are the world.',
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content = '여러분 잘 따라오고 계시죠?',
        )
        self.assertEqual(Post.objects.count(), 2)
        
        #2. 포스트 목록 페이지를 새로고침 했을때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        #3. 메인 영역에 포스트 2개의 타이틀이 존재한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        #4. '아직 게시물이 없습니다.'라는 문구가 보이지 않는다.
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)
        
    