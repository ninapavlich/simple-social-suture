#simple_social_suture

This library provides a unified JSON structure for Twitter, Instagram and Vimeo


##Usage:
	

	from simple_social_suture.api import get_my_messages    
	
    settings = {
    	'TWITTER_APP_KEY' : 'XXXXXXXXXX',
		'TWITTER_APP_KEY_SECRET' : 'XXXXXXXXXX',
		'TWITTER_ACCESS_TOKEN' : 'XXXXXXXXXX',
		'TWITTER_ACCESS_TOKEN_SECRET' : 'XXXXXXXXXX',
		'INSTAGRAM_USER_NAME' : 'XXXXXXXXXX',
		'INSTAGRAM_CLIENT_ID' : 'XXXXXXXXXX',
		'INSTAGRAM_SECRET_CLIENT_ID' : 'XXXXXXXXXX',
		'INSTAGRAM_ACCESS_TOKEN' : 'XXXXXXXXXX',
		'VIMEO_USER_NAME' : 'XXXXXXXXXX',
		'VIMEO_CLIENT_ID' : 'XXXXXXXXXX',
		'VIMEO_SECRET_CLIENT_ID' : 'XXXXXXXXXX',
		'MAX_TWITTER_COUNT' : 100,
		'MAX_QUERY_COUNT' : 200
    }

    messages = get_my_messages(settings, "@twitter_username", "@instagram_username", "vimeo_username")
    
    print messages

    #Example schema output
    [
	    {
		    'message_date': datetime.datetime(2017, 5, 4, 14, 11, 37),
		    'message_timesince': '3 days ago',
		    'hashes': [],
		    'id': XXXXXXXXXX,
		    'user_profile_url': u'https: //twitter.com/XXXXXXXXXX',
		    'message_html': u'XXXXXXXXXX',
		    'raw_data': {... this is the json returned from Twitter API ...},
		    'user_screen_name': u'XXXXXXXXXX',
		    'user_avatar_url': u'https: //pbs.twimg.com/profile_images/XXXXXXXXXX/XXXXXXXXXX.jpg',
		    'message_url': u'https: //twitter.com/XXXXXXXXXX/status/XXXXXXXXXX',
		    'user_name': u'XXXXXXXXXX',
		    'message_id': 'tweet_XXXXXXXXXX'
		},
	    {
	    'message_date': datetime.datetime(2017, 5, 1, 10, 0, 19),
		    'message_timesince': '6 days ago',
		    'hashes': [
		        u'XXXXXXXXXX',
		        u'XXXXXXXXXX',
		        u'XXXXXXXXXX'
		    ],
		    'id': XXXXXXXXXX,
		    'user_profile_url': u'https: //instagram.com/XXXXXXXXXX',
		    'message_html': u"XXXXXXXXXX",
		    'raw_data': {... this is the json returned from Instagram API ...},
		    'user_screen_name': u'XXXXXXXXXX',
		    'user_avatar_url': u'https: //scontent.cdninstagram.com/XXXXXXXXXX/XXXXXXXXXX.jpg',
		    'message_url': u'https: //www.instagram.com/p/XXXXXXXXXX/',
		    'user_name': u'XXXXXXXXXX',
		    'message_id': u'instagram_XXXXXXXXXX'
		},
	    {
		    'message_date': datetime.datetime(2016,8, 15, 18,30,55),
		    'message_timesince': '8 months ago',
		    'hashes': [],
		    'id': 'XXXXXXXXXX',
		    'user_profile_url': u'https: //vimeo.com/XXXXXXXXXX',
		    'message_html': u'<iframesrc="https://player.vimeo.com/video/XXXXXXXXXX?badge=0&autopause=0&player_id=0" width="640" height="360" frameborder="0" title="XXXXXXXXXX" ></iframe>',
		    'raw_data': {... this is the json returned from Vimeo API ...},
		    'user_screen_name': 'XXXXXXXXXX',
		    'user_avatar_url': u'https: //i.vimeocdn.com/portrait/XXXXXXXXXX?r=pad',
		    'message_url': u'https: //vimeo.com/XXXXXXXXXX',
		    'user_name': u'XXXXXXXXXX',
		    'message_id': 'vimeo_XXXXXXXXXX'
		}
	]
