#!/usr/bin/python

import os, sys, ConfigParser, json

from lib.service import YoutubeUtils
from lib.service.FeedlyUtils import FeedlyAPI as Feedly
from lib.utils import OSXUtils

APP_NAME = os.path.splitext(os.path.basename(__file__))[0] #'Tubely'

FEEDLY_RSS_FOLDER = 'YouTube'

def filterSubscriptions(feedly_folder, feedly_items, youtube_items):
	to_del = []
	to_add = []

	checked    = []
	categories = []
	for item in feedly_items:
		for cat in item['categories']:
			if cat['label'].lower() == feedly_folder.lower(): # look only for YouTube category, not case sensitive
				if len(categories) == 0:
					categories = [cat]
				j = 0
				while j < len(youtube_items):
					if item['id'] == youtube_items[j]['id']:
						checked.append(j)
						break
					j += 1

				if j == len(youtube_items):
					to_del.append(item)
				break
	checked = list(set(checked))
	only_youtube = [i for j, i in enumerate(youtube_items) if j not in checked] # remove same elements
	for item in only_youtube:
		item.update({'categories': categories})
		to_add.append(item)

	return [to_del, to_add]

if __name__ == "__main__":
	#workdir = os.path.dirname(os.path.abspath(__file__))

	args = YoutubeUtils.argparser.parse_args()

	cfg = ConfigParser.RawConfigParser()
	cfg.read(os.path.expanduser("~") + os.sep + '.' + APP_NAME + '.cfg')

	filepref               = os.path.expanduser("~") + os.sep + '.' + APP_NAME
	youtube_client_secrets = filepref + '-youtube.json'
	youtube_storage_path   = filepref + '-youtube-oauth2.json'

	try:
		youtube_channel_id  = cfg.get(APP_NAME, 'youtube_channel_id')
		feedly_access_token = cfg.get(APP_NAME, 'feedly_access_token')
		if not os.path.isfile(youtube_client_secrets):
			raise Exception('Google settings')
	except Exception as e:
		print('[-] {0}'.format(e), file=sys.stderr)
		OSXUtils.notify(APP_NAME, 'error', 'unable to to read config')
		sys.exit(-1)

	try:
		youtube = YoutubeUtils.YoutubeAPI(args, youtube_client_secrets, youtube_storage_path)
		y_items = youtube.getSubscriptions(youtube_channel_id)
		if len(y_items) == 0:
			print('[-] unable to get YouTube subscriptions', file=sys.stderr)
			OSXUtils.notify(APP_NAME, 'error', 'unable to get YouTube subscriptions')
			sys.exit(-1)
		#if len(y_items) > feedly.rss_max_count:
		#	print >> sys.stderr, '[-] YouTube subscriptions number more than Feedly limit'
		#	print('[-] YouTube subscriptions number more than Feedly limit', file=sys.stderr)
		#	OSXUtils.notify(APP_NAME, 'error', 'YouTube subscriptions number more than Feedly limit')
		#	sys.exit(-1)
	except Exception as e:
		print('[-] {0}'.format(e), file=sys.stderr)
		OSXUtils.notify(APP_NAME, 'error', 'unable to get YouTube subscriptions')
		sys.exit(-1)

	try:
		feedly = Feedly(feedly_access_token)
		f_items = feedly.getSubscriptions()
		if len(f_items) == 0:
			print('[-] unable to get feedly subscriptions', file=sys.stderr)
			OSXUtils.notify(APP_NAME, 'error', 'unable to get feedly subscriptions')
			sys.exit(-1)
		f_res = filterSubscriptions(FEEDLY_RSS_FOLDER, f_items, y_items)
		if len(f_items) - len(f_res[0]) + len(f_res[1]) > feedly.rss_max_count:
			print('[-] subscriptions number more than Feedly limit', file=sys.stderr)
			OSXUtils.notify(APP_NAME, 'error', 'subscriptions number more than Feedly limit')
			sys.exit(-1)
	except Exception as e:
		print('[-] {0}'.format(e), file=sys.stderr)
		OSXUtils.notify(APP_NAME, 'error', 'unable to get Feedly subscriptions, try to refresh Feedly access token')
		sys.exit(-1)

	not_good = False
	try:
		if len(f_res[0]) > 0:
			print('[!] something to unsubscribe')
			if not feedly.unsubscribe(f_res[0]):
				not_good = True
				print('[-] unable to unsubscribe')
		else:
			print('[!] nothing to unsubscribe')
		if len(f_res[1]) > 0:
			print('[!] something to subscribe')
			if not feedly.subscribe(f_res[1]):
				not_good = True
				print('[-] unable to subscribe to something')
		else:
			print('[!] nothing to subscribe')
		if not_good:
			print('[!] something is wrong')
			OSXUtils.notify(APP_NAME, 'message', 'something is wrong')
		else:
			print('[+] synchronized')
			OSXUtils.notify(APP_NAME, 'success', 'synchronized')
	except Exception as e:
		print('[-] {0}'.format(e), file=sys.stderr)
		OSXUtils.notify(APP_NAME, 'error', 'unable to sync')
		sys.exit(-1)	

	if not_good:
		print('[-] not good', file=sys.stderr)
		sys.exit(-1)

	sys.exit(0)