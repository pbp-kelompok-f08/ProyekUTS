from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from matches.models import Match, Participation, SportCategory
from liveChat.models import Group, Chat
import json
import uuid


class LiveChatGroupTestCase(TestCase):
    """Test cases for Group operations in liveChat app"""
    
    def setUp(self):
        self.client = Client()
        
        self.user1 = CustomUser.objects.create_user(
            username='chat_user1',
            password='chat123',
            role='user',
            email='user1@test.com'
        )
        self.user2 = CustomUser.objects.create_user(
            username='chat_user2',
            password='chat123',
            role='user',
            email='user2@test.com'
        )
        self.admin = CustomUser.objects.create_user(
            username='chat_admin',
            password='admin123',
            role='admin',
            email='admin@test.com'
        )

        self.category = SportCategory.objects.create(name='Basket')
        self.match1 = Match.objects.create(
            title='Basketball Game',
            category=self.category,
            location='Court A',
            event_date=timezone.now() + timedelta(days=5),
            max_members=8
        )
        self.match2 = Match.objects.create(
            title='Basketball Tournament',
            category=self.category,
            location='Court B',
            event_date=timezone.now() + timedelta(days=10),
            max_members=10
        )

        self.group1 = Group.objects.create(
            match=self.match1,
            name='Group Basketball Game'
        )
        self.group2 = Group.objects.create(
            match=self.match2,
            name='Group Basketball Tournament'
        )

        Participation.objects.create(match=self.match1, user=self.user1, message='')
        Participation.objects.create(match=self.match2, user=self.user2, message='')

    def test_show_main_page(self):
        """Test accessing main live chat page"""
        self.client.login(username='chat_user1', password='chat123')
        response = self.client.get(reverse('liveChat:show_main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chat_user1')

    def test_show_main_requires_login(self):
        """Test main page requires authentication"""
        response = self.client.get(reverse('liveChat:show_main'))
        self.assertEqual(response.status_code, 302)

    def test_get_user_groups(self):
        """Test regular user getting their groups"""
        self.client.login(username='chat_user1', password='chat123')
        response = self.client.get(reverse('liveChat:operate_group'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'Group Basketball Game')

    def test_get_all_groups_as_admin(self):
        """Test admin can get all groups"""
        self.client.login(username='chat_admin', password='admin123')
        response = self.client.get(reverse('liveChat:operate_group'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('data', data)
        self.assertGreaterEqual(len(data['data']), 2)

    def test_get_specific_group_as_member(self):
        """Test getting specific group details as a member"""
        self.client.login(username='chat_user1', password='chat123')
        response = self.client.get(
            reverse('liveChat:operate_group', kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('data', data)
        self.assertEqual(data['data']['name'], 'Group Basketball Game')

    def test_get_specific_group_as_admin(self):
        """Test admin can get any group details"""
        self.client.login(username='chat_admin', password='admin123')
        response = self.client.get(
            reverse('liveChat:operate_group', kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('data', data)

    def test_patch_group_name(self):
        """Test updating group name"""
        self.client.login(username='chat_user1', password='chat123')
        response = self.client.patch(
            reverse('liveChat:operate_group', kwargs={'group_id': self.group1.id}),
            json.dumps({'name': 'Updated Basketball Group'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        self.group1.refresh_from_db()
        self.assertEqual(self.group1.name, 'Updated Basketball Group')

    def test_patch_group_empty_name(self):
        """Test updating group with empty name doesn't change it"""
        original_name = self.group1.name
        self.client.login(username='chat_user1', password='chat123')
        response = self.client.patch(
            reverse('liveChat:operate_group', kwargs={'group_id': self.group1.id}),
            json.dumps({'name': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        self.group1.refresh_from_db()
        self.assertEqual(self.group1.name, original_name)

    def test_delete_specific_group_as_admin(self):
        """Test admin can delete specific group"""
        self.client.login(username='chat_admin', password='admin123')
        group_id = self.group1.id
        response = self.client.delete(
            reverse('liveChat:operate_group', kwargs={'group_id': group_id})
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Group.objects.filter(id=group_id).exists())

    def test_delete_all_groups_as_admin(self):
        """Test admin can delete all groups"""
        self.client.login(username='chat_admin', password='admin123')
        response = self.client.delete(reverse('liveChat:operate_group'))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Group.objects.count(), 0)

    def test_delete_group_as_user_forbidden(self):
        """Test regular user cannot delete group"""
        self.client.login(username='chat_user1', password='chat123')
        group_id = self.group1.id
        response = self.client.delete(
            reverse('liveChat:operate_group', kwargs={'group_id': group_id})
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Group.objects.filter(id=group_id).exists())

    def test_group_404_not_found(self):
        """Test getting non-existent group returns 404"""
        self.client.login(username='chat_user1', password='chat123')
        fake_uuid = uuid.uuid4()
        response = self.client.get(
            reverse('liveChat:operate_group', kwargs={'group_id': fake_uuid})
        )
        self.assertEqual(response.status_code, 404)


class LiveChatMessageTestCase(TestCase):
    """Test cases for Chat operations in liveChat app"""
    
    def setUp(self):
        self.client = Client()
        
        self.user1 = CustomUser.objects.create_user(
            username='msg_user1',
            password='msg123',
            role='user',
            email='msg1@test.com'
        )
        self.user2 = CustomUser.objects.create_user(
            username='msg_user2',
            password='msg123',
            role='user',
            email='msg2@test.com'
        )
        self.admin = CustomUser.objects.create_user(
            username='msg_admin',
            password='admin123',
            role='admin',
            email='msgadmin@test.com'
        )

        self.category = SportCategory.objects.create(name='Futsal')
        self.match = Match.objects.create(
            title='Futsal Night',
            category=self.category,
            location='Indoor Arena',
            event_date=timezone.now() + timedelta(days=3),
            max_members=10
        )
        self.group = Group.objects.create(
            match=self.match,
            name='Group Futsal Night'
        )

        Participation.objects.create(match=self.match, user=self.user1, message='')

    def test_get_chats_empty_group(self):
        self.client.login(username='msg_user1', password='msg123')
        response = self.client.get(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 0)

    def test_get_chats_with_messages(self):
        Chat.objects.create(
            group_id=self.group,
            username=self.user1,
            message='Hello everyone!'
        )
        Chat.objects.create(
            group_id=self.group,
            username=self.user1,
            message='Looking forward to the game!'
        )
        
        self.client.login(username='msg_user1', password='msg123')
        response = self.client.get(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['data'][0]['username'], 'msg_user1')
        self.assertIn('profile_picture', data['data'][0])

    def test_post_chat_message(self):
        self.client.login(username='msg_user1', password='msg123')
        response = self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id}),
            json.dumps({'message': 'This is a test message'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        chat = Chat.objects.filter(
            group_id=self.group,
            username=self.user1.username,
            message='This is a test message'
        )
        self.assertTrue(chat.exists())

    def test_post_chat_invalid_data(self):
        self.client.login(username='msg_user1', password='msg123')
        response = self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id}),
            json.dumps({'message': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('errors', data)

    def test_unauthorized_user_cannot_get_chats(self):
        self.client.login(username='msg_user2', password='msg123')
        response = self.client.get(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        self.assertEqual(response.status_code, 401)

    def test_unauthorized_user_cannot_post_chat(self):
        self.client.login(username='msg_user2', password='msg123')
        response = self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id}),
            json.dumps({'message': 'Trying to post'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_admin_can_get_any_group_chats(self):
        Chat.objects.create(
            group_id=self.group,
            username=self.user1,
            message='Admin should see this'
        )
        
        self.client.login(username='msg_admin', password='admin123')
        response = self.client.get(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)

    def test_admin_can_post_to_any_group(self):
        self.client.login(username='msg_admin', password='admin123')
        response = self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id}),
            json.dumps({'message': 'Admin message'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_delete_all_chats_as_admin(self):
        Chat.objects.create(group_id=self.group, username=self.user1, message='Message 1')
        Chat.objects.create(group_id=self.group, username=self.user1, message='Message 2')
        Chat.objects.create(group_id=self.group, username=self.user1, message='Message 3')
        
        self.client.login(username='msg_admin', password='admin123')
        response = self.client.delete(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Chat.objects.filter(group_id=self.group).count(), 0)

    def test_delete_chats_as_user_forbidden(self):
        Chat.objects.create(group_id=self.group, username=self.user1, message='Test')
        
        self.client.login(username='msg_user1', password='msg123')
        response = self.client.delete(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Chat.objects.filter(group_id=self.group).exists())

    def test_chat_404_invalid_group(self):
        self.client.login(username='msg_user1', password='msg123')
        fake_uuid = uuid.uuid4()
        response = self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': fake_uuid}),
            json.dumps({'message': 'Test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_multiple_users_chatting(self):
        Participation.objects.create(match=self.match, user=self.user2, message='')

        self.client.login(username='msg_user1', password='msg123')
        self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id}),
            json.dumps({'message': 'Message from user1'}),
            content_type='application/json'
        )

        self.client.login(username='msg_user2', password='msg123')
        self.client.post(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id}),
            json.dumps({'message': 'Message from user2'}),
            content_type='application/json'
        )

        response = self.client.get(
            reverse('liveChat:operate_chat_by_group', kwargs={'group_id': self.group.id})
        )
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)
        usernames = [chat['username'] for chat in data['data']]
        self.assertIn('msg_user1', usernames)
        self.assertIn('msg_user2', usernames)