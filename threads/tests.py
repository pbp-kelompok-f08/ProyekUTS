from django.test import TestCase,Client
from accounts.models import CustomUser
from threads.models import Thread, ReplyChild
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ThreadViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="12345")
        self.thread = Thread.objects.create(
            user=self.user,
            content="Hello World",
            tags="intro,test"
        )
        self.reply = ReplyChild.objects.create(
            thread=self.thread,
            content="Nice post!",
            user=self.user
        )

    def test_show_main_requires_login(self):
        response = self.client.get(reverse("threads:show_main"))
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.client.login(username="tester", password="12345")
        response = self.client.get(reverse("threads:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main_threads.html")

    def test_show_json_returns_threads(self):
        self.client.login(username="tester", password="12345")
        response = self.client.get(reverse("threads:show_json"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("content", data[0])
        self.assertEqual(data[0]["content"], "Hello World")

    def test_add_thread_entry_ajax(self):
        self.client.login(username="tester", password="12345")
        response = self.client.post(
            reverse("threads:add_thread_entry_ajax"),
            {"content": "New post!", "tags": "fun"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Thread.objects.filter(content="New post!").exists())

    def test_delete_thread(self):
        self.client.login(username="tester", password="12345")
        response = self.client.get(reverse("threads:delete_thread", args=[self.thread.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Thread.objects.filter(id=self.thread.id).exists())

    def test_get_replies_by_threadId(self):
        self.client.login(username="tester", password="12345")
        response = self.client.get(reverse("threads:get_replies_by_threadId", args=[self.thread.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("content", data[0])

    def test_add_reply_entry_ajax(self):
        self.client.login(username="tester", password="12345")
        response = self.client.post(
            reverse("threads:add_reply_entry_ajax", args=[self.thread.id]),
            {"content": "This is a reply."}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("content", data)
        self.assertEqual(data["content"], "This is a reply.")

    def test_like_thread_ajax(self):
        self.client.login(username="tester", password="12345")
        response = self.client.post(reverse("threads:like_thread_ajax", args=[self.thread.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("likeCount", data)
        self.assertTrue(data["isLiked"])

    def test_like_reply_ajax(self):
        self.client.login(username="tester", password="12345")
        response = self.client.post(reverse("threads:like_reply_ajax", args=[self.reply.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("isLiked", data)
        self.assertTrue(data["isLiked"])

    def test_delete_reply(self):
        self.client.login(username="tester", password="12345")
        response = self.client.get(reverse("threads:delete_reply", args=[self.reply.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ReplyChild.objects.filter(id=self.reply.id).exists())

class ThreadModelTests(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = CustomUser.objects.create_user(username="user1", password="pass123")
        self.user2 = CustomUser.objects.create_user(username="user2", password="pass123")

        # Create a thread
        self.thread = Thread.objects.create(
            user=self.user1,
            content="This is a test thread.",
            tags="test,thread",
            image="https://example.com/image.png"
        )

    def test_thread_creation(self):
        """Ensure thread is created correctly."""
        self.assertEqual(self.thread.user, self.user1)
        self.assertEqual(self.thread.likeCount, 0)
        self.assertEqual(self.thread.shareCount, 0)
        self.assertEqual(self.thread.replyCount, 0)
        self.assertEqual(str(self.thread.content), "This is a test thread.")

    def test_change_like_add_and_remove(self):
        """Test liking and unliking a thread toggles correctly."""
        result = self.thread.changeLike(self.user2)
        self.assertTrue(result)
        self.assertEqual(self.thread.likeCount, 1)
        self.assertIn(self.user2, self.thread.liked_by.all())

        result = self.thread.changeLike(self.user2)
        self.assertFalse(result)
        self.assertEqual(self.thread.likeCount, 0)
        self.assertNotIn(self.user2, self.thread.liked_by.all())

    def test_change_share_increments_and_decrements(self):
        """Test share counter increments and decrements."""
        self.thread.changeShare(True)
        self.assertEqual(self.thread.shareCount, 1)
        self.thread.changeShare(False)
        self.assertEqual(self.thread.shareCount, 0)

    def test_change_reply_increments_and_decrements(self):
        """Test reply counter increments and decrements."""
        self.thread.changeReply(True)
        self.assertEqual(self.thread.replyCount, 1)
        self.thread.changeReply(False)
        self.assertEqual(self.thread.replyCount, 0)

    def test_replychild_creation_and_like_toggle(self):
        """Ensure replies can be created and liked properly."""
        reply = ReplyChild.objects.create(
            thread=self.thread,
            user=self.user2,
            content="This is a reply."
        )

        self.assertEqual(reply.thread, self.thread)
        self.assertEqual(reply.likeCount, 0)
        self.assertEqual(reply.content, "This is a reply.")

        # Like the reply
        result = reply.changeLike(self.user1)
        self.assertTrue(result)
        self.assertEqual(reply.likeCount, 1)
        self.assertIn(self.user1, reply.liked_by.all())

        # Unlike it
        result = reply.changeLike(self.user1)
        self.assertFalse(result)
        self.assertEqual(reply.likeCount, 0)
        self.assertNotIn(self.user1, reply.liked_by.all())
