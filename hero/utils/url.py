from requests import head
from re import compile, match, IGNORECASE


regex = compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', IGNORECASE)


def exists(url: str):
    if match(regex, url) is not None and head(url).status_code == 200:
        return True
    return False


def is_image(url: str):
    if exists(url):
        image_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif")
        if head(url).headers["content-type"] in image_formats:
            return True
    return False
