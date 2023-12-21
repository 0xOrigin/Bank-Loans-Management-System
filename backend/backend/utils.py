

def get_attr_in_lang(obj, request, attr_ar, attr_en) -> str:
    try:
        return getattr(obj, attr_ar) if request.headers.get('Accept-Language', 'en') == 'ar' else getattr(obj, attr_en)
    except AttributeError:
        return ''
