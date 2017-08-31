import datetime
import hashlib
import json
import time

import click
import requests
import rqopen_client

global g_url, g_app_key, g_user_360, g_secret_360, g_user_rq, g_password_rq, g_run_id, g_smtp_user, g_smtp_password, \
    g_smtp_server, g_smtp_port

import smtplib

from email.mime.text import MIMEText


def send_message_inforamtion(content, subject, from_whom, to_whom):
    msg = MIMEText(content)

    msg['Subject'] = subject
    msg['From'] = from_whom
    msg['To'] = to_whom

    s = smtplib.SMTP(g_smtp_server, port=g_smtp_port)
    s.login(user=g_smtp_user, password=g_smtp_password)
    s.send_message(msg)
    s.quit()


class RequestFor360System(dict):
    def _build_sign(self):
        self.update({
            'appkey': g_app_key,
            'user': g_user_360,
            't': time.time() * 1000
        })

        keys = sorted(self.keys())
        string = ''.join([str(self[k]) for k in keys])
        self['s'] = hashlib.md5((string + g_secret_360).encode('ascii')).hexdigest()

    def submit(self):
        self._build_sign()

        content = requests.post(url=g_url, data=self).content.decode('utf-8')

        json_object = json.loads(content)

        return json_object

    def update_ricequant_trade(self, ricequant_trade):
        number, code = ricequant_trade['order_book_id'].split('.')

        self['action'] = 'buy' if ricequant_trade['quantity'] > 0 else 'sell'
        self['amount'] = int(abs(ricequant_trade['quantity']))
        self['prop'] = 'U'
        self['price'] = ricequant_trade['price'] * 1.01 if self['action'] == 'buy' else ricequant_trade['price'] * 0.99
        self['product_code'] = number + '.' + ('SH' if code == 'XSHG' else 'SZ')


@click.command()
@click.option('--url', envvar='RQ360_URL', default='http://tstockapi.nicaifu.com/api.php')
@click.option('--app_key', envvar='RQ360_APPKEY', default=None)
@click.option('--user_360', envvar='RQ360_360USER', default=None)
@click.option('--secret_360', envvar='RQ360_360SECRET', default=None)
@click.option('--user_rq', envvar='RQ360_RQUSER', default=None)
@click.option('--password_rq', envvar='RQ360_RQPASSWORD', default=None)
@click.option('--run_id', envvar='RQ360_RUNID', default=None)
@click.option('--smtp_user', envvar='RQ360_SMTPUSER', default=None)
@click.option('--smtp_password', envvar='RQ360_SMTPPASSWORD', default=None)
@click.option('--smtp_server', envvar='RQ360_SMTPSERVER', default='smtp.exmail.qq.com')
@click.option('--smtp_port', envvar='RQ360_SMTPPORT', default=994)
def main(url, app_key, user_360, secret_360, user_rq, password_rq, run_id, smtp_user, smtp_password, smtp_server,
         smtp_port):
    global g_url, g_app_key, g_user_360, g_secret_360, g_user_rq, g_password_rq, g_run_id, g_smtp_user, g_smtp_password, g_smtp_server, g_smtp_port

    g_url, g_app_key, g_user_360, g_secret_360, g_user_rq, g_password_rq, g_run_id, g_smtp_user, g_smtp_password, g_smtp_server, g_smtp_port = \
        url, app_key, user_360, secret_360, user_rq, password_rq, run_id, smtp_user, smtp_password, smtp_server, smtp_port

    client = rqopen_client.RQOpenClient(g_user_rq, g_password_rq)

    latest_finished_order_id = 0

    while (True):
        try:

            data = client.get_day_trades(run_id=run_id)

            if (data['code'] != 200):
                print(str(data))
                send_message_inforamtion(content='Exception:' + str(data), from_whom=g_smtp_user, to_whom=g_user_rq,
                                         subject='Error report for RQ360 online PT')

            trades = client.get_day_trades(run_id=run_id)['resp']['trades']

            for trade in trades:

                if trade['order_id'] <= latest_finished_order_id:
                    continue

                latest_finished_order_id = trade['order_id']

                request = RequestFor360System()
                request.update_ricequant_trade(trade)

            print('%s Synchronized' % str(datetime.datetime.now()))

        except Exception as e:

            print(str(e))
            send_message_inforamtion(content='Exception:' + str(e), from_whom=g_smtp_user, to_whom=g_user_rq,
                                     subject='Error report for RQ360 online PT')

        time.sleep(5)


if __name__ == '__main__':
    main()
