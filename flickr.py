import requests
from xml.etree import ElementTree

url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&tags=trump,donald&api_key=6b32be403aae5c0a5765e7677385d4e0&media=photos&content_type=1&safe_search=1&tag_mode=AND'

response = requests.get(url)

photos = ElementTree.fromstring(response.content)

images_list = []
count = 0

for photo in photos.iter():
    farm = photo.get('farm')
    server = photo.get('server')
    photo_id = photo.get('id')
    secret = photo.get('secret')
    image_link = 'https://farm%s.staticflickr.com/%s/%s_%s.jpg' % (farm,server,photo_id,secret)
    images_list.append(image_link)
    count += 1
    if count > 4:
        break
    
print images_list
