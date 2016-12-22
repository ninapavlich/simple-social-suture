import re
import collections
import datetime
from random import shuffle
from twython import Twython
from instagram.client import InstagramAPI
from ttp import ttp
import urllib, json







#==========================================
# PUBLIC ==================================
#==========================================
def get_message_by_id(settings, message_id):
    
    is_twitter = "tweet_" in message_id
    is_instagram = "instagram_" in message_id

    message = {}
    if is_twitter:
        tweet_id = message_id[6:]
        twitter = _get_twitter_api()
        tweet = twitter.show_status(id=tweet_id)
        message = _format_twitter_message(tweet)

    elif is_instagram:
        instagram_id = message_id[10:]

        instagram = _get_instagram_api()
        message_object = instagram.media(instagram_id)
        # url = 'https://api.instagram.com/v1/media/%s?client_id=%s'%(instagram_id, settings.INSTAGRAM_CLIENT_ID)
        # response = urllib.urlopen(url)
        # data = json.loads(response.read())
        message = _format_instagram_message(message_object)

    return message

def get_messages_by_hashtag(settings, hashtag_search):
    
    output = []

    end_date = _add_years(datetime.datetime.now(), -1)
    
    instagram_messages = _search_instagram_joined(settings, [hashtag_search], end_date)
    
    twitter_messages = _search_twitter_joined(settings, [hashtag_search], end_date)
    
    output = instagram_messages + twitter_messages
    output = sorted(output, key=lambda p: p['message_date'], reverse=True)

    return output

def get_messages_by_user(settings, twitter_user_name, instagram_user_name):
    
    output = []

    end_date = _add_years(datetime.datetime.now(), -1)

    instagram_messages = [] if not instagram_user_name else _get_instagram_posts_for_username(settings, instagram_user_name, end_date)
    twitter_messages = [] if not twitter_user_name else _get_twitter_posts_for_username(settings, twitter_user_name)
    
    output = instagram_messages + twitter_messages
    output = sorted(output, key=lambda p: p['message_date'], reverse=True)

    return output

def get_my_messages(settings, twitter_user_name, instagram_user_name):
    
    output = []

    end_date = _add_years(datetime.datetime.now(), -1)

    instagram_messages = [] if not instagram_user_name else _get_my_instagram_feed(settings, end_date)
    twitter_messages = [] if not twitter_user_name else _get_twitter_posts_for_username(settings, twitter_user_name)
    
    output = instagram_messages + twitter_messages
    output = sorted(output, key=lambda p: p['message_date'], reverse=True)

    return output    

#==========================================
# PRIVATE =================================
#==========================================

def _get_twitter_api(settings):
    return Twython(app_key=settings.TWITTER_APP_KEY, 
        app_secret=settings.TWITTER_APP_KEY_SECRET, 
        oauth_token=settings.TWITTER_ACCESS_TOKEN, 
        oauth_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET)


def _get_instagram_api(settings):
    return InstagramAPI(client_id=settings.INSTAGRAM_CLIENT_ID, client_secret=settings.INSTAGRAM_SECRET_CLIENT_ID)





def _search_twitter_joined(settings, searches, end_date, max_id=None, current_count=0):
    #Join multiple searches together to get desired max count
    
    statuses, next_max_id, last_message_end_date = _search_twitter_parsed(settings, searches, max_id)

    if len(statuses) == 0:
        return statuses

    total_length = current_count + len(statuses)

    # print 'found %s so far. the last message in this list was at %s shooting for %s next_max_id: %s'%(total_length, last_message_end_date, end_date, next_max_id)

    if(total_length < settings.MAX_QUERY_COUNT and last_message_end_date > end_date and next_max_id != None):
        statuses += _search_twitter_joined(settings, searches, end_date, next_max_id, total_length)

    return statuses


def _search_twitter_parsed(settings, searches, max_id=None):
    #Handles parsing raw data into unified format

    search = searches[0]
    search_results = _search_twitter(settings, search, settings.MAX_TWITTER_COUNT, max_id)
        
    
    try:
        next_results_url_params = search_results['search_metadata']['next_results']
        next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
    except:
        next_max_id = None

    raw_statuses = search_results['statuses'] 
    if len(raw_statuses) == 0:
        return ([], None, None)

    statuses = []
    for message in raw_statuses:
        statuses.append(_format_twitter_message(message, True))

    last_status = statuses[len(statuses)-1]
    last_message_date = last_status['message_date']


    if not search_results:
        return []

    return (statuses, next_max_id, last_message_date)


