import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramcomSpider(scrapy.Spider):
    name = 'instagramcom'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = 'andrey_breakthroughchallenge'
    insta_password = '#PWD_INSTAGRAM_BROWSER:10:1617171488:AT5QAJPeicCmtethM0GdRHoL/8QOE3aSHenYB2IF+d0haBUZxJYlWBXH+/A4EOQJTlwGEEwCCrwVxEtJnvW2ua5EPXo9KifJAgON+E510dypwarm80PX8uHwoOrugQiYhYFXrPpyE4A/0VkcLg=='

    parse_users = ['luna_k.jp', 'syfoxb']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    hash_dict = {'followers_hash': 'c76146de99bb02f6415203be841dd25a', 'following_hash': 'd04b0a864b4b54837c0d870b0e77e076'}

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_password},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.followers_following_lists,
                    cb_kwargs={'username': user}
                )

    def followers_following_lists(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 24}
        for key, query_hash in self.hash_dict.items():
            link_to_parse = f'{self.graphql_url}query_hash={query_hash}&{urlencode(variables)}'
            yield response.follow(
                link_to_parse,
                callback=self.user_followers_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'target': deepcopy(key)}
            )

    def user_followers_following_parse(self, response: HtmlResponse, username, user_id, variables,
                                       target):
        j_data = json.loads(response.text)

        if target == 'followers_hash':
            target_j_data = j_data.get('data').get('user').get('edge_followed_by')
            friend_type = 'follower'
        elif target == 'following_hash':
            target_j_data = j_data.get('data').get('user').get('edge_follow')
            friend_type = 'following'
        print()
        page_info = target_j_data.get('page_info')
        if page_info.get('has_next_page'):
            variables = {'id': user_id,
                         'first': 24}
            variables['after'] = page_info['end_cursor']
            link_to_parse = f'{self.graphql_url}query_hash={self.hash_dict[target]}&{urlencode(variables)}'
            yield response.follow(
                link_to_parse,
                callback=self.user_followers_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'target': target}
            )

        friends = target_j_data.get('edges')
        for friend in friends:
            item = InstaparserItem(
                user_id=user_id,
                user_name=username,
                friend_type=friend_type,
                friend_id=friend['node']['id'],
                friend_username=friend['node']['username'],
                friend_full_name=friend['node']['full_name'],
                friend_photo=friend['node']['profile_pic_url'],
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
