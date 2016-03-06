# -*- coding: utf-8 -*-

# Copyright 2015 Donne Martin. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from __future__ import print_function
from __future__ import division

import mock
import os
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from hncli.hacker_news import HackerNews
from tests.data.comment import formatted_comment, formatted_heading, raw_comment
from tests.data.item import formatted_items
from tests.data.markdown import formatted_markdown, raw_markdown
from tests.data.regex import raw_text_for_regex
from tests.data.tip import formatted_tip
from tests.data.title import formatted_title, raw_title
from tests.data.url import formatted_url
from tests.mock_hacker_news_api import MockHackerNewsApi


class HackerNewsTest(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.hacker_news_api = MockHackerNewsApi()
        self.limit = len(self.hn.hacker_news_api.items)
        self.valid_id = 0
        self.invalid_id = 9000
        self.query = 'foo'

    def top(self, limit=2):
        self.hn.print_items(
            message=self.headlines_message(self.MSG_TOP),
            item_ids=self.hn.hacker_news_api.top_stories(limit))

    def test_config(self):
        expected = os.path.join(os.path.abspath(os.environ.get('HOME', '')),
                                self.hn.CONFIG)
        assert self.hn._config(self.hn.CONFIG) == expected

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    def test_ask(self, mock_print_items):
        self.hn.ask(self.limit)
        mock_print_items.assert_called_with(
            message=self.hn.headlines_message(self.hn.MSG_ASK),
            item_ids=self.hn.hacker_news_api.ask_stories(self.limit))

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    def test_best(self, mock_print_items):
        self.hn.best(self.limit)
        mock_print_items.assert_called_with(
            message=self.hn.headlines_message(self.hn.MSG_BEST),
            item_ids=self.hn.hacker_news_api.best_stories(self.limit))

    @mock.patch('hncli.hacker_news.HackerNews.save_cache')
    def test_clear_item_cache(self, mock_save_cache):
        item_ids = self.hn.load_cache(self.hn.CONFIG_IDS)
        self.hn.clear_item_cache()
        assert self.hn.item_ids == item_ids
        assert self.hn.item_cache == []
        mock_save_cache.assert_called_with()

    def test_format_markdown(self):
        result = self.hn.format_markdown(raw_markdown)
        assert result == formatted_markdown

    def test_headlines_message(self):
        message = 'foo'
        headlines_message = self.hn.headlines_message(message)
        assert message in headlines_message

    @mock.patch('hncli.hacker_news.HackerNews.print_comments')
    @mock.patch('hncli.hacker_news.HackerNews.print_item_not_found')
    def test_hiring_and_freelance(self,
                                  mock_print_item_not_found,
                                  mock_print_comments):
        self.hn.hiring_and_freelance(self.query, post_id=self.valid_id)
        item = self.hn.hacker_news_api.get_item(self.valid_id)
        mock_print_comments.assert_called_with(
            item, self.query, hide_no_match=True)
        self.hn.hiring_and_freelance(self.query, post_id=self.invalid_id)
        mock_print_item_not_found.assert_called_with(self.invalid_id)

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    def test_jobs(self, mock_print_items):
        self.hn.jobs(self.limit)
        mock_print_items.assert_called_with(
            message=self.hn.headlines_message(self.hn.MSG_JOBS),
            item_ids=self.hn.hacker_news_api.ask_stories(self.limit))

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    def test_new(self, mock_print_items):
        self.hn.new(self.limit)
        mock_print_items.assert_called_with(
            message=self.hn.headlines_message(self.hn.MSG_NEW),
            item_ids=self.hn.hacker_news_api.new_stories(self.limit))

    @mock.patch('hncli.hacker_news.HackerNews.format_index_title')
    @mock.patch('hncli.hacker_news.click')
    def test_onion(self, mock_click, mock_format_index_title):
        self.hn.onion(self.limit)
        assert len(mock_format_index_title.mock_calls) == self.limit
        assert mock_click.mock_calls

    def test_save_and_load_item_ids(self):
        self.hn.item_ids = [0, 1, 2]
        self.hn.item_cache = [3, 4, 5]
        self.hn.save_cache()
        item_ids = self.hn.load_cache(self.hn.CONFIG_IDS)
        assert item_ids == ['0', '1', '2']
        item_cache = self.hn.load_cache(self.hn.CONFIG_CACHE)
        assert item_cache == ['3', '4', '5']

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    def test_show(self, mock_print_items):
        self.hn.show(self.limit)
        mock_print_items.assert_called_with(
            message=self.hn.headlines_message(self.hn.MSG_SHOW),
            item_ids=self.hn.hacker_news_api.show_stories(self.limit))

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    def test_top(self, mock_print_items):
        self.hn.top(self.limit)
        mock_print_items.assert_called_with(
            message=self.hn.headlines_message(self.hn.MSG_TOP),
            item_ids=self.hn.hacker_news_api.top_stories(self.limit))

    @mock.patch('hncli.hacker_news.HackerNews.print_items')
    @mock.patch('hncli.hacker_news.click')
    @mock.patch('hncli.hacker_news.HackerNews.print_item_not_found')
    def test_user(self, mock_print_item_not_found,
                  mock_click, mock_print_items):
        user_id = 'foo'
        self.hn.user(user_id, self.limit)
        user = self.hn.hacker_news_api.get_user(user_id)
        mock_print_items.assert_called_with(
            self.hn.MSG_SUBMISSIONS, user.submitted[0:self.limit])
        assert mock_click.mock_calls
        self.hn.user(self.invalid_id, self.limit)
        mock_print_item_not_found.assert_called_with(self.invalid_id)

    @mock.patch('hncli.hacker_news.HackerNews.view')
    def test_view_setup_query_recent(self, mock_view):
        index = 0
        comments = False
        comments_recent = True
        comments_unseen = False
        comments_clear_cache = False
        browser = False
        self.hn.view_setup(
            index, self.query, comments, comments_recent,
            comments_unseen, comments_clear_cache, browser)
        comments_expected = True
        mock_view.assert_called_with(
            index, self.hn.QUERY_RECENT, comments_expected, browser)

    @mock.patch('hncli.hacker_news.HackerNews.view')
    def test_view_setup_query_unseen(self, mock_view):
        index = 0
        comments = False
        comments_recent = False
        comments_unseen = True
        comments_clear_cache = False
        browser = False
        self.hn.view_setup(
            index, self.query, comments, comments_recent,
            comments_unseen, comments_clear_cache, browser)
        comments_expected = True
        mock_view.assert_called_with(
            index, self.hn.QUERY_UNSEEN, comments_expected, browser)

    @mock.patch('hncli.hacker_news.HackerNews.view')
    @mock.patch('hncli.hacker_news.HackerNews.clear_item_cache')
    def test_view_comment_clear_cache(self, mock_clear_item_cache, mock_view):
        index = 0
        comments = False
        comments_recent = False
        comments_unseen = True
        comments_clear_cache = True
        browser = False
        self.hn.view_setup(
            index, self.query, comments, comments_recent,
            comments_unseen, comments_clear_cache, browser)
        comments_expected = True
        mock_clear_item_cache.assert_called_with()
        mock_view.assert_called_with(
            index, self.hn.QUERY_UNSEEN, comments_expected, browser)

    def test_format_comment(self):
        item = self.hn.hacker_news_api.get_item(self.valid_id)
        item.text = raw_comment
        heading, comment = self.hn.format_comment(
            item, depth=3, header_color='yellow', header_adornment='')
        assert heading == formatted_heading
        assert comment == formatted_comment

    def test_format_index_title(self):
        result = self.hn.format_index_title(
            index=1, title=raw_title)
        assert result == formatted_title

    def test_format_item(self):
        items = self.hn.hacker_news_api.items
        for index, item in enumerate(items):
            result = self.hn.format_item(items[index], index+1)
            assert result == formatted_items[index]

    @mock.patch('hncli.hacker_news.click.echo')
    def test_print_comments_unseen(self, mock_click_echo):
        items = self.hn.hacker_news_api.items
        self.hn.print_comments(items[0])
        mock_click_echo.assert_any_call(
            '\x1b[35m\nfoo - just now [!]\x1b[0m\n')
        mock_click_echo.assert_any_call(
            'text foo')
        mock_click_echo.assert_any_call(
            '\x1b[35m\n  bar - just now [!]\x1b[0m\n')
        mock_click_echo.assert_any_call(
            '  text bar')
        mock_click_echo.assert_any_call(
            '\x1b[35m\n    baz - just now [!]\x1b[0m\n')
        mock_click_echo.assert_any_call(
            '    text baz')

    @mock.patch('hncli.hacker_news.click.echo')
    def test_print_comments_regex(self, mock_click_echo):
        items = self.hn.hacker_news_api.items
        regex_query = 'foo'
        self.hn.print_comments(items[0], regex_query)
        mock_click_echo.assert_any_call(
            '\x1b[35m\nfoo - just now [!]\x1b[0m\n')
        mock_click_echo.assert_any_call(
            'text foo')
        mock_click_echo.assert_any_call(
            '\x1b[35m\n  bar - just now [!]\x1b[0m\n')
        mock_click_echo.assert_any_call(
            '  text bar [...]')
        mock_click_echo.assert_any_call(
            '\x1b[35m\n    baz - just now [!]\x1b[0m\n')
        mock_click_echo.assert_any_call(
            '    text baz [...]')

    @mock.patch('hncli.hacker_news.click.echo')
    def test_print_comments_regex_seen(self, mock_click_echo):
        items = self.hn.hacker_news_api.items
        item = items[2]
        regex_query = 'foo'
        self.hn.item_cache.append(str(item.item_id))
        self.hn.print_comments(item, regex_query)
        mock_click_echo.assert_any_call(
            '\x1b[33m\nbaz - just now\x1b[0m\n')
        mock_click_echo.assert_any_call(
            'text baz [...]')

    @mock.patch('hncli.hacker_news.click')
    def test_print_item_not_found(self, mock_click):
        self.hn.print_item_not_found(self.invalid_id)
        mock_click.secho.assert_called_with(
            self.hn.MSG_ITEM_NOT_FOUND.format(self.invalid_id), fg='red')

    @mock.patch('hncli.hacker_news.click')
    @mock.patch('hncli.hacker_news.HackerNews.format_item')
    def test_print_items(self, mock_format_item, mock_click):
        items = self.hn.hacker_news_api.items
        item_ids = [item.item_id for item in items]
        self.hn.print_items(self.hn.headlines_message(
            self.hn.MSG_TOP), item_ids)
        for index, item in enumerate(items):
            assert mock.call(item, index+1) in mock_format_item.mock_calls
        assert mock_click.secho.mock_calls

    def test_print_tip_view(self):
        result = self.hn.tip_view(max_index=10)
        assert result == formatted_tip

    @mock.patch('hncli.hacker_news.requests')
    def test_url_contents(self, mock_requests):
        self.hn.html_to_text = mock.Mock(handle=lambda _: 'bar')
        result = self.hn.url_contents('foo')
        mock_requests.get.assert_called_with('foo')
        assert result == formatted_url

    def test_match_comment_unseen(self):
        regex_query = ''
        header_adornment = ''
        match = self.hn.match_comment_unseen(regex_query, header_adornment)
        assert not match
        regex_query = self.hn.QUERY_UNSEEN
        header_adornment = self.hn.COMMENT_UNSEEN
        match = self.hn.match_comment_unseen(regex_query, header_adornment)
        assert match

    def test_match_regex(self):
        regex_query = '(?i)(Python|JavaScript).*(rockstar)'
        item = self.hn.hacker_news_api.get_item(self.valid_id)
        assert not self.hn.match_regex(item, regex_query)
        item.text = raw_text_for_regex
        assert self.hn.match_regex(item, regex_query)

    def test_match_regex_user(self):
        regex_query = 'bar'
        item = self.hn.hacker_news_api.get_item(self.valid_id)
        assert not self.hn.match_regex(item, regex_query)
        regex_query = 'fo'
        assert self.hn.match_regex(item, regex_query)

    def test_match_regex_item(self):
        regex_query = 'just now'
        item = self.hn.hacker_news_api.get_item(self.valid_id)
        assert self.hn.match_regex(item, regex_query)
        regex_query = 'minutes ago'
        assert not self.hn.match_regex(item, regex_query)

    @mock.patch('hncli.hacker_news.HackerNews.url_contents')
    @mock.patch('hncli.hacker_news.click')
    def test_view(self, mock_click, mock_url_contents):
        items = self.hn.hacker_news_api.items
        self.hn.item_ids = [int(item.item_id) for item in items]
        one_based_index = self.valid_id + 1
        comments_query = ''
        comments = False
        browser = False
        self.hn.view(one_based_index, comments_query, comments, browser)
        mock_url_contents.assert_called_with(
            items[self.valid_id].url)
        assert mock_click.secho.mock_calls
        assert mock_click.echo_via_pager.mock_calls

    @mock.patch('hncli.hacker_news.HackerNews.print_comments')
    @mock.patch('hncli.hacker_news.click')
    def test_view_comments(self, mock_click, mock_print_comments):
        items = self.hn.hacker_news_api.items
        self.hn.item_ids = [int(item.item_id) for item in items]
        one_based_index = self.valid_id + 1
        comments_query = 'foo'
        comments = True
        browser = False
        self.hn.view(one_based_index, comments_query, comments, browser)
        mock_print_comments.assert_called_with(
            items[self.valid_id], regex_query=comments_query)
        assert mock_click.mock_calls

    @mock.patch('hncli.hacker_news.HackerNews.print_comments')
    @mock.patch('hncli.hacker_news.click')
    def test_view_no_url(self, mock_click, mock_print_comments):
        self.hn.hacker_news_api.items[0].url = None
        items = self.hn.hacker_news_api.items
        self.hn.item_ids = [int(item.item_id) for item in items]
        one_based_index = self.valid_id + 1
        comments_query = 'foo'
        comments = False
        browser = False
        self.hn.view(one_based_index, comments_query, comments, browser)
        mock_print_comments.assert_called_with(
            items[self.valid_id], regex_query=comments_query)
        assert mock_click.mock_calls

    @mock.patch('hncli.hacker_news.webbrowser')
    @mock.patch('hncli.hacker_news.click')
    def test_view_browser_url(self, mock_click, mock_webbrowser):
        items = self.hn.hacker_news_api.items
        self.hn.item_ids = [int(item.item_id) for item in items]
        one_based_index = self.valid_id + 1
        comments_query = 'foo'
        comments = False
        browser = True
        self.hn.view(one_based_index, comments_query, comments, browser)
        mock_webbrowser.open.assert_called_with(items[self.valid_id].url)
        assert mock_click.mock_calls

    @mock.patch('hncli.hacker_news.webbrowser')
    @mock.patch('hncli.hacker_news.click')
    def test_view_browser_comments(self, mock_click, mock_webbrowser):
        items = self.hn.hacker_news_api.items
        self.hn.item_ids = [int(item.item_id) for item in items]
        one_based_index = self.valid_id + 1
        comments_query = 'foo'
        comments = True
        browser = True
        self.hn.view(one_based_index, comments_query, comments, browser)
        item = items[self.valid_id]
        comments_url = self.hn.URL_POST + str(item.item_id)
        mock_webbrowser.open.assert_called_with(comments_url)
        assert mock_click.mock_calls