def _search_twitter(settings, search, max_count, max_id=None):
    try:
        twitter = _get_twitter_api(settings)
        if max_id:
            results = twitter.search(q=search, count=max_count, result_type='realtime', max_id=max_id)
        else:
            results = twitter.search(q=search, count=max_count, result_type='realtime')
        return results
    except:
        return None

def _get_twitter_posts_for_username(settings, username):

    username = username.replace("@","")        

    twitter = _get_twitter_api(settings)
    user_timeline = twitter.get_user_timeline(screen_name=username)

    # print user_timeline
    statuses = []
    for message in user_timeline:
        statuses.append(_format_twitter_message(message, True))

    return statuses


def _search_instagram_joined(settings, searches, end_date, max_id=None, current_count=0):
    #Join multiple searches together to get desired max count
    
    statuses, next_max_id, last_message_end_date = _search_instagram_parsed(settings, searches, max_id)

    total_length = current_count + len(statuses)

    # print 'found %s so far. the last message in this list was at %s shooting for %s next_max_id: %s'%(total_length, last_message_end_date, end_date, next_max_id)

    if(total_length < settings.MAX_QUERY_COUNT and last_message_end_date > end_date and next_max_id != None):
        statuses += _search_instagram_joined(settings, searches, end_date, next_max_id, total_length)

    return statuses


def _search_instagram_parsed(settings, searches, max_id):


    search = searches[0]
    search_results = _search_instagram(settings, search, max_id)

    if not search_results:
        return []

    if len(searches)>1:
        subsearch = searches[1].replace("#","")
        output = []

        for message in search_results['data']:
            for tag in message['tags']:
                if tag.lower() == subsearch.lower():
                    output.append(message)

    else:
        if 'data' in search_results:
            output = search_results['data']
        else:
            output = []

    statuses = []
    for message in output:
        statuses.append(_format_instagram_message(message, True))

    try:
        next_max_id = search_results['pagination']['next_max_tag_id']
    except:
        next_max_id = None

    last_status = statuses[len(statuses)-1]
    last_message_date = last_status['message_date']

    return (statuses, next_max_id, last_message_date)


def _search_instagram(settings, search, max_count, offset=None):
    try:
        instagram = _get_instagram_api()

        messages = instagram.tag_recent_media(max_count=max_count,tag_name=search_term)
        return messages


        # search_term = search.replace("#","")
        # url = "https://api.instagram.com/v1/tags/%s/media/recent?client_id=%s"%(
        #     search_term, settings.INSTAGRAM_CLIENT_ID
        # )
        # #TODO: Max count or max id...
        # try:
        #     response = urllib.urlopen(url)
        #     data = json.loads(response.read())
        #     return data
        # except:
        #     return None
    except:
        return None


def _get_instagram_posts_for_username(settings, username, end_date):

    
    username = username.replace("@","") 
    # search_url = "https://api.instagram.com/v1/users/search?q=%s&client_id=%s"%(
    #     username, settings.INSTAGRAM_CLIENT_ID
    # )
    # print search_url
    instagram = _get_instagram_api(settings)
    
    instagram_users = instagram.user_search(username)
    if len(instagram_users)>0:
        user = instagram_users[0]
        return _get_instagram_posts_for_userid_joined(settings, user.id, end_date)
    else:
        return []

def _get_my_instagram_feed(settings, end_date):

    return _get_my_instagram_posts_joined(settings, end_date)
    


def _get_instagram_posts_for_userid_joined(settings, user_id, end_date, max_id=None, current_count=0):
    #Join multiple searches together to get desired max count

    statuses, next_max_id, last_message_end_date = _get_instagram_posts_for_userid_parsed(settings, user_id, max_id)

    total_length = current_count + len(statuses)

    # print 'found %s so far. the last message in this list was at %s shooting for %s next_max_id: %s'%(total_length, last_message_end_date, end_date, next_max_id)

    if(total_length < settings.MAX_QUERY_COUNT and last_message_end_date > end_date and next_max_id != None):
        statuses += _get_instagram_posts_for_userid_joined(settings, user_id, end_date, next_max_id, total_length)

    return statuses


def _get_instagram_posts_for_userid_parsed(settings, user_id, max_id):

    posts, next_max_id = _get_instagram_posts_for_userid(settings, user_id, max_id)

    statuses = []
    for post in posts:
        statuses.append(_format_instagram_message(post, True))

    last_status = statuses[len(statuses)-1]
    last_message_date = last_status['message_date']

    return (statuses, next_max_id, last_message_date)


