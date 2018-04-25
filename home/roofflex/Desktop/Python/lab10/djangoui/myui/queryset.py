# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import MultipleObjectsReturned
import requests
from django.http import HttpResponseRedirect, Http404
import copy

class MyApiRequests(object):
    def __init__(self, method, url, *args, **kwargs):
        self.request_method = method
        self.url = 'http://localhost:8000' + url
        self.args = args
        self.kwargs = kwargs

    def activate_user(self):
        self.request_method = "PUT"
        self.kwargs.update({'headers':{'authorization': 'Token c3742eb494b6f9847ec6dd28389838f2bd6a2c8c'}})
        response = requests.request(self.request_method, self.url, *self.args, **self.kwargs)
        return response.json()

    def create_user(self):
        self.request_method = "POST"
        self.url = 'http://localhost:8000/users/register/'
        response = requests.request(self.request_method, self.url, *self.args, **self.kwargs)
        return response.json()

    def delete_todolists(self):
        self.request_method = "DELETE"
        requests.request(self.request_method, self.url, *self.args, **self.kwargs)
        return "DELETED"

    def put_todolists(self):
        self.request_method = "PUT"
        response = requests.request(self.request_method, self.url, *self.args, **self.kwargs)
        return response.json()

    def post_todolists(self):
        self.request_method = "POST"
        response = requests.request(self.request_method, self.url,  *self.args, **self.kwargs)
        if response.status_code != 201:
            return False
        return response.json()

    def get_token(self):
        self.request_method = "POST"
        response = requests.request(self.request_method, 'http://localhost:8000/get-token/', *self.args, **self.kwargs)
        return response.json()

    def get_todolists(self):
        self.request_method = "GET"
        print(self.request_method, self.url,  self.args, self.kwargs)
        response = requests.request(self.request_method, self.url,  *self.args, **self.kwargs)
        if response.status_code != 200:
            return False
        return response.json()

    def get_users(self):
        self.request_method = "GET"
        response = requests.request(self.request_method, self.url, *self.args, **self.kwargs)
        return response.json()