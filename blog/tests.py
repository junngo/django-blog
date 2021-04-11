from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(soup.title.text, "Blog")

        navbar = soup.nav
        self.assertIn("Blog", navbar.text)
        self.assertIn("About me", navbar.text)

        self.assertEqual(Post.objects.count(), 0)
        main_area = soup.find("div", id="main-area")
        self.assertIn("No Posts", main_area.text)

        post_001 = Post.objects.create(
            title="First Post",
            content="This is First Post.",
        )
        post_002 = Post.objects.create(
            title="Second Post",
            content="Fisrt is not all "
        )
        self.assertEqual(Post.objects.count(), 2)

        response = self.client.get("/blog/")
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(response.status_code, 200)

        main_area = soup.find("div", id="main-area")
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)

        self.assertNotIn("No Posts", main_area.text)

    def test_post_detail(self):
        post_001 = Post.objects.create(
            title="First Post",
            content="Hello World. We are First Post."
        )
        self.assertEqual(post_001.get_absolute_url(), "/blog/1/")

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        navbar = soup.nav
        self.assertIn("Blog", navbar.text)
        self.assertIn("About me", navbar.text)

        # self.assertIn(post_001.title, soup.title.text)

        # main_area = soup.find("div", id="main-area")
        # post_area = main_area.find("div", id="post-area")
        # self.assertIn(post_001.title, post_area.text)
        # self.assertIn(post_001.content, post_area.text)