def _get_instagram_posts_for_userid(settings, user_id, max_id = None):
    
    instagram = _get_instagram_api(settings)
    posts, next_max_id = instagram.user_recent_media(user_id=user_id, max_id=max_id)
    
    return (posts, next_max_id)



####

def _get_my_instagram_posts_joined(settings, end_date, max_id=None, current_count=0):
    #Join multiple searches together to get desired max count

    statuses, next_max_id, last_message_end_date = _get_my_instagram_posts_parsed(settings, max_id)

    total_length = current_count + len(statuses)

    # print 'found %s so far. the last message in this list was at %s shooting for %s next_max_id: %s'%(total_length, last_message_end_date, end_date, next_max_id)

    if(total_length < settings.MAX_QUERY_COUNT and last_message_end_date > end_date and next_max_id != None):
        statuses += _get_my_instagram_posts_joined(settings, end_date, next_max_id, total_length)

    return statuses


def _get_my_instagram_posts_parsed(settings, max_id):

    posts, next_max_id = _get_my_instagram_posts(settings, max_id)
    
    statuses = []
    for post in posts:
        statuses.append(_format_instagram_message_dict(post, True))

    last_status = statuses[len(statuses)-1]
    last_message_date = last_status['message_date']

    return (statuses, next_max_id, last_message_date)


def _get_my_instagram_posts(settings,max_id = None):
    
    # instagram = _get_instagram_api(settings)
    # posts, next_max_id = instagram.user_media_feed(max_id=max_id)
    
    url = 'https://api.instagram.com/v1/users/self/media/recent?access_token=%s&max_id=%s'%(settings.INSTAGRAM_ACCESS_TOKEN, max_id)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    
    posts = data['data']
    try:
        next_max_id = data['pagination']['next_max_tag_id']
    except:
        next_max_id = None

    return (posts, next_max_id)    



def _format_instagram_message_dict(instagram, full=True):
    # print instagram
    message_id = 'instagram_%s'%(instagram['id'])
    message_date = datetime.datetime.fromtimestamp(int(instagram['created_time']))

    if not full:
        return {
            'message_id':message_id,
            'message_date':message_date
        }

    # print instagram

    parser = ttp.Parser()    
    try:
        caption = _cleanhtml(instagram['caption']['text'])
    except:
        caption = ''
    parsed = parser.parse(caption)

    message_url = instagram['link']
    instagram_url = (instagram['images']['standard_resolution']['url']).replace("http://", 'https://')
    text = "<figure><a href='%s'><img src='%s' alt='%s'></a>\
        <figcaption>%s</figcaption></figure>"%(message_url, instagram_url, \
        caption, _process_message_html(parsed.html))


    message = {
        'message_id':message_id,
        'message_date':message_date,
        'message_timesince':_timesince(message_date),
        'user_name':instagram['user']['full_name'],
        'user_screen_name':instagram['user']['username'],
        'user_avatar_url':instagram['user']['profile_picture'],
        'user_profile_url':'https://instagram.com/%s'%instagram['user']['username'],
        'message_url':message_url,
        'message_html':text,
        'hashes':[hashtag.lower() for hashtag in instagram['tags']],
        'raw_data':instagram
    }
    return message

