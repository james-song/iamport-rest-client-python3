import json
import requests

from .decorator import required

__all__ = ['IAMPORT_API_URL', 'Iamport']

IAMPORT_API_URL = 'https://api.iamport.kr/'


class Iamport:
    def __init__(self, imp_key, imp_secret, imp_url=IAMPORT_API_URL):
        self.imp_key = imp_key
        self.imp_secret = imp_secret
        self.imp_url = imp_url
        requests_session = requests.Session()
        requests_adapters = requests.adapters.HTTPAdapter(max_retries=3)
        requests_session.mount('https://', requests_adapters)
        self.requests_session = requests_session

    class ResponseError(Exception):
        def __init__(self, code=None, message=None):
            self.code = code
            self.message = message

    class HttpError(Exception):
        def __init__(self, code=None, reason=None):
            self.code = code
            self.reason = reason

    @staticmethod
    def get_response(response):
        if response.status_code != requests.codes.ok:
            raise Iamport.HttpError(response.status_code, response.reason)
        result = response.json()
        if result['code'] != 0:
            raise Iamport.ResponseError(
                result.get('code'), result.get('message')
            )
        return result.get('response')

    def _get_token(self):
        url = f'{self.imp_url}users/getToken'
        payload = {'imp_key': self.imp_key,
                   'imp_secret': self.imp_secret}
        response = self.requests_session.post(url, data=payload)
        return self.get_response(response).get('access_token')

    def get_headers(self):
        return {'X-ImpTokenHeader': self._get_token()}

    def _get(self, url, payload=None):
        headers = self.get_headers()
        response = self.requests_session.get(url,
                                             headers=headers, params=payload)
        return self.get_response(response)

    def _post(self, url, payload=None):
        headers = self.get_headers()
        response = self.requests_session.post(url,
                                              headers=headers, data=payload)
        return self.get_response(response)

    def _delete(self, url, payload=None):
        headers = self.get_headers()
        response = self.requests_session.delete(url,
                                                headers=headers, data=payload)
        return self.get_response(response)

    def find_by_merchant_uid(self, merchant_uid):
        url = f'{self.imp_url}payments/find/{merchant_uid}'
        return self._get(url)

    def find_by_imp_uid(self, imp_uid):
        url = f'{self.imp_url}payments/{imp_uid}'
        return self._get(url)

    def find(self, **kwargs):
        merchant_uid = kwargs.get('merchant_uid')
        if merchant_uid:
            return self.find_by_merchant_uid(merchant_uid)
        try:
            imp_uid = kwargs['imp_uid']
        except KeyError:
            raise KeyError('merchant_uid or imp_uid is required')
        return self.find_by_imp_uid(imp_uid)

    def _cancel(self, payload):
        url = f'{self.imp_url}payments/cancel'
        return self._post(url, payload)

    @required(['merchant_uid', 'amount',
               'card_number', 'expiry', 'birth', 'pwd_2digit'])
    def pay_onetime(self, **kwargs):
        url = f'{self.imp_url}subscribe/payments/onetime'
        return self._post(url, kwargs)

    @required(['customer_uid', 'merchant_uid', 'amount'])
    def pay_again(self, **kwargs):
        url = f'{self.imp_url}subscribe/payments/again'
        return self._post(url, kwargs)

    @required(['customer_uid', 'card_number', 'expiry', 'birth'])
    def customer_create(self, **kwargs):
        customer_uid = kwargs.get('customer_uid')
        url = f'{self.imp_url}subscribe/customers/{customer_uid}'
        return self._post(url, kwargs)

    def customer_get(self, customer_uid):
        url = f'{self.imp_url}subscribe/customers/{customer_uid}'
        return self._get(url)

    def customer_delete(self, customer_uid):
        url = f'{self.imp_url}subscribe/customers/{customer_uid}'
        return self._delete(url)

    @required(['merchant_uid', 'amount', 'card_number', 'expiry'])
    def pay_foreign(self, **kwargs):
        url = f'{self.imp_url}subscribe/payments/foreign'
        return self._post(url, kwargs)

    @required(['customer_uid'])
    def pay_schedule(self, **kwargs):
        headers = self.get_headers()
        headers['Content-Type'] = 'application/json'
        url = f'{self.imp_url}subscribe/payments/schedule'
        for key in ['merchant_uid', 'schedule_at', 'amount']:
            for schedules in kwargs['schedules']:
                if key not in schedules:
                    raise KeyError('Essential parameter is missing!: %s' % key)

        response = self.requests_session.post(url, headers=headers,
                                              data=json.dumps(kwargs))
        return self.get_response(response)

    @required(['customer_uid'])
    def pay_unschedule(self, **kwargs):
        url = f'{self.imp_url}subscribe/payments/unschedule'
        return self._post(url, kwargs)

    def cancel_by_merchant_uid(self, merchant_uid, reason, **kwargs):
        payload = {'merchant_uid': merchant_uid, 'reason': reason}
        if kwargs:
            payload.update(kwargs)
        return self._cancel(payload)

    def cancel_by_imp_uid(self, imp_uid, reason, **kwargs):
        payload = {'imp_uid': imp_uid, 'reason': reason}
        if kwargs:
            payload.update(kwargs)
        return self._cancel(payload)

    def cancel(self, reason, **kwargs):
        imp_uid = kwargs.pop('imp_uid', None)
        if imp_uid:
            return self.cancel_by_imp_uid(imp_uid, reason, **kwargs)

        merchant_uid = kwargs.pop('merchant_uid', None)
        if merchant_uid is None:
            raise KeyError('merchant_uid or imp_uid is required')
        return self.cancel_by_merchant_uid(merchant_uid, reason, **kwargs)

    def is_paid(self, amount, **kwargs):
        response = kwargs.get('response')
        if not response:
            response = self.find(**kwargs)
        status = response.get('status')
        response_amount = response.get('amount')
        return status == 'paid' and response_amount == amount

    def prepare(self, merchant_uid, amount):
        url = f'{self.imp_url}payments/prepare'
        payload = {'merchant_uid': merchant_uid, 'amount': amount}
        return self._post(url, payload)

    def prepare_validate(self, merchant_uid, amount):
        url = f'{self.imp_url}payments/prepare/{merchant_uid}'
        response = self._get(url)
        response_amount = response.get('amount')
        return response_amount == amount
