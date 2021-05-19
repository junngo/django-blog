from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username="trump", password="somepassword")
        self.user_obama = User.objects.create_user(username="obama", password="somepassword")
        self.user_obama.is_staff = True
        self.user_obama.save()

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

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content="This is first comment"
        )


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

        # comment area
        comments_area = soup.find("div", id="comment-area")
        comment_001_area = comments_area.find("div", id="comment-1")
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

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

    def test_create_post(self):
        response = self.client.get("/blog/create_post/")
        self.assertNotEqual(response.status_code, 200)

        # Not Staff user - Trump
        self.client.login(username="trump", password="somepassword")
        response = self.client.get("/blog/create_post/")
        self.assertNotEqual(response.status_code, 200)

        # Staff user - Obama
        self.client.login(username="obama", password="somepassword")
        response = self.client.get("/blog/create_post/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual("Create Post - Blog", soup.title.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn("Create New Post", main_area.text)

        tag_str_input = main_area.find("input", id="id_tags_str")
        self.assertTrue(tag_str_input)

        self.client.post(
            "/blog/create_post/",
            {
                "title": "Making post Form",
                "content": "Start to makie post Form",
                "tags_str": "new tag; HanGle Tag, python",
            }

        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Making post Form")

        self.assertEqual(last_post.author.username, "obama")
        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name="new tag"))
        self.assertTrue(Tag.objects.get(name="HanGle Tag"))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f"/blog/update_post/{self.post_003.pk}/"

        # Not log in
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # log in, not author on post
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(
            username=self.user_trump.username,
            password="somepassword"
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # log in and author on post
        self.client.login(
            username=self.post_003.author.username,
            password="somepassword"
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        self.assertEqual("Edit Post - Blog", soup.title.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn("Edit Post", main_area.text)

        tag_str_input = main_area.find("input", id="id_tags_str")
        self.assertTrue(tag_str_input)
        self.assertIn("python korea; python", tag_str_input.attrs["value"])

        response = self.client.post(
            update_post_url,
            {
                "title": "This is 3rd",
                "content": "Hello, We are the one",
                "category": self.category_music.pk,
                "tags_str": "python study; HanGle Tag, some tag",
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")
        self.assertIn("This is 3rd", main_area.text)
        self.assertIn("Hello, We are the one", main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn("python study", main_area.text)
        self.assertIn("HanGle Tag", main_area.text)
        self.assertIn("some tag", main_area.text)
        self.assertIn("HanGle Tag", main_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        # Not log in
        comment_area = soup.find("div", id="comment-area")
        self.assertIn("Log in and leave a comment", comment_area.text)
        self.assertFalse(comment_area.find("form"))

        # Log in
        self.client.login(username="obama", password="somepassword")
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        comment_area = soup.find("div", id="comment-area")
        self.assertNotIn("Log in and leave a comment", comment_area.text)

        comment_form = comment_area.find("form", id="comment-form")
        self.assertTrue(comment_form.find("textarea", id="id_content"))
        response = self.client.post(
            self.post_001.get_absolute_url + "new_comment/",
            {
                "content": "That is Obama comment",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()

        soup = BeautifulSoup(response.content, "html.parser")
        self.assertIn(new_comment.post.title, soup.title.text)

        comment_area = soup.find("div", id="comment-area")
        new_comment_div = comment_area.find("div", id=f"comment-{new_comment.pk}")
        self.assertIn("obama", new_comment_div.text)
        self.assertIn("That is Obama comment", new_comment_div.text)