def _format_instagram_message(instagram, full=True):
    # print instagram
    message_id = 'instagram_%s'%(instagram.id)
    message_date = instagram.created_time#datetime.datetime.fromtimestamp(int(instagram.created_time))

    if not full:
        return {
            'message_id':message_id,
            'message_date':message_date
        }

    """
    {'caption': Comment: inertiaunlimited said "What's better than going down a water slide in the Bahamas? Capturing the fun in high-speed, of course. #atlantisresort #xmo #sportstech",
 'comment_count': 1,
 'comments': [Comment: atlantisresort said "Amazing!"],
 'created_time': datetime.datetime(2015, 12, 7, 13, 33, 4),
 'filter': 'Normal',
 'id': '1134770313898096730_2142750893',
 'images': {'low_resolution': Image: https://scontent.cdninstagram.com/hphotos-xpf1/t51.2885-15/s320x320/e35/12277430_1682421975377994_535438069_n.jpg,
            'standard_resolution': Image: https://scontent.cdninstagram.com/hphotos-xpf1/t51.2885-15/s640x640/sh0.08/e35/12277430_1682421975377994_535438069_n.jpg,
            'thumbnail': Image: https://scontent.cdninstagram.com/hphotos-xpf1/t51.2885-15/s150x150/e35/12277430_1682421975377994_535438069_n.jpg},
 'like_count': 1,
 'likes': [User: itsofficialjojo],
 'link': 'https://www.instagram.com/p/-_g5aVjfha/',
 'location': Location: 145849377 (Point: (25.084288198, -77.321467938)),
 'tags': [Tag: xmo, Tag: sportstech, Tag: atlantisresort],
 'type': 'image',
 'user': User: inertiaunlimited,
 'users_in_photo': []}
    """

    parser = ttp.Parser()    
    try:
        caption = _cleanhtml(instagram.caption.text)
    except:
        caption = ''
    parsed = parser.parse(caption)

    message_url = instagram.link
    instagram_url = (instagram.get_standard_resolution_url()).replace("http://", 'https://')
    text = "<figure><a href='%s'><img src='%s' alt='%s'></a>\
        <figcaption>%s</figcaption></figure>"%(message_url, instagram_url, \
        caption, _process_message_html(parsed.html))
    
    message = {
        'message_id':message_id,
        'message_date':message_date,
        'message_timesince':_timesince(message_date),
        'user_name':instagram.user.full_name,
        'user_screen_name':instagram.user.username,
        'user_avatar_url':instagram.user.profile_picture,
        'user_profile_url':'https://instagram.com/%s'%instagram.user.username,
        'message_url':message_url,
        'message_html':text,
        'hashes':[hashtag.name.lower() for hashtag in instagram.tags],
        'raw_data':instagram
    }
    return message


def _format_twitter_message(tweet, full=True):
    # print tweet
    message_id = 'tweet_%s'%(tweet['id'])
    message_date = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

    if not full:
        return {
            'message_id':message_id,
            'message_date':message_date
        }

    parser = ttp.Parser()
    parsed = parser.parse(tweet['text'])
    message_url = 'https://twitter.com/%s/status/%s'%(tweet['user']['screen_name'], tweet['id'])
    
    if tweet['entities'].has_key('media'):
        text = "<figure><a href='%s'><img src='%s:large' alt='%s'></a>\
            <figcaption>%s</figcaption></figure>"%(message_url, tweet['entities']['media'][0]['media_url_https'], \
            _cleanhtml(parsed.html), _process_message_html(parsed.html))
    else:
        text = _process_message_html(parsed.html)

    return {
        'message_id':message_id,
        'message_date':message_date,
        'message_timesince':_timesince(message_date),
        'user_name':tweet['user']['screen_name'],
        'user_screen_name':tweet['user']['screen_name'],
        'user_avatar_url':tweet['user']['profile_image_url_https'],
        'user_profile_url':'https://twitter.com/%s'%tweet['user']['screen_name'],
        'message_url':message_url,
        'message_html':text,
        'hashes':[hashtag['text'].lower() for hashtag in tweet['entities']['hashtags']],
        'raw_data':tweet
    }

   

def _process_message_html(parsed_html):
    # parsed_html = parsed_html.replace('https://twitter.com/search', '')
    # parsed_html = parsed_html.replace('%23', '')
    return parsed_html




def _cleanhtml(raw_html):
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr,'', raw_html)
    return cleantext


TIMEZONE_OFFSET = 0

def _timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """

    
    now = datetime.datetime.utcnow() - datetime.timedelta(hours=TIMEZONE_OFFSET)
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default

def _timesince_detailed(dt):

    now = datetime.datetime.utcnow() - datetime.timedelta(hours=TIMEZONE_OFFSET)
    diff = now - dt
    if diff.total_seconds() < 60:
        return '%s seconds ago'%(diff.total_seconds())
    elif diff.total_seconds() < 60*60:
        return '%s minutes ago'%(int(diff.total_seconds()/60))
    else:
        return '%s hours ago'%(int(diff.total_seconds()/(60*60)))
    # elif diff.total_seconds() < 60*60*24:
    #     return '%s hours ago'%(int(diff.total_seconds()/(60*60)))
    # elif diff.total_seconds() < 60*60*24*7:
    #     return '%s days ago'%(int(diff.total_seconds()/(60*60*24)))
    # elif diff.total_seconds() < 60*60*24*30:
    #     return '%s weeks ago'%(int(diff.total_seconds()/(60*60*24*7)))
    # elif diff.total_seconds() < 60*60*24*365:
    #     return '%s months ago'%(int(diff.total_seconds()/(60*60*24*30)))
    # else:
    #     return '%s years ago'%(int(diff.total_seconds()/(60*60*365)))


def _add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))    