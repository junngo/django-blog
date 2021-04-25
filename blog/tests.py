from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username="trump", password="somepassword")
        self.user_obama = User.objects.create_user(username="obama", password="somepassword")

        self.category_programming = Category.objects.create(name="programming", slug="programming")
        self.category_music = Category.objects.create(name="music", slug="music")

        self.tag_python_kor = Tag.objects.create(name="python korea", slug="python-korea")
        self.tag_python = Tag.objects.create(name="python", slug="python")
        self.tag_hello = Tag.objects.create(name="hello", slug="hello")

        self.post_001 = Post.objects.create(
            title="First Post",
            content="This is First Post.",
            category = self.category_programming,
            author=self.user_trump,
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title="Second Post",
            content="Fisrt is not all",
            category = self.category_music,
            author=self.user_obama,
        )
        self.post_003 = Post.objects.create(
            title="Third Post",
            content="Not exist Category",
            author=self.user_obama,
        )
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)


    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn("Blog", navbar.text)
        self.assertIn("About me", navbar.text)

        logo_btn = navbar.find("a", text="Jun Blog")
        self.assertEqual(logo_btn.attrs["href"], "/")

        home_btn = navbar.find("a", text="Home")
        self.assertEqual(home_btn.attrs["href"], "/")

        blog_btn = navbar.find("a", text="Blog")
        self.assertEqual(blog_btn.attrs["href"], "/blog/")

        about_me_btn = navbar.find("a", text="About me")
        self.assertEqual(about_me_btn.attrs["href"], "/about_me/")

    def category_card_test(self, soup):
        categories_card = soup.find("div", id="categories-card")
        self.assertIn("Categories", categories_card.text)
        self.assertIn(
            f"{self.category_programming.name} ({self.category_programming.post_set.count()})"
            , categories_card.text
        )
        self.assertIn(
            f"{self.category_music.name} ({self.category_music.post_set.count()})"
            , categories_card.text
        )
        self.assertIn(
            f"No Category (1)"
            , categories_card.text
        )

    def test_post_list(self):
        # Exist Post
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find("div", id="main-area")
        self.assertNotIn("No Post", main_area.text)

        post_001_card = main_area.find("div", id="post-1")
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find("div", id="post-2")
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find("div", id="post-3")
        self.assertIn("No Category", post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # No Exist Post
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get("/blog/")
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")
        self.assertIn("No Post", main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), "/blog/1/")

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find("div", id="main-area")
        post_area = main_area.find("div", id="post-area")
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        self.assertIn(self.user_trump.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find("div", id="main-area")
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find("div", id="main-area")
        self.assertIn(self.tag_hello.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
