import json

from django.test import TestCase
from django.test import Client
from django.conf import settings

from .models import TestModel


class ApiTestCase(TestCase):
    list_url = '/api/test/1.0/'

    def setUp(self):
        self.client = Client()
        self.createObjects(100)

    def createObjects(self, n):
        for i in range(n):
            TestModel.objects.create(title='title_{0}'.format(i), text='text_{0}'.format(i))

    def clearObjects(self):
        TestModel.objects.delete()

    def test_getList(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response['objects']), settings.XREST_DEFAULT_LIST_LIMIT)

    def test_postList(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        overall = response['meta']['overall_count']
        response_post = self.client.post(self.list_url, json.dumps({'title': 'c0', 'text': 'c1'}), content_type='application/json')
        self.assertEqual(response_post.status_code, 200)

        response_after = self.client.get(self.list_url)
        self.assertEqual(response_after.status_code, 200)
        response_after = response_after.json()
        overall_after = response_after['meta']['overall_count']

        self.assertEqual(overall+1, overall_after)

    def test_getObject(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        item = response['objects'][0]

        response_item = self.client.get(self.list_url+str(item['pk'])+'/')
        self.assertEqual(response_item.status_code, 200)
        response_item = response_item.json()['object']
        self.assertEqual(item['pk'], response_item['pk'])
        self.assertEqual(item['title'], response_item['title'])
        self.assertEqual(item['text'], response_item['text'])

    def test_postObject(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        item = response['objects'][0]
        response_post_item = self.client.post(self.list_url+str(item['pk'])+'/',
                                              json.dumps({'title': 'new_title', 'text': 'new_text'}),
                                              content_type='application/json')
        self.assertEqual(response_post_item.status_code, 200)

        response_item = self.client.get(self.list_url+str(item['pk'])+'/')
        self.assertEqual(response_item.status_code, 200)
        response_item = response_item.json()['object']
        self.assertEqual(response_item['title'], item['title'])
        self.assertEqual(response_item['text'], 'new_text')

    def test_deleteObject(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        item = response['objects'][0]
        response_item = self.client.get(self.list_url+str(item['pk'])+'/')
        self.assertEqual(response_item.status_code, 200)

        response_item = self.client.delete(self.list_url+str(item['pk'])+'/')
        self.assertEqual(response_item.status_code, 200)

        response_item = self.client.get(self.list_url+str(item['pk'])+'/')
        self.assertEqual(response_item.status_code, 404)