import requests


class HTTP:
    @staticmethod
    def get(url, return_json=True):
        r = requests.get(url) ##获得的是response对象
        if r.status_code == 200:
            if return_json:
                return r.json()
            return r.text
        else:
            if return_json:
                return {}
            return ''
