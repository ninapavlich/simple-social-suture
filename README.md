simple_social_suture


Usage:
	
	from simple_social_suture.api import get_messages_by_hashtag    
	
    settings = {
    	'TWITTER_APP_KEY' : 'XXXXXXXXXX',
		'TWITTER_APP_KEY_SECRET' : 'XXXXXXXXXX',
		'TWITTER_ACCESS_TOKEN' : 'XXXXXXXXXX',
		'TWITTER_ACCESS_TOKEN_SECRET' : 'XXXXXXXXXX',
		'INSTAGRAM_CLIENT_ID' : 'XXXXXXXXXX',
		'INSTAGRAM_SECRET_CLIENT_ID' : 'XXXXXXXXXX',
		'MAX_TWITTER_COUNT' : 100,
		'MAX_QUERY_COUNT' : 200
    }
    messages = get_messages_by_hashtag(settings, "#helloworld")
    