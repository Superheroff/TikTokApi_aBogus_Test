# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import json
from pathlib import Path
import random
import time
import re
from urllib.parse import urlencode, quote, parse_qs, urlparse
import requests
import math
import uuid
from curl_cffi import requests as tls_requests


class TikTokApi:

    host = 'http://124.220.179.225:5050'

    proxy = {
        'host': 'e688.kdltps.com:15818',
        'user': 't19759518838891',
        'password': 'ftlnwbla'
    }
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": proxy['user'], "pwd": proxy['password'],
                                                        "proxy": proxy['host']}
    }

    def __init__(self, cid):
        self.cid = cid
        self.array = {}
        self.__web_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'

    @property
    def __AppKey(self):
        """
        这是本api的加密
        :return:
        """
        data = self.cid + '5c6b8r9a'
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def convert_high_low_to_values(high, low):
        """
        将high/low结构转换为各种表示形式

        Args:
            high: 高32位
            low: 低32位
        """
        int64_value = (high << 32) | (low & 0xFFFFFFFF)
        return int64_value

    @staticmethod
    def getUUID():
        t = int(time.time() * 1000)  # 当前时间的毫秒数
        e = int(time.perf_counter() * 1000) if hasattr(time, 'perf_counter') else 0
        uuid_template = "xxxxxxxx"

        def replace_char(match):
            char = match.group(0)
            r = 16 * random.random()
            nonlocal t, e
            if t > 0:
                r = (t + r) % 16
                r = int(r)
                t = math.floor(t / 16)
            else:
                r = (e + r) % 16
                r = int(r)
                e = math.floor(e / 16)

            if char == 'x':
                return format(int(r), 'x')
            else:
                result = (3 & int(r)) | 8
                return format(result, 'x')

        return re.sub(r'[xy]', replace_char, uuid_template)

    @staticmethod
    def getTraceId():
        return TikTokApi.getUUID().replace('-', '')

    @staticmethod
    def get_cookie_value_oneliner(cookie_str, key):
        return next((v.split('=', 1)[1] for v in cookie_str.split('; ') if v.startswith(key + '=')), None)

    def getxBogus(self, url:str, body=None):
        """
        v2/xbogus 适用于xbogus+_signature+abogus共同出现的场景
        :param url:
        :param body:
        :return:
        """
        sign_url = TikTokApi.host + '/dyapi/v2/web/signature'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        params = {
            'url': url,
            'body': body,
            'sign': sign
        }
        resp = requests.post(sign_url, data=params, headers=header).text
        print('web_xbogus', resp)
        return resp

    def encode_login(self, key, userAgent):
        """JWT body参数加签"""
        sign_url = TikTokApi.host + '/dyapi/web/encode_login'
        sign = self.set_sign
        body = {
            '_token': key,
            'userAgent': userAgent,
            'sign': sign
        }
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        resp = requests.post(sign_url, data=body, headers=header).text
        print('encode_login', resp)
        return resp



    def getABogus(self, url, ua, data=None, t=None):
        """
        aBogus版本,默认douyin=1.0.1.19-fix,tuan=团长1.0.1.15,ju=巨量百应1.0.1.20,doudian=1.0.1.1,qc=巨量千川1.0
        :return:
        """
        sign_url = TikTokApi.host + '/dyapi/web/abogus'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign

        data = {
            'url': url,
            'ua': ua,
            'data': data,
            't': t,
            'sign': sign
        }
        resp = requests.post(sign_url, data=data, headers=header)
        # print('aBogus:', resp['abogus'], 'aBogus长度:', len(resp['abogus']))
        print('getABogus', resp.text)
        return resp.json()

    def get_web_sign(self, url, referer, ua):
        """
        获取web sign
        :param url:
        :param referer:
        :param ua:
        :return:
        """
        sign_url = TikTokApi.host + '/dyapi/web/signature'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign
        params = {
            'url': url,
            'referer': referer,
            'ua': ua,
            'sign': sign

        }
        resp = requests.post(sign_url, data=params, headers=header).json()
        print('web_sign', resp)
        return resp

    APP_UA = ('com.ss.android.ugc.aweme/410001 (Linux; U; Android 16; zh_CN; 2407FRK8EC; '
              'Build/BP2A.250605.031.A3; Cronet/TTNetVersion:f2d9b21f 2026-10-12 '
              'QuicVersion:636d43af 2026-09-02)')

    # 票据链静态字段：跨会话逐字节不变的部分（与真机抓包一致）。
    # ree-public-key / client-cert / static-sign 三项不写死，由
    # ticket_guard_headers() 按私钥与 sec-ts 动态生成，保证三者自洽。
    TICKET_GUARD_HEADERS = {
        'passport-sdk-settings': 'x-tt-token,sec_user_id,device_transfer_s_0,device_transfer_ab_2',
        'passport-sdk-sign': 'x-tt-token,sec_user_id',
        'bd-ticket-guard-tee-status': '0',
        'bd-ticket-guard-iteration-version': '2',
        'x-tt-request-tag': 'n=1;s=-1;p=0',
    }

    # 本地 P-256 私钥标量（0x 十六进制）；公钥、证书、签名都由它当场派生。
    TICKET_GUARD_PRIVATE_KEY = '0xAA84079218C5004A1240DFAD3660A6CDA8C89D425D319A3AEC3B26A638F5667B'
    # 服务端下发的 sec-ts 令牌，无法本地生成；为空则跳过 static-sign，不伪造。
    TICKET_GUARD_SEC_TS = '#wi8I5o4ukHFXKd9PwjLIi72DJeCF5kEQIchWS2oQyCyyAb6fTDbV+ChjDRi6'

    # FIPS 186-4 / SEC 2 P-256 参数；签名与证书全部纯 Python 计算，不引第三方库。
    _P256_P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    _P256_A = _P256_P - 3
    _P256_B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    _P256_N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    _P256_G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
               0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

    @classmethod
    def _p256_add(cls, u, v):
        if u is None:
            return v
        if v is None:
            return u
        x, y = u
        xx, yy = v
        if x == xx and (y + yy) % cls._P256_P == 0:
            return None
        if u == v:
            s = ((3 * x * x + cls._P256_A) * pow(2 * y, -1, cls._P256_P)) % cls._P256_P
        else:
            s = ((yy - y) * pow(xx - x, -1, cls._P256_P)) % cls._P256_P
        nx = (s * s - x - xx) % cls._P256_P
        return nx, (s * (x - nx) - y) % cls._P256_P

    @classmethod
    def _p256_mul(cls, k, point=None):
        if not 0 < k < cls._P256_N:
            raise ValueError('P-256 标量越界')
        point = cls._P256_G if point is None else point
        result = None
        while k:
            if k & 1:
                result = cls._p256_add(result, point)
            point = cls._p256_add(point, point)
            k >>= 1
        return result

    @staticmethod
    def _der_int(value):
        raw = value.to_bytes((value.bit_length() + 7) // 8 or 1, 'big')
        if raw[0] & 0x80:
            raw = b'\x00' + raw
        return b'\x02' + bytes([len(raw)]) + raw

    @classmethod
    def ticket_guard_headers(cls):
        """按本地私钥与 sec-ts 动态生成票据链，静态字段原样保留。
        私钥导出公钥 → 公钥写进 client-cert → 同一把钥匙对 sec-ts 做双重
        SHA256 的 P-256 签名，三项因此始终自洽。sec-ts 是服务端下发的令牌，
        不能本地生成；缺省时只跳过 static-sign，不伪造。
        """
        raw_key = cls.TICKET_GUARD_PRIVATE_KEY
        if isinstance(raw_key, str):
            raw_key = bytes.fromhex(raw_key[2:] if raw_key[:2].lower() == '0x' else raw_key)
        private = int.from_bytes(raw_key, 'big') if isinstance(raw_key, bytes) else int(raw_key)
        if not 0 < private < cls._P256_N:
            raise ValueError('TICKET_GUARD_PRIVATE_KEY 不在 P-256 有效范围内')
        x, y = cls._p256_mul(private)
        public_raw = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        headers = dict(cls.TICKET_GUARD_HEADERS)
        headers['ticket_guard_private_key'] = cls.TICKET_GUARD_PRIVATE_KEY
        sec_ts = cls.TICKET_GUARD_SEC_TS
        if sec_ts:
            headers['bd-ticket-guard-sec-ts'] = sec_ts
        headers['bd-ticket-guard-ree-public-key'] = base64.b64encode(public_raw).decode()
        headers['bd-ticket-guard-client-cert'] = base64.b64encode(
            b'pub.' + base64.b64encode(public_raw)).decode()
        if sec_ts:
            digest = hashlib.sha256(('sec_ts=' + sec_ts).encode('utf-8')).digest()
            z = int.from_bytes(hashlib.sha256(digest).digest(), 'big')
            while True:
                k = random.randrange(1, cls._P256_N)
                r = cls._p256_mul(k)[0] % cls._P256_N
                s = (pow(k, -1, cls._P256_N) * (z + r * private)) % cls._P256_N
                if r and s:
                    body = cls._der_int(r) + cls._der_int(s)
                    headers['bd-ticket-guard-static-sign'] = base64.b64encode(
                        b'\x30' + bytes([len(body)]) + body).decode()
                    break
        return headers

    @staticmethod
    def _signer_body_text(resp):
        """签名服务的中文 msg 是 GBK 输出的，先 utf-8 再回退 gbk，避免乱码掩盖真实报错。"""
        for encoding in ('utf-8', 'gbk'):
            try:
                return resp.content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return resp.text

    @staticmethod
    def _query_value(url, key):
        values = parse_qs(urlparse(url).query).get(key)
        return values[0] if values else None

    def get_xgorgon(
            self,
            url,
            headers=None,
            body=None,
            body_encoding=None,
            device_token=None,
            device_id=None,
            iid=None,
            bd_ticket_guard=None,
            timeout=30
    ):
        """调用 /dyapi/xgorgon，返回平铺的签名头字典。

        服务端硬性要求（缺一个就 400/404，不会给任何签名值）：
        1. url 的查询串里必须同时有 device_id 和 iid（或显式传 device_id/iid）；
        2. device_token 必须放在 JSON body 里（只放 headers 的 x-tt-dt 服务端不认）；
        3. sign 与请求头 timestamp 必须同秒且不超过服务端时间窗，否则 404 签名无效；
        4. bd_ticket_guard 里带 ticket_guard_private_key 时，必须同时带
           bd-ticket-guard-sec-ts。

        只有把 TG 放进 bd_ticket_guard（payload）才会有 static-sign / client-cert /
        sec-ts / ree-public-key / tee-status 回显；只放请求头一律被忽略。为了不踩这个
        坑，bd_ticket_guard 缺省时会自动从 headers 里收 bd-ticket-guard-* 与
        ticket_guard_private_key，也接受 JSON 字符串。
        """
        # 老调用点是 get_xgorgon(url, cookie, body, 'max', headers) 这种写法，第二个
        # 位置参数其实是 Cookie 字符串，这里兼容掉，避免 str.get 直接抛 AttributeError。
        if not isinstance(headers, dict):
            headers = {}
        device_id = str(device_id or self._query_value(url, 'device_id') or '')
        iid = str(iid or self._query_value(url, 'iid') or '')
        missing = [name for name, value in (('device_id', device_id), ('iid', iid)) if not value]
        if missing:
            raise ValueError('xgorgon 需要 %s：请放进 url 查询串或显式传入' % '/'.join(missing))

        device_token = str(device_token or headers.get('x-tt-dt') or headers.get('X-Tt-Dt') or '')
        if not device_token:
            raise ValueError('xgorgon 需要 device_token：请显式传入或在 headers 里给 x-tt-dt')

        if bd_ticket_guard is None:
            # 只把 TG 字段当请求头发出去，服务端一律忽略（实测只回 16 个头、没有
            # static-sign/client-cert）。这里自动把 headers 里的 TG 字段收进 payload。
            collected = {key: value for key, value in headers.items()
                         if key.lower().startswith('bd-ticket-guard-')
                         or key.lower() == 'ticket_guard_private_key'}
            if collected:
                bd_ticket_guard = collected
        elif isinstance(bd_ticket_guard, str):
            bd_ticket_guard = json.loads(bd_ticket_guard)

        if bd_ticket_guard:
            flattened = {str(k).lower(): v for k, v in bd_ticket_guard.items()}
            if 'ticket_guard_private_key' in flattened and not flattened.get('bd-ticket-guard-sec-ts'):
                raise ValueError('bd_ticket_guard 带 ticket_guard_private_key 时必须同时带 '
                                 'bd-ticket-guard-sec-ts')

        sign_url = TikTokApi.host + '/dyapi/xgorgon'
        ts = str(time.time()).split('.')[0]
        request_headers = {
            'cid': self.cid,
            'timestamp': ts,
            'Content-Type': 'application/json',
        }
        payload = {
            # sign 内部自己取时间，跨秒会和上面的 timestamp 对不上，这里固定同一 ts。
            'sign': hashlib.md5(
                ('1005' + self.cid + ts + self.__AppKey).encode('utf8')).hexdigest(),
            'url': url,
            'body': '' if body is None else body,
            'device_token': device_token,
        }
        if body_encoding:
            payload['body_encoding'] = body_encoding
        if bd_ticket_guard:
            payload['bd_ticket_guard'] = bd_ticket_guard

        resp = requests.post(sign_url, json=payload, headers=request_headers, timeout=timeout)
        text = self._signer_body_text(resp)
        try:
            data = json.loads(text)
        except ValueError:
            data = {'raw': text[:500]}
        if resp.status_code != 200 or 'X-Gorgon' not in data:
            raise RuntimeError('xgorgon 失败: %s %s' % (
                resp.status_code, data.get('msg') or data.get('detail') or text[:300]))
        print('xgorgon', data)
        return data

    @staticmethod
    def parse_comment_stream(body):
        """解析评论响应：纯 JSON，或 stream 端点的「十六进制长度前缀 + JSON」分帧。
        与 comment_api_direct.py 的 parse_comment_stream 等价；body 传 HTTP 解压后的字节。
        """
        raw = body.lstrip(b'\r\n \t')
        if raw.startswith(b'{'):
            document = json.loads(raw)
            if not isinstance(document, dict):
                raise ValueError('评论响应不是 JSON 对象')
            return [document]
        documents = []
        position = 0
        while position < len(raw):
            while position < len(raw) and raw[position] in (10, 13):
                position += 1
            if position == len(raw):
                break
            end = raw.find(b'\n', position)
            if end < 0:
                raise ValueError('评论分帧长度不完整')
            size = int(raw[position:end].strip(), 16)
            position = end + 1
            if size == 0:
                break
            if size < 0 or size > len(raw) - position:
                raise ValueError('评论分帧负载不完整')
            document = json.loads(raw[position:position + size])
            if not isinstance(document, dict):
                raise ValueError('评论分帧不是 JSON 对象')
            documents.append(document)
            position += size
        if not documents:
            raise ValueError('评论响应没有可解析的帧')
        return documents

    @staticmethod
    def decode_comment_common_data(blob):
        """解 comment_common_data：base64 → 1.0.0 信封，输出头信息与负载特征。

        值形如 MS4wLjAAAAAA...：解码后前 5 字节是 '1.0.0'，随后 4 字节头，余下是
        高熵负载（本地没有对应密钥，只给出长度、摘要、hex 前缀与可打印片段）。
        """
        if not blob:
            return None
        raw = base64.urlsafe_b64decode(str(blob) + '=' * (-len(str(blob)) % 4))
        payload = raw[9:] if raw[:5] == b'1.0.0' else raw
        strings = [match.decode('ascii', errors='replace')
                   for match in re.findall(rb'[ -~]{6,}', payload)[:5]]
        return {
            'version': raw[:5].decode('ascii', errors='replace') if raw[:5].isascii() else None,
            'header_hex': raw[5:9].hex(),
            'decoded_bytes': len(raw),
            'payload_bytes': len(payload),
            'payload_sha256': hashlib.sha256(payload).hexdigest()[:16],
            'payload_hex': payload[:32].hex(),
            'strings': strings,
            'encrypted': raw[:5] == b'1.0.0',
        }

    def app_comment_list(self, aweme_id, device, cursor=0, count=20, timeout=30):
        """APP 评论采集：本地签名后直接请求 comment/list。

        device 至少含 device_id / iid，cdid 与 device_token 有就一起带上。
        """
        now_ms = int(time.time() * 1000)
        query = urlencode({
            'aweme_id': str(aweme_id), 'cursor': str(cursor), 'count': str(count),
            'item_type': '0', 'insert_ids': '', 'comment_scene': '0', 'page_source': '0',
            'device_id': str(device['device_id']), 'iid': str(device['iid']),
            'cdid': str(device.get('cdid', '')), 'aid': '1128', 'app_name': 'aweme',
            'version_code': '410000', 'version_name': '41.0.0', 'device_platform': 'android',
            'os': 'android', 'ssmix': 'a', 'device_type': '2407FRK8EC', 'device_brand': 'Redmi',
            'language': 'zh', 'os_api': '36', 'os_version': '16', 'channel': 'xiaomi_1128_64',
            'manifest_version_code': '410001', 'resolution': '1220*2522', 'dpi': '520',
            'update_version_code': '41009900', 'package': 'com.ss.android.ugc.aweme',
            'cpu_support64': 'true', 'host_abi': 'arm64-v8a', 'ac': 'wifi',
            '_rticket': str(now_ms), 'ts': str(now_ms // 1000),
        })
        url = 'https://api3-normal-c.amemv.com/aweme/v2/comment/list/?' + query
        headers = {
            'user-agent': self.APP_UA,
            'x-tt-dt': str(device.get('device_token', '')),
            'x-ss-req-ticket': str(now_ms),
            'accept-encoding': 'gzip',
        }
        headers.update({str(k): str(v) for k, v in self.get_xgorgon(url, headers=headers).items()})
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        # 评论接口是 stream：hex 长度前缀 + JSON 分帧，不能直接 .json()。
        frames = self.parse_comment_stream(response.content)
        document = {}
        comments = {}
        order = []
        for frame in frames:
            for comment in frame.get('comments') or []:
                cid = str(comment.get('cid', ''))
                if cid and cid not in comments:
                    order.append(cid)
                if cid:
                    comments[cid] = comment
            document.update({name: value for name, value in frame.items()
                             if name != 'comments'})
        if comments:
            document['comments'] = [comments[cid] for cid in order]
        document['_frames'] = len(frames)
        raw_common = document.get('comment_common_data')
        if raw_common:
            document['comment_common_data'] = self.decode_comment_common_data(raw_common)
        return document

    def tt_encrypt(self, plain, seed=None, gz=True, timeout=30):
        """调用 /dyapi/tt_encrypt：传明文，返回 result(base64)。

        gz=True 返回 base64(TTEncrypt(gzip(明文)))（tt_info 用）；
        gz=False 返回裸 TTEncrypt 密文的 base64（发码 body 用，解码后发二进制）。
        """
        url = TikTokApi.host + '/dyapi/tt_encrypt'
        ts = str(time.time()).split('.')[0]
        payload = {'sign': self.set_sign, 'data': plain, 'gzip': gz}
        if seed:
            payload['seed'] = seed
        resp = requests.post(url, json=payload, timeout=timeout, headers={
            'cid': self.cid, 'timestamp': ts, 'Content-Type': 'application/json'})
        result = resp.json()
        if resp.status_code != 200 or not result.get('result'):
            raise RuntimeError('tt_encrypt 失败: %s %s' % (resp.status_code, result))
        return result['result']

    def app_send_code(self, phone, device, country_code='+86', timeout=30):
        """发送验证码：明文写在这里，加密交给 /dyapi/tt_encrypt。

        plain 为原生表单明文（mobile 明文，type=3731 / unbind_exist=35 即 XOR5 结果）；
        接口返回 {'result': base64}，本方法把该 base64 作为请求体并参与签名。
        默认 dry-run 只返回待发请求；send=True 才真正 POST。
        """
        now_ms = int(time.time() * 1000)
        plain = (
            'is_vcd=1&reg_cookie_opt=true&ttnet_sdk_version=4.2.301.15-douyin&auto_read=0'
            '&auth_sdk_version=4.7.7-rc.48&mix_mode=1&account_app_language=zh&mobile='
            + quote(country_code + ' ' + str(phone), safe='') +
            '&language=zh&multi_login=1&type=3731&sec_sdk_version=67765248'
            '&account_sdk_source=app'
            '&passport_support_flow=choose_account,captcha,real_name_check,verify'
            '&unbind_exist=35&verify_sdk_version=4.2.2.cn&is_from_iesaccountsaas=1'
        )
        # 发码 body 必须是裸 TTEncrypt 二进制：接口 gzip=False 返回裸密文 base64，解码还原。
        encoded = self.tt_encrypt(plain, gz=False)
        raw_body = base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4))
        query = urlencode({
            'passport-sdk-version': '60763', 'request_from_account_sdk': '1',
            'is_from_ttaccountsdk': '1', 'klink_egdi': str(device.get('klink_egdi', '')),
            'iid': str(device['iid']), 'device_id': str(device['device_id']),
            'ac': 'wifi', 'channel': 'xiaomi_1128_64', 'aid': '1128', 'app_name': 'aweme',
            'version_code': '410000', 'version_name': '41.0.0', 'device_platform': 'android',
            'os': 'android', 'ssmix': 'a', 'device_type': '2407FRK8EC', 'device_brand': 'Redmi',
            'language': 'zh', 'os_api': '36', 'os_version': '16', 'manifest_version_code': '410001',
            'resolution': '1220*2522', 'dpi': '520', 'update_version_code': '41009900',
            '_rticket': str(now_ms), 'package': 'com.ss.android.ugc.aweme',
            'cpu_support64': 'true', 'host_abi': 'arm64-v8a', 'is_guest_mode': '0',
            'app_type': 'normal', 'minor_status': '0', 'appTheme': 'light',
            'is_preinstall': '0', 'need_personal_recommend': '1', 'is_android_pad': '0',
            'is_android_fold': '0', 'ts': str(now_ms // 1000), 'cdid': str(device.get('cdid', '')),
        })
        url = 'https://api5-normal-lq.amemv.com/passport/mobile/send_code/?' + query
        headers = {
            'user-agent': self.APP_UA,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept-encoding': 'gzip, deflate, br', 'x-ss-dp': '1128', 'sdk-version': '2',
            'passport-sdk-version': '60763', 'x-vc-bdturing-sdk-version': '4.2.2.cn',
            'x-tt-dt': str(device.get('device_token', '')), 'x-ss-req-ticket': str(now_ms),
            'x-tt-cipher-version': '1.0.0', 'x-tt-encrypt-info': '1',
            **({'cookie': str(device['cookie'])} if device.get('cookie') else {}),
            **({'x-tt-passport-csrf-token': str(device['csrf'])} if device.get('csrf') else {}),
            **({'x-tt-device-dtrait-token': str(device['dtrait_token'])} if device.get('dtrait_token') else {}),
            **({'x-tt-device-dtrait': str(device['dtrait'])} if device.get('dtrait') else {}),
            **self.ticket_guard_headers(),
            **({str(k): str(v) for k, v in device['tg_headers'].items()
                if not k.startswith('bd-ticket-guard-client-data') and not k.startswith('bd-ticket-guard-version')
                and not k.startswith('bd-ticket-guard-iteration-version')} if device.get('tg_headers') else {}),
        }

        # 票据链是会话观测值：私钥在 headers 里，get_xgorgon 会自动收进
        # bd_ticket_guard 交给服务端，换取 static-sign / client-cert 等回显。
        signed = self.get_xgorgon(url, body=raw_body.hex(), body_encoding='hex', headers=headers,
                                  bd_ticket_guard=device.get('bd_ticket_guard'))
        print(json.dumps(signed, ensure_ascii=False, indent=2))
        headers.update({str(k): str(v) for k, v in signed.items()})
        resp = requests.post(url, data=raw_body, headers=headers, timeout=timeout, proxies={'http':'http://127.0.0.1:7890'})
        return resp.text

    def app_play_report(self, video_id, device, cookie=None, impr_id=None, play_ms=0, timeout=30):
        """播放上报：POST /aweme/v1/aweme/stats/。

        video_id 是作品 ID，进 item_id / pre_item_id / batch_item_ids；
        impr_id 缺省按当前时间本地生成（真实链路取自推荐流响应的 x-tt-logid）；
        play_ms 为已播放毫秒，>=15000 时 pre_item_is_finish=1。
        stats 接口成功时不回响应体（200/204 空 body），所以返回结构化结果而不是 resp.text。
        """
        now_ms = int(time.time() * 1000)
        if impr_id is None:
            impr_id = time.strftime('%Y%m%d%H%M%S', time.localtime()) + uuid.uuid4().hex[:16].upper()
        elapsed = max(0, int(play_ms))
        entry = {
            'item_id': str(video_id), 'pre_item_id': str(video_id),
            'pre_impr_id': impr_id, 'request_id': impr_id,
            'action_time': str(now_ms // 1000), 'pre_item_time': str(elapsed),
            'pre_item_playtime': str(elapsed), 'pre_item_progress': '0',
            'pre_item_max_progress': str(elapsed),
            'pre_item_is_finish': '1' if elapsed >= 15000 else '0',
            'play_delta': '1', 'video_play_action': '1', 'order': '0',
            'pre_item_seen': '0', 'traceless_view': '0', 'is_from_ad': '0',
            'follow_status': '0', 'follower_status': '0', 'aweme_type': '0',
            'pre_aweme_type': '0', 'is_familiar': '0', 'is_mate': '0',
            'data_from': '0', 'resp_from': 'sati', 'tab_type': '0',
            'first_install_time': str(int(time.time()) - 86400),
        }
        body = urlencode([
            ('target_batch_time', '5'),
            ('batch_time', '5006'),
            ('batch_stats', json.dumps([entry], ensure_ascii=False, separators=(',', ':'))),
            ('batch_item_ids', str(video_id)),
            ('target_batch_count', '3'),
        ])
        query = urlencode({
            'device_id': str(device['device_id']), 'iid': str(device['iid']),
            'cdid': str(device.get('cdid', '')), 'aid': '1128', 'app_name': 'aweme',
            'version_code': '410000', 'version_name': '41.0.0', 'device_platform': 'android',
            'os': 'android', 'ssmix': 'a', 'device_type': '2407FRK8EC', 'device_brand': 'Redmi',
            'language': 'zh', 'os_api': '36', 'os_version': '16', 'channel': 'xiaomi_1128_64',
            'manifest_version_code': '410001', 'resolution': '1220*2522', 'dpi': '520',
            'update_version_code': '41009900', 'package': 'com.ss.android.ugc.aweme',
            'cpu_support64': 'true', 'host_abi': 'arm64-v8a', 'ac': 'wifi',
            '_rticket': str(now_ms), 'ts': str(now_ms // 1000),
        })
        url = 'https://aweme.snssdk.com/aweme/v1/aweme/stats/?' + query
        headers = {
            'user-agent': self.APP_UA,
            'x-tt-dt': str(device.get('device_token', '')),
            'x-ss-req-ticket': str(now_ms),
            'content-type': 'application/x-www-form-urlencoded',
            'accept-encoding': 'identity',
            **self.ticket_guard_headers()

        }
        print(headers)
        if cookie:
            headers['cookie'] = cookie
        signed = self.get_xgorgon(url, body=body, headers=headers)
        headers.update({str(k): str(v) for k, v in signed.items()})
        resp = requests.post(url, data=body.encode('utf-8'), headers=headers, timeout=timeout)
        return resp.text

    def get_ApiInfo(self):
        """
        获取接口使用情况
        minCount 当前用了多少
        maxCount 你可以用的最大值
        :return:
        """
        url = TikTokApi.host + '/end_time'
        resp = requests.post(url, data={'cid': self.cid, 'api': 'dyapi'}).text
        return resp

    def get_device(self, proxy=None, model=None, brand=None, rom=None,
                   resolution=None, dpi=None, oaid=None, bind=True):
        """获取设备号：调用网关 /dyapi/device/register（注册 + dtrait 绑定 + 二次注册）

        一次调用只注册一台设备。服务端按「设备指纹 + OAID」判定设备，本接口每次
        随机生成指纹与 OAID，因此每次调用都会返回一台新设备（同 IP 有创建配额）。

        :param proxy:      代理，支持 "http://user:pwd@host:port" 或 {"host","user","password"}
        :param model:      指定机型，缺省随机
        :param brand:      指定品牌，缺省随机
        :param rom:        指定 ROM，缺省随机
        :param resolution: 指定分辨率，如 1260*2720
        :param dpi:        指定 DPI
        :param oaid:       指定 OAID，缺省随机
        :param bind:       是否执行 dtrait 绑定，默认 True
        :return: 单个设备 dict
        """
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        params = {
            'sign': self.set_sign,
            'bind': 'true' if bind else 'false',
        }
        if proxy:
            params['proxy'] = proxy if isinstance(proxy, str) else json.dumps(proxy, ensure_ascii=False)
        for name, value in (('model', model), ('brand', brand), ('rom', rom),
                            ('resolution', resolution), ('dpi', dpi), ('oaid', oaid)):
            if value not in (None, ''):
                params[name] = str(value)
        resp = requests.post(TikTokApi.host + '/dyapi/device/register',
                             data=params, headers=header, timeout=90)
        try:
            data = resp.json()
        except ValueError:
            raise RuntimeError('设备注册接口返回非 JSON: %s %s' % (resp.status_code, resp.text[:200]))
        if resp.status_code != 200:
            raise RuntimeError('设备注册失败: %s %s' % (resp.status_code, data))
        print('设备id:', data.get('device_id'), 'iid:', data.get('iid'),
              'new_user:', data.get('new_user'), 'bound:', data.get('bound'))
        return data

    def __md5(self, string):
        post_data = gzip.compress(bytes(json.dumps(string), encoding="utf8"))
        m = hashlib.md5()
        m.update(bytes(post_data))
        str_md5 = m.hexdigest()
        return str_md5.upper()

    def get_shop_product(self, uid, device_token=''):
        """
        获取橱窗列表
        :param uid:
        :return:
        """
        # ecom5-normal-lf.ecombdapi.com
        proxy = {
            "host": "q210.kdltps.com:15818",
            "user": "t19759795155723",
            "password": "3eox5mcw"
        }
        proxies = {
            # "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": proxy['user'], "pwd": proxy['password'],
                                                             "proxy": proxy['host']}
        }

        uri = f"https://api3-normal-c.amemv.com/aweme/v1/shop/product/list/?sec_author_id" \
              f"={uid}&target_tab_type=100&cursor=0&size=10" \
              f"&is_first_enter=false" \
              f"&iid=2966909673546948&device_id=2966909673542852&ac" \
              f"=wifi&channel=update&aid=2329&app_name=aweme&version_code=150900&version_name=15.9.0&device_platform" \
              f"=android&os=android&ssmix=a&device_type=MI+9&device_brand=Xiaomi&language=zh&os_api=28&os_version=9" \
              f"&manifest_version_code=150901&resolution=900*1600&dpi=320&update_version_code=15909900&_rticket" \
              f"={round(time.time() * 1000)}&package=com.ss.android.ugc.aweme&mcc_mnc=46000&cpu_support64=true&host_abi=arm64-v8a" \
              f"&is_guest_mode=0&app_type=normal&minor_status=0&appTheme=light&need_personal_recommend=1" \
              f"&is_android_pad=0&ts={round(time.time())}&md=0"

        headers = {
            'X-SS-REQ-TICKET': str(round(time.time() * 1000)),
            "sdk-version": "1",
            "X-SS-DP": "2329",
            # "Host": "api5-normal-c-lf.amemv.com",
            # "X-Tt-Token": "00ce4bfaa6a09c92e09b095040c34ceb9602b5978cf678b3c349f216e32529620188c2c9031d546131ff48317725e401ddbedebb054787f0f71d0776c317a7f01348b84b9899c3fa41f5b2046b11ea198aad41536eb24834fadca8c0fcf8c358a641c-1.0.1",
            'User-Agent': 'com.ss.android.ugc.aweme.lite/150900 (Linux; U; Android 9; zh_CN; MI 9; Build/NMF26X; Cronet/TTNetVersion:a87ab8c7 2020-11-24 QuicVersion:47946d2a 2020-10-14)',
            "Cookie": "store-region=cn-jx; ttreq=1$1430dbab38a934b2fa67d2b0d60d1c93fba83ca7; passport_csrf_token=59d6b08cd8db90cfe156c4bbdcdf4d1c; passport_csrf_token_default=59d6b08cd8db90cfe156c4bbdcdf4d1c; d_ticket=06fa9938e030782addd82051850bca62a49ad; multi_sids=1618070996524280%3A0a7fb4782a2469191a11260deb6600df; passport_assist_user=CkHH2OYUv87kxHaSmuMQmMDq36J_MlY3naYzGqLvWCxWLV4x-zXmKl4DzG9iH6bkcepBwIqt67IFHr3Lu_19DNyAnxpKCjwnbLZqWpCd-N1K2KpNCmpPMC5CAJn_Xh9UMmZYrh1GqwdLu7zaG-VXWQBMZ-smNSRbMLbvc_1nmSo5kYgQ95W_DRiJr9ZUIAEiAQOJCoLD; n_mh=EyEgyFxFI5fiy-d_iT660NAbFEw22sfOXLkhKXhtwCs; sid_guard=0a7fb4782a2469191a11260deb6600df%7C1697889700%7C5184000%7CWed%2C+20-Dec-2023+12%3A01%3A40+GMT; uid_tt=f5fb5c4e17d03a8814b6ab396d1d541a; uid_tt_ss=f5fb5c4e17d03a8814b6ab396d1d541a; sid_tt=0a7fb4782a2469191a11260deb6600df; sessionid=0a7fb4782a2469191a11260deb6600df; sessionid_ss=0a7fb4782a2469191a11260deb6600df; store-region-src=uid; odin_tt=9bb93ac2d9f7879f1194d87fb406a5f2bbca349dac5a9e6a9cc88463a3a8248cc92d8d0572764c03c31e2c43e3ef7b21b75478c2de47d0661d7cef44965cb46241374f234830f7a0773b5f5b0e0bffa5",
        }
        if device_token:
            headers['x-tt-dt'] = device_token
        sig = self.get_xgorgon(uri, headers=headers)
        headers.update(sig)
        # headers["X-Gorgon"] = sig["xgorgon"]
        # headers["X-Khronos"] = sig["xkhronos"]
        # headers["X-SS-REQ-TICKET"] = sig["X-SS-REQ-TICKET"]
        res = requests.get(uri, headers=headers).text
        print("橱窗列表", res)
        return res

    def get_keyword(self, device_id, iid, keyword, page, device_token=''):
        """
        搜索视频
        :param device_id:
        :param iid:
        :param keyword:
        :param page:
        :return:
        """

        url = f"https://aweme.snssdk.com/aweme/v1/search/item/?os_api=25&device_type=Pixel+XL&ssmix=a" \
              f"&manifest_version_code=180101&dpi=560&is_guest_mode=0&app_name=aweme&version_name=18.1" \
              f".0&ts={int(time.time())}&cpu_support64=true&app_type=normal&appTheme=light&ac=wifi&host_abi=armeabi" \
              f"-v7a&channel=wandoujia_lesi_1128_0629&update_version_code=18109900&_rticket=1686903952535" \
              f"&device_platform=android&iid={iid}&version_code=180100&cdid=0528d7f9-bb0f-4d1d-b142-097951a0629d&os" \
              f"=android&is_android_pad=0&openudid=60a02c5de917fa4c&device_id=" \
              f"{device_id}&package=com.ss.android.ugc.aweme&resolution=1440*2392&device_brand=google&language=zh" \
              f"&os_version=7.1.2&need_personal_recommend=1&aid=1128&minor_status=0"

        data = {
            "keyword": keyword,
            "offset": page,
            "count": "12",
            "source": "video_search",
            "from_user": "",
            "search_source": "switch_tab",
            "is_pull_refresh": "1",
            "hot_search": "0",
            "search_id": "",
            "query_correct_type": "1",
            "is_filter_search": "0",
            "sort_type": "0",
            "publish_time": "0",
            "search_range": "0",
            "enter_from": "homepage_hot",
            "backtrace": "",
            "user_avatar_shrink": "64_64",
            "video_cover_shrink": "372_496",
            "previous_searchid": "20230616162541D17367263D89FB0029F7",
            "switch_tab_from": "general",
            "rs_word_count": "5",
            "location_permission": "0",
            "need_filter_settings": "1",
            "enable_history": "1"
        }

        headers = {
            "X-SS-STUB": self.__md5(json.dumps(data)),
            "activity_now_client": str(int(time.time() * 1000)),
            "x-ss-req-ticket": str(int(time.time() * 1000)),
            "x-vc-bdturing-sdk-version": "2.2.1.cn",
            "passport-sdk-version": "20356",
            "sdk-version": "2",
            "User-Agent": "okhttp/3.10.0.1",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "aweme.snssdk.com",
            "Cookie": f"install_id={iid};",
        }
        if device_token:
            headers['x-tt-dt'] = device_token
        sig = self.get_xgorgon(url, headers=headers, body=urlencode(data))
        headers.update(sig)
        print(headers)
        response = requests.post(url=url, headers=headers, data=data)
        print("搜索", response.text)
        return response.text

    def get_userinfo(self, secUid):
        """
        获取用户信息
        :param secUid:
        :return:
        """
        url = TikTokApi.host + "/dyapi/get_userinfo"
        ts = str(time.time()).split('.')[0]
        sign = self.set_sign
        header = {
            'cid': self.cid,
            'timestamp': ts
        }

        ret = requests.post(url, data={"secUid": secUid, "sign": sign}, headers=header).text
        print("获取用户信息", ret)
        return ret

    def get_comment(self, video_id, device_id, iid, page=None, ttdt=''):
        """
        视频评论
        :param video_id:
        :param device_id:
        :param iid:
        :param page:
        :return:
        """

        if page is None:
            page = '0'

        url = f"https://api3-normal-c.amemv.com/aweme/v2/comment/list/?aweme_id={video_id}" \
              f"&cursor={page}&count=20&insert_ids&address_book_access=2&gps_access=2&forward_page_type=1&channel_id=0" \
              f"&city=360800&hotsoon_filtered_count=0&hotsoon_has_more=0&follower_count=0&is_familiar=0&page_source=0" \
              f"&user_avatar_shrink=64_64&item_type=0&comment_aggregation=0&top_query_word&is_preload=0&channel_ext" \
              f"=%7B%7D&service_id=0&group_id=0&comment_scene=0&hotspot_id&ad_info=&iid=3314355470873225&device_id=4204946618851176&ac=wifi&channel=update&aid=1128&app_name=aweme&version_code=250900&version_name=25.9" \
              f".0&device_platform=android&os=android&ssmix=a&device_type=MI+9&device_brand=Xiaomi&language=zh&os_api" \
              f"=28&os_version=9&openudid={device['data'][0]['openudid']}&manifest_version_code=250901&resolution=900*1600&dpi=320" \
              f"&update_version_code=25909900&_rticket={round(time.time() * 1000)}" \
              f"&package=com.ss.android.ugc.aweme&mcc_mnc=46000&cpu_support64=true&host_abi=arm64-v8a&is_guest_mode" \
              f"=0&app_type=normal&minor_status=0&appTheme=light&need_personal_recommend=1&is_android_pad=0&ts=" \
              f"{round(time.time())}&uuid={device['data'][0]['uuid']}"

        headers = {
            'Host': 'api3-normal-c.amemv.com',
            'passport-sdk-version': '2036851',
            'sdk-version': '2',
            "activity_now_client": str(int(time.time() * 1000)),
            "X-SS-REQ-TICKET": str(int(time.time() * 1000)),
            'x-tt-store-region': 'cn-jx',
            'x-tt-store-region-src': 'did',
            'x-vc-bdturing-sdk-version': '3.6.1.cn',
            'user-agent': 'com.ss.android.ugc.aweme/250901 (Linux; U; Android 9; zh_CN; MI 9; Build/PQ3B.190801.06161913;tt-ok/3.12.13.1)',
            'x-tt-dt': ttdt
        }

        sig = self.get_xgorgon(url, headers=headers)
        headers.update(sig)

        response = requests.get(url, headers=headers).json()
        print("视频评论", response)
        if len(response['comments']) == 0:
            print(url)
        return response

    @property
    def re_channel(self):
        channel = ['wandoujia_aweme_feisuo', 'wandoujia_aweme2', 'tengxun_new', 'douyinw', 'douyin_tengxun_wzl',
                   'aweGW', 'aweme_360', 'aweme_tengxun', 'xiaomi']
        return random.choice(channel)

    def get_web_comment(self, vid, page):
        """
        web版获取评论
        :param vid:
        :param page:
        :return:
        """
        url = ("https://www.douyin.com/aweme/v1/web/comment/list/?device_platform=webapp&aid=6383&channel"
               "=channel_pc_web&aweme_id=" + vid + "&cursor=" + str(page) + "&count=20&item_type=0&insert_ids"
                                                                            "=&whale_cut_token=&cut_version=1&rcFT=&update_version_code=170400&pc_client_type=1&pc_libra_divert"
                                                                            "=Windows&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1920&screen_height"
                                                                            "=1280&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=131.0.0.0"
                                                                            "&browser_online=true&engine_name=Blink&engine_version=131.0.0.0&os_name=Windows&os_version=10"
                                                                            "&cpu_core_num=32&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid"
                                                                            "=7453916638578247208")
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        cookies = "passport_fe_beating_status=false; __ac_nonce=06771a1d900ef26fd2278; __ac_signature=_02B4Z6wo00f01GRE2MgAAIDAU2AcluFdMAhkZNxAAH5ocf; ttwid=1%7CI3GxiWyW785AW7DCf6SBYhsu4iNZ75OMvrSstLjV8yc%7C1735500250%7C30f19f6032017e85c9410612d4facfcf4017dae290ade8ea647d889c09548b64; UIFID_TEMP=c4a29131752d59acb78af076c3dbdd52744118e38e80b4b96439ef1e20799db0c7abc2e9374d96f07f3a7d8674d16acfb6e9730bf895c58fe3d8c6cf745c45409a58ceffdcb5dc3673986e3f28c85523ce641c22b10dc267d4e1f0947571b12923aed9f393ffb50fe5c91cbd3aed3f11; douyin.com; device_web_cpu_core=32; device_web_memory_size=8; architecture=amd64; hevc_supported=true; IsDouyinActive=true; dy_swidth=1920; dy_sheight=1280; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1280%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A32%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; csrf_session_id=24c071b511ed42fa96a6e8cd04eb2ac0; fpk1=U2FsdGVkX19GQ81BXK6wAEuO+SprqBLD5pZz2y+vq7ttClUnqK7y6atcDZo6BGesfoXofPtoTjR5+LrnboxoRw==; fpk2=f51bb482c660d0eeadd1f058058a2b35; s_v_web_id=verify_m5a01ha9_GYTMCJzR_hY1R_4fnw_Aa17_sCR84M5C0GRM; strategyABtestKey=%221735500252.906%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; odin_tt=ad2a1cfbf1e63c54bd62d954bd5340dab00e91d4f89292282d0caa068b321140d2c3f5a3345004aaf439fa368c160f4819d524a40909106fcca10609f7ec032a02c8020331d8949a2063304d5a02d05e; xgplayer_user_id=386822469583; passport_csrf_token=a471f9f509721473e570cc01d6764244; passport_csrf_token_default=a471f9f509721473e570cc01d6764244; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; biz_trace_id=33244ca3; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRmZGK1QvZ2RkZnVSdkdsVmFWRy9lQUw1VlhZRDYrRW4yS3JDaXV6cU56alg4Z3lsTWFHWi8wMVhLbThxN2prM2pCb3gvYk1mZkxBQ2N4enZwaTAxekk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; bd_ticket_guard_client_web_domain=2; home_can_add_dy_2_desktop=%221%22; xg_device_score=7.703177139687378; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e5827292771273f27343035303337353530303632342778; bit_env=r_UNzWYD_mbbOK_GZriMavvvuknstKS8Mku6Vit-EjMctOLk_q4FWeDXkK-6F84fKtsrK0-pIMN8n2QuSjS2iQFfI55yujrqQWqy7rYY3ZhCCJ2WCaNIqMRSrr5BHGroGnKgC0nUpKG2CM8DwmfOPuVjWBjyRTWfqvl7Rmpi4FwheGBir38S-mSd5DthsQUc7jqgZxqO1nDBKr6p1BVLrWr7bTFw25_QkO-JcCMXdEJ6Zq1v5c158UoLElFEPuQn0hdUYmKbFAyiWH0wa5LFSeeQJrldGyU2NigU0VsC1MAHBE3bzZPXQ-uHuiM_Cz311UK7YeM1JyuhcjFkLC-G31tFN_P8SS2leWbsK4qnLH2xqDMEwN8-ZilG0RSAFp-mo3-Lj010EFz3Xj0ogoNrBG-BvQYAi1R86PaqL7CXGGgt7KtDtLYO85ZxMKRBV3qw_cQ0G3jTcjcZLgIJpa72jNA72VbziAg2NYJExOY51a5OvT_URyMSDav20s06gK3P; gulu_source_res=eyJwX2luIjoiNGEyZmE1ZTg5YTg1M2ViNDJiOTRmMzNjODI3MThlYzAyMDdmNDc5ZjdhYTgxNmE5ZjlmZmNjNmI3OGFhZWZmNiJ9; passport_auth_mix_state=hxf6etbkzgig2k1ibbn6r8r5sbdgwjab7qtzh2yykfugl4j0; UIFID=c4a29131752d59acb78af076c3dbdd52744118e38e80b4b96439ef1e20799db0c7abc2e9374d96f07f3a7d8674d16acfb6e9730bf895c58fe3d8c6cf745c45409b8cf27a5b0f76752a28fe5fcdcab0eecb725d57673ad675d5d59b450f53b666150a6e7daeb910fcbaf499546cbb8ed46c5568723bd11137cac59f2d67f0b03d671490e3cf11edf40ef14b90f6ff6e97a279af71f93a5a4a23d4eee1aee45004d099f2fc74abba94d40d6ccb6951e87c13516a4fc81758b68600437aa9a8749c; is_dash_user=1; download_guide=%221%2F20241230%2F0%22"
        headers = {
            'User-Agent': ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://www.douyin.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            'Cookie': cookies
        }
        a_bogus = self.getABogus(url, ua=headers["User-Agent"])
        resp = requests.get(url + "&a_bogus=" + a_bogus['abogus'], headers=headers).text
        print('web评论列表：', resp)
        return resp

    def JuLiangHeaders(self, cookie_str=''):
        return {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://buyin.jinritemai.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://buyin.jinritemai.com/',
            'sec-ch-ua': '"Google Chrome";v="146", "Chromium";v="146", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-storage-access': 'active',
            'cookie': cookie_str,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }

    def JuLiang_BatchLink(self, urls, cookies=None):
        """
        通过链接查询巨量百应商品信息，最大30个链接
        :param cookies:
        :param urls:
        :return:
        """

        headers = self.JuLiangHeaders(cookies)

        params = {
            'urls': urls,
            'scene': '1',
            'verifyFp': 'verify_m3pyuj09_e02851c6_fd50_d7b8_87c0_6d97774e8d52',
            'fp': 'verify_m3pyuj09_e02851c6_fd50_d7b8_87c0_6d97774e8d52',
            'request_from': '203',
            'msToken': 'rde3LdGvoz2yzQsg44ISndxp2uowmjOQq1NfjcVkejAeWrJX4bYxH2Hmha3nKzm_9ZJZfTWvcgCIC79AD3pGS3nmWNIF13AdoUaBI3PQizM5QG5fMV6Ger5sk-XpRKg2Y7svs3LL-1Z_9UbrR6Wwuau2PuP_ZRfQ31TopsP1YWyz'
        }
        a_bogus = self.getABogus(urlencode(params), ua=headers["user-agent"], t="ju")
        params['a_bogus'] = a_bogus['abogus']
        resp = requests.get("https://buyin.jinritemai.com/pc/selection_tool/batch_link", params=params,
                            headers=headers).text
        print("巨量百应商品信息:", resp)
        return resp


    def get_cookie_value(self, cookie_str, key):
        from http.cookies import SimpleCookie
        ck = SimpleCookie()
        ck.load(cookie_str)
        return ck.get(key).value if ck.get(key) else None

    def getMsToken(self, head:dict, msToken='', uuid_str=''):
        url = f'{TikTokApi.host}/dyapi/web/get_msToken'
        ts = str(int(time.time()))
        headers = {
            'cid': self.cid,
            'timestamp': ts,
            'content-type': 'application/json',
        }
        sign = self.set_sign
        params = {
            "sign": sign,
            "msToken": msToken,
            "headers": head,
            "uuid": uuid_str,
        }
        result = requests.post(url, json=params, headers=headers).json()
        print(result)
        return result.get('msToken', '')


    def encryptStrData(self, strData):
        url = f'{TikTokApi.host}/dyapi/web/encryptStrData'
        ts = str(int(time.time()))
        headers = {
            'cid': self.cid,
            'timestamp': ts,
            'content-type': 'application/json',
        }
        sign = self.set_sign
        params = {
            "sign": sign,
            "strData": strData,
        }
        result = requests.post(url, json=params, headers=headers).json()
        # print("encryptStrData", result)
        return result.get('result', '')


    def decryptStrData(self, strData):
        url = f'{TikTokApi.host}/dyapi/web/decryptStrData'
        ts = str(int(time.time()))
        headers = {
            'cid': self.cid,
            'timestamp': ts,
            'content-type': 'application/json',
        }
        sign = self.set_sign
        params = {
            "sign": sign,
            "strData": strData,
        }
        result = requests.post(url, json=params, headers=headers).json()
        # print("decryptStrData", result)
        return result.get('result', '')


    def get_token(self, cookie_str, biz_id):
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?commodity_id={biz_id}&commodity_location=2&id={biz_id}&commodity_location=2&pick_first_source={quote('百应')}&pick_second_source={quote('选品广场')}&pick_third_source=category_recommend&pick_source_id=&recommend_reason_type=&recommend_reason_text=&recall_source=viking_pick_efficient_recalls%3A164%3A-3.56817%2CFIRST%23i2v_search_recalls%3A17%3A-9+%7C+&is_outside_log=1&only_query_params=1&universal_append=1',
            'sec-ch-ua': '"Google Chrome";v="146", "Chromium";v="146", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
            'x-secsdk-csrf-request': '1',
            'x-secsdk-csrf-version': '1.2.22',
            'cookie': cookie_str
        }
        response = tls_requests.head('https://buyin.jinritemai.com/pc/selection/common/btm_mapping', headers=headers, impersonate='chrome146')
        _csrf_token = response.headers.get('x-ware-csrf-token')
        if _csrf_token:
            _csrf_token = _csrf_token.split(',')[1]
        return _csrf_token


    def getShopSku(self, promotion_id:str, userInfo:dict):
        """
        通过商品ID查询商品规格
        Args:
            promotion_id: 商品ID
            userInfo: 登录信息
        Returns:
            商品SKU
        """
        url = f'{TikTokApi.host}/dyapi/web/get_shop_sku'
        ts = str(int(time.time()))
        headers = {
            'cid': self.cid,
            'timestamp': ts,
            'content-type': 'application/json',
        }
        sign = self.set_sign
        user_info = dict(userInfo)
        params = {
            "sign": sign,
            "promotion_id": promotion_id,
            "userinfo": json.dumps(user_info, ensure_ascii=False, separators=(',',':')),
        }
        response = requests.post(url, json=params, headers=headers, timeout=45)
        summary = {'http_status': response.status_code}
        try:
            result = response.json()
            if isinstance(result, dict):
                summary['has_response'] = bool(result.get('response'))
                error = result.get('error')
                if isinstance(error, dict):
                    summary['error'] = {key: error.get(key) for key in
                                        ('code', 'upstream_status', 'sec_code', 'log_id')}
        except ValueError:
            summary['error'] = 'API未返回JSON'
        print("商品SKU", json.dumps(summary, ensure_ascii=False))
        return response.text


    def getShopList(self, shop_id, _page=0, userInfo: dict=None):
        """根据店铺ID获取店铺商品列表
        Args:
            shop_id: 店铺ID
            _page: 翻页游标
            userInfo:
        Returns:
            商品列表
        """
        if not userInfo:
            print("请先登录")
            return
        cookie_str = userInfo.get('cookie', '')
        _msToken = userInfo.get('msToken', '')

        fp = self.get_cookie_value(cookie_str, 's_v_web_id')
        params = {
            'seraph_did': '',
            'verifyFp': fp,
            'fp': fp,
            'msToken': _msToken,
        }

        body = {
            'scene': 'PCShopDetailFeed',
            'cursor': _page,
            'size': 10,
            'extra': {
                'shop_id': shop_id,
            },
            'filters': {},
        }
        headers = self.JuLiangHeaders(cookie_str)
        headers['content-type'] = 'application/json'
        json_data = json.dumps(body, separators=(',', ':'))
        url = f'https://buyin.jinritemai.com/pc/selection/common/material_list?{urlencode(params)}'
        a_bogus = self.getABogus(url, ua=headers["user-agent"], data=json_data, t='ju')
        # print(a_bogus)
        url += "&a_bogus=" + a_bogus['abogus']
        response = tls_requests.post(url, headers=headers, data=json_data, impersonate='chrome146').text
        print("店铺商品列表", response)
        return response

    def JuLiang_ShopInfo(self, promotion_id, userinfo:dict, sale: bool = False):
        """
        通过商品ID查询商品详情
        Args:
            promotion_id: 商品ID
            userinfo: 登录信息
            sale: 是否获取销量，默认否获取商品详情
        Returns:
            商品SKU
        """
        url = f'{TikTokApi.host}/dyapi/web/get_shop_info'
        ts = str(int(time.time()))
        headers = {
            'cid': self.cid,
            'timestamp': ts,
            'content-type': 'application/json',
        }
        sign = self.set_sign
        params = {
            "sign": sign,
            "promotion_id": promotion_id,
            "userinfo": json.dumps(userinfo, ensure_ascii=False, separators=(',',':')),
            "sale": sale,
        }
        response = requests.post(url, json=params, headers=headers).text
        print(f"商品{"销量信息" if sale else "详情信息"}", response)
        return response


    def JuLiang_material_list(self, pg=0):
        """巨量选品广场
        :param pg: 第一页0，下一页+30
        """
        tempCookie = 's_v_web_id=verify_mh25cqr0_kFrExpAc_pQTY_4y0s_8cLd_DrxNMCvmDdGk; qc_tt_tag=0; passport_csrf_token=fc8f6b07421ae775d95641ab829a5fbf; passport_csrf_token_default=fc8f6b07421ae775d95641ab829a5fbf; is_staff_user=false; gfkadpd=2631,22740; _tea_utm_cache_3813=undefined; scmVer=1.0.1.9453; ttwid=1%7Ckimy0lj6g3kkGnScZio9_HcjxwaCUkUSVYLufFm4Prw%7C1762937264%7C9a29ae9e6f916bdf2f08d6202abdfee5e130e7b2704b3f4a6153a8c1dc10a63e; odin_tt=ca0a788e3e7e38c0d879011854118401d2163725b9136bcdfa07e6c65ea14b56426fb107939d2435d7048b2b9d5373f506479518969e6c7ea787f680c1b1e7d0; passport_auth_status=2bcb324c11f18e09eb57307b4ae678d4%2C7b6b24a8f63a79f3c37037bd7e18bda1; passport_auth_status_ss=2bcb324c11f18e09eb57307b4ae678d4%2C7b6b24a8f63a79f3c37037bd7e18bda1; uid_tt=78ab528d86d52c455b3d62365bab3369; uid_tt_ss=78ab528d86d52c455b3d62365bab3369; sid_tt=2c9936e6b3b043fb37e4815e670048eb; sessionid=2c9936e6b3b043fb37e4815e670048eb; sessionid_ss=2c9936e6b3b043fb37e4815e670048eb; ucas_c0_buyin=CkEKBTEuMC4wELSIkp7ztZKKaRi9LyDJ6eCg1cypBiiPETD60OCg1cztAkCzk9HIBkizx43LBlC_vK-goPKusWZYfhIUFGSdUaI05OZMOBdK6mtby7CwWds; ucas_c0_ss_buyin=CkEKBTEuMC4wELSIkp7ztZKKaRi9LyDJ6eCg1cypBiiPETD60OCg1cztAkCzk9HIBkizx43LBlC_vK-goPKusWZYfhIUFGSdUaI05OZMOBdK6mtby7CwWds; sid_guard=2c9936e6b3b043fb37e4815e670048eb%7C1762937267%7C5184000%7CSun%2C+11-Jan-2026+08%3A47%3A47+GMT; session_tlb_tag=sttt%7C15%7CLJk25rOwQ_s35IFeZwBI6__________WPmlm2ti-8YxUGw_C4wesmZvavwTXx4Zo8axIs03OjSU%3D; session_tlb_tag_bk=sttt%7C15%7CLJk25rOwQ_s35IFeZwBI6__________WPmlm2ti-8YxUGw_C4wesmZvavwTXx4Zo8axIs03OjSU%3D; sid_ucp_v1=1.0.0-KGIyYTVjMzFkOGQxZjA0MjYxNGQwZDE4MmRkYWZmNzRjMWVhODQxZWYKGAj60OCg1cztAhCzk9HIBhiPESAMOAhAJhoCbHEiIDJjOTkzNmU2YjNiMDQzZmIzN2U0ODE1ZTY3MDA0OGVi; ssid_ucp_v1=1.0.0-KGIyYTVjMzFkOGQxZjA0MjYxNGQwZDE4MmRkYWZmNzRjMWVhODQxZWYKGAj60OCg1cztAhCzk9HIBhiPESAMOAhAJhoCbHEiIDJjOTkzNmU2YjNiMDQzZmIzN2U0ODE1ZTY3MDA0OGVi; SASID=SID2_7571756393511928115; BUYIN_SASID=SID2_7571756393511928115; buyin_shop_type=24; buyin_account_child_type=1128; buyin_app_id=1128; buyin_shop_type_v2=24; buyin_account_child_type_v2=1128; buyin_app_id_v2=1128; csrf_session_id=a4e7bae06169f1f189dcb4cf508fe1fd'
        fp = re.search(r's_v_web_id=(.*?);', tempCookie) or ''
        if fp:
            fp = fp.group(1)
        url = f'https://buyin.jinritemai.com/pc/selection/common/material_list?ewid=b3cc81f1ab7841d91579571fee82d6f5&verifyFp={fp}&fp={fp}&msToken=OoQTZmTPhVZmg9M_ke_FOEUOwlHlz6qrrd0sZSQmzFUusEEmIS3tXF9l-vtku-2g_nn7cYKKPvhPH1cnXwz47KuRSgWUKWSjeNlXN73FA6uvTqOrphG98jij7FsOWI3l8iqSEIqqejIB7NG4rshAa8CcqnoqZVo8I9cJQqrb9Njfi5KrAgB8bmQ%3D'
        body = {
            'scene': 'PCSquareFeed',
            'size': 30,
            'search_text': '',
            'cursor': pg,
            'extra': {
                'new_session_strategy': '1',
                'search_id': '2240ef2d8a855155c5a83bb0482ffccf197cd99dd99017347d914442b8d79bf111678ffe7c7db548e1de57831c17e1a5030019891130cf3908aad7b4d90691c0b575106cf5b10f6e5986770134c70f51',
                'session_id': '2240ef2d8a855155c5a83bb0482ffccf197cd99dd99017347d914442b8d79bf111678ffe7c7db548e1de57831c17e1a5030019891130cf3908aad7b4d90691c0b575106cf5b10f6e5986770134c70f51',
                'use_kol_product': '1',
            },
            'filters': {
                'FeaturedItems': {
                    'value': [
                        'is_first_onshelf_prod_30d',
                    ],
                },
            },
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://buyin.jinritemai.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://buyin.jinritemai.com/dashboard/merch-picking-library',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'cookie': tempCookie,
        }

        json_data = json.dumps(body, separators=(',', ':'))
        a_bogus = self.getABogus(url, ua=headers["user-agent"], t="ju", data=json_data)
        url += "&a_bogus=" + a_bogus['abogus']
        response = requests.post(url, headers=headers, data=json_data).text
        print("response2", response)
        return response


    def get_old_comment(self, vid, page):
        """
        旧版获取视频评论
        :param vid:
        :param page:
        :return:
        """
        url = TikTokApi.host + '/dyapi/get_comment'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            "Accept-Encoding": "gzip"
        }
        sign = self.set_sign

        resp = requests.post(url, data={'sign': sign, "aweme_id": vid, "page": page}, headers=header).content
        print("旧版视频评论", gzip.decompress(resp).decode('utf-8'))
        return resp

    def get_web_promotions(self, room_id, uid, web_rid, page=0):
        """
        web版获取小黄车商品
        :param room_id:
        :param uid:
        :param web_rid:
        :param page:
        :return:
        """

        url = (f'https://live.douyin.com/live/promotions/page/?device_platform=webapp&aid=6383&channel=channel_pc_web'
               f'&room_id={room_id}&author_id={uid}&offset={page}&limit=20&pc_client_type=1&version_code'
               f'=210800&version_name=21.8.0&cookie_enabled=True&screen_width=1920&screen_height=1280&browser_language=zh'
               f'-CN&browser_platform=Win32&browser_name=Chrome&browser_version=124.0.0.0&browser_online=True&engine_name'
               f'=Blink&engine_version=124.0.0.0&os_name=Windows&os_version=10&cpu_core_num=32&device_memory=8&platform'
               f'=PC&downlink=10&effective_type=4g&round_trip_time=50')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": f"https://live.douyin.com/{web_rid}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            # "X-Secsdk-Csrf-Token": "",
            'Cookie': "passport_csrf_token=641cfdedf1ebf458cc1fca45e5e9e7f3; passport_csrf_token_default=641cfdedf1ebf458cc1fca45e5e9e7f3; ttwid=1%7CcPFTqVvnTz3G--ULEqniVlAaegbrW6NERNmAHrzn1Jc%7C1714293851%7C709fd473905e48b204e824f591ceaf02d3c333c728f269e143f5bb9e20313b75; strategyABtestKey=%221714293853.364%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.4%7D; bd_ticket_guard_client_web_domain=2; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1280%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A32%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.95%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; home_can_add_dy_2_desktop=%221%22; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; __ac_nonce=0662e7e69009b12f3818b; __ac_signature=_02B4Z6wo00f01QUnOowAAIDADwHhJ5g.3TkFBz4AACdqR8wihe3iu0VRHEkVfzI4nuRVeRKwKc7hjWNB9X9LhNVh6sHue4OWm7xuWY2YjY5E2WImsUldVWq9tHdVDkhvMs.s7hAnRXzhwK8D03; __live_version__=%221.1.1.9930%22; has_avx2=null; device_web_cpu_core=32; device_web_memory_size=8; live_use_vvc=%22false%22; xgplayer_user_id=829993556135; csrf_session_id=797f27d7bc861694e3643f98bbb5859a; WallpaperGuide=%7B%22showTime%22%3A1714323055480%2C%22closeTime%22%3A0%2C%22showCount%22%3A1%2C%22cursor1%22%3A7%2C%22cursor2%22%3A0%7D; download_guide=%223%2F20240429%2F0%22; pwa2=%220%7C0%7C3%7C0%22; webcast_leading_last_show_time=1714323221901; webcast_leading_total_show_times=1; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; d_ticket=46803d9f253accb32a5488d82e8138eb9f031; s_v_web_id=verify_lvjs6961_tiJfsPPC_AU8C_4fms_AcsO_kDJkyLN9aRt4; passport_assist_user=CkGb4GVxkjuwkpFXFhwLrpbB2AAQjedx_9tL10jzEhZ8YtLE0fn7L_FrzFVtBGZS2vhUA9yLZtUDmjY1rphnImwXCRpKCjwTpW8do0Duhsy0zqcnA9IygN1gYml576dIKXE2lJ4JOZTxtHvpchrSXoBEpFiSBga_3BSAW3ntNLExYWIQmvLPDRiJr9ZUIAEiAQM7xhCq; n_mh=EyEgyFxFI5fiy-d_iT660NAbFEw22sfOXLkhKXhtwCs; sso_uid_tt=1ce7f556d74bf6de02373e308380996a; sso_uid_tt_ss=1ce7f556d74bf6de02373e308380996a; toutiao_sso_user=1e25178e8ae1547eb34fb9284832e377; toutiao_sso_user_ss=1e25178e8ae1547eb34fb9284832e377; sid_ucp_sso_v1=1.0.0-KDdhOTRkM2ZkNjIzN2U4N2I2MDAwMGFmZDViMGIzYWNiNzUyOWY1NmEKHwj4ueCXiPTvAhClg7qxBhjvMSAMMK3goPgFOAZA9AcaAmxmIiAxZTI1MTc4ZThhZTE1NDdlYjM0ZmI5Mjg0ODMyZTM3Nw; ssid_ucp_sso_v1=1.0.0-KDdhOTRkM2ZkNjIzN2U4N2I2MDAwMGFmZDViMGIzYWNiNzUyOWY1NmEKHwj4ueCXiPTvAhClg7qxBhjvMSAMMK3goPgFOAZA9AcaAmxmIiAxZTI1MTc4ZThhZTE1NDdlYjM0ZmI5Mjg0ODMyZTM3Nw; passport_auth_status=ce2f8dc1259a16ba8facd886fe15730a%2C; passport_auth_status_ss=ce2f8dc1259a16ba8facd886fe15730a%2C; uid_tt=cea0c22385450511db8db12af3025431; uid_tt_ss=cea0c22385450511db8db12af3025431; sid_tt=cc78d1dc2dc8a871ce111cbcbf008ee2; sessionid=cc78d1dc2dc8a871ce111cbcbf008ee2; sessionid_ss=cc78d1dc2dc8a871ce111cbcbf008ee2; xg_device_score=7.681574142025062; live_can_add_dy_2_desktop=%221%22; passport_fe_beating_status=true; IsDouyinActive=true; publish_badge_show_info=%220%2C0%2C0%2C1714323881762%22; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=a8b1e34e660790c54d33a982134815c8; __security_server_data_status=1; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRmZGK1QvZ2RkZnVSdkdsVmFWRy9lQUw1VlhZRDYrRW4yS3JDaXV6cU56alg4Z3lsTWFHWi8wMVhLbThxN2prM2pCb3gvYk1mZkxBQ2N4enZwaTAxekk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; sid_guard=cc78d1dc2dc8a871ce111cbcbf008ee2%7C1714323882%7C5183998%7CThu%2C+27-Jun-2024+17%3A04%3A40+GMT; sid_ucp_v1=1.0.0-KGIzNmQwNTE4NmEyYzhiNTdmZjVlYjFkNmIzZDM4YWIwMGE3Y2ZiYjMKGwj4ueCXiPTvAhCqg7qxBhjvMSAMOAZA9AdIBBoCbGYiIGNjNzhkMWRjMmRjOGE4NzFjZTExMWNiY2JmMDA4ZWUy; ssid_ucp_v1=1.0.0-KGIzNmQwNTE4NmEyYzhiNTdmZjVlYjFkNmIzZDM4YWIwMGE3Y2ZiYjMKGwj4ueCXiPTvAhCqg7qxBhjvMSAMOAZA9AdIBBoCbGYiIGNjNzhkMWRjMmRjOGE4NzFjZTExMWNiY2JmMDA4ZWUy; odin_tt=6916a56924b3ce114aec5bff8c0ffe669ab8847ce29ffe5959d6401d10324ce1851e0eb8497f65bee94e85eeccc4c244; msToken=d92VZSUMy-usoybxwoZ81ZmFbdHj5I4lxnSnacj1mx11mR5z78XSScf6-0Ujf2a2LAz0sAnYY-0kCuM5T3H5IhBTNzfEMcuG4FNRf2oGQpMK1uCzeA=="
        }
        abogus = self.getABogus(url, headers["User-Agent"], headers["Cookie"])
        resp = requests.post(url + "&a_bogus=" + abogus['abogus'], headers=headers).text
        print('小黄车商品：', resp)
        return resp

    def get_video(self, secUid, page="0", iid='', device_id='', device_token=''):
        """
        获取作品列表
        :param secUid:
        :param page:
        :param iid:
        :param device_id:
        :return:
        """

        url = f"https://api3-normal-c.amemv.com/aweme/v1/aweme/post/?publish_video_strategy_type=2&source=0" \
              f"&user_avatar_shrink=96_96&video_cover_shrink=248_330&need_time_list=0&max_cursor={page}&sec_user_id" \
              f"={secUid}&count=20&show_live_replay_strategy=1" \
              f"&is_order_flow=0&page_from=2&location_permission=0&familiar_collects=0&page_scene=1" \
              f"&post_serial_strategy=0&need_article=1&_rticket={round(time.time() * 1000)}" \
              f"&mcc_mnc=46000&need_personal_recommend=1&ts={round(time.time())}&ac=wifi&aid=1128&appTheme=light" \
              f"&app_name=aweme&app_type=normal&channel=update&cpu_support64=true&device_brand=Xiaomi&device_id" \
              f"={device_id}&device_platform=android&device_type=MI+9&dpi=320&host_abi=arm64-v8a&iid" \
              f"={iid}&is_android_pad=0&is_guest_mode=0&language=zh&manifest_version_code=250901" \
              f"&minor_status=0&os=android&os_api=28&os_version=9&package=com.ss.android.ugc.aweme&resolution=900" \
              f"*1600&ssmix=a&update_version_code=25909900&version_code=250900&version_name=25.9.0"

        headers = {
            'Host': 'api3-normal-c.amemv.com',
            'Accept-Encoding': 'gzip',
            'passport-sdk-version': '2036851',
            'sdk-version': '2',
            'ttzip-version': '32782',
            'X-SS-DP': '1128',
            "activity_now_client": str(int(time.time() * 1000)),
            "X-SS-REQ-TICKET": str(int(time.time() * 1000)),
            'x-tt-request-tag': 's=0;p=0',
            'x-tt-store-region': 'cn-jx',
            'x-tt-store-region-src': 'did',
            'x-vc-bdturing-sdk-version': '3.6.1.cn',
            'user-agent': 'com.ss.android.ugc.aweme/250901 (Linux; U; Android 9; zh_CN; MI 9; Build/PQ3B.190801.06161913;tt-ok/3.12.13.1)',
            # 'x-tt-dt': ttdt,
            "X-Tt-Token": "0090e9070d88238e42336c3de32b0d9fab01d15b38e73d369d56440ae12f40059a673893d4b954ece8b30836b42f44e7e81e36019a313b94e6fc9f88df7ddbf6aa25dae2ecccfed26583b2a6ce6f16bc8c4ba95706a349e936ba62b6591e233330cbd-1.0.1"
        }

        if device_token:
            headers['x-tt-dt'] = device_token
        sig = self.get_xgorgon(url, headers=headers)
        headers.update(sig)
        response = requests.get(url, headers=headers)
        print("作品列表", response.text)
        # if len(response.json()['aweme_list']) == 0:
        #     print(url)
        return response

    def encode_mobile(self, mobile):
        url = TikTokApi.host + '/dyapi/mobile'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign, 'mobile': mobile}, headers=header).json()
        return resp


    def encode_source_info(self, data):
        url = TikTokApi.host + '/dyapi/web/encode_source_info'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign, 'data': data}, headers=header).json()
        return resp


    def getVerifyFp(self):
        url = TikTokApi.host + '/dyapi/web/getVerifyFp'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign}, headers=header).json()
        return resp


    def fingerprint(
        self,
        data:dict=None,
        uuid_str='',
        fingerprint_seed=65522,  #修改id变化全套指纹，同个账号必须使用相同id得到同一套指纹
        referer='https://buyin.jinritemai.com/mpa/account/login?log_out=1&type=24',
        user_agent=None
    ):
        url = TikTokApi.host + '/dyapi/web/fingerprint'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        if not data:
            data = {
                'app': 'fangxingou',
                'context': {
                    'ttwid': '',
                    'seraph_did': '',
                    'pid': '/mpa/account/login'
                },
                '_token': ''
            }
        sign = self.set_sign
        body = {
            'sign': sign,
            'data': json.dumps(data, separators=(',',':')),
            'uuid': uuid_str,
            'fingerprint_seed': fingerprint_seed,
            'referer': referer,
            # 'url': referer,
            'user_agent': user_agent or '',
        }
        resp = tls_requests.post(url, data=body, headers=header, impersonate='chrome146').json()
        return resp


    def encrypt_login_body(self, _token, _data):
        url = TikTokApi.host + '/dyapi/web/encrypt_login_body'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign, 'token': _token, 'body': _data}, headers=header).json()
        return resp


    def get_ac_sign(self, ac_nonce):
        """
        ac_sign
        :param ac_nonce:
        :return:
        """
        url = TikTokApi.host + '/dyapi/web/ac_sign'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'User-Agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign, 'ac_nonce': ac_nonce}, headers=header).text
        print('ac_sign:', resp)
        return resp

    def get_video_info(self, video: list) -> str:
        """
        测试获取视频信息接口
        :param video: 视频列表
        :return:
        """
        url = TikTokApi.host + '/dyapi/video_info'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        resp = requests.post(url, data={'video_list': str(video), 'sign': sign}, headers=header).text
        # resp = gzip.decompress(byte).decode('utf-8')
        print('视频信息列表:', resp)
        return resp

    def get_cookie(self):
        header = {
            'Referer': 'https://www.douyin.com/',
            'x-tt-passport-csrf-token': '',
            'User-Agent': self.__web_ua
        }
        ret = requests.get('https://www.douyin.com/', headers=header)
        cookie_1 = requests.utils.dict_from_cookiejar(ret.cookies)
        # print('得到最初cookie', cookie_1)
        url = 'https://sso.douyin.com/get_qrcode/?service=https%3A%2F%2Fwww.douyin.com%2F&need_logo=false&aid=6383'
        header['Cookie'] = urlencode(cookie_1)
        ret = requests.get(url, headers=header)
        cookie_2 = requests.utils.dict_from_cookiejar(ret.cookies)
        # print('得到token', cookie_2)
        cookies = dict()
        cookies.update(cookie_1)
        cookies.update(cookie_2)
        print('cookie合并后', cookies)
        return cookies

    def get_web_cookie(self):
        """
        获取滑块后的cookie
        :return:
        """
        url = TikTokApi.host + '/dyapi/get_cookie/v2'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign}, headers=header).json()
        print(resp)
        return resp['data'][0]['cookie']

    def get_room_info(self, _url):
        """
        网页直播链接获取直播id
        :param _url:
        :return:
        """
        url = TikTokApi.host + '/dyapi/web/room_info'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        resp = requests.post(url, data={'sign': sign, 'url': _url}, headers=header).json()
        print('获取直播信息', resp)
        return resp

    @property
    def set_sign(self):
        """
        :return:
        """
        ts = str(time.time()).split('.')[0]
        string = '1005' + self.cid + ts + self.__AppKey
        sign = hashlib.md5(string.encode('utf8')).hexdigest()
        # print('本api的sign', sign)
        return sign

    def get_video_list(self, uid, page=None):
        """
        获取作品列表
        :param uid:
        :param page:
        :return:
        """
        if page is None:
            page = '0'

        uri = TikTokApi.host + '/dyapi/get_video_list'
        ts = str(time.time()).split('.')[0]
        sign = self.set_sign
        data = {"uid": uid, "page": page, "sign": sign}
        headers = {
            'cid': self.cid,
            'timestamp': ts,
            "Accept-Encoding": "gzip"
        }
        ret = requests.post(uri, data=data, headers=headers).content
        print("作品列表", gzip.decompress(ret).decode('utf-8'))
        return ret

    def getBd(self, privateKey=None, cert=None, salt=None, t=None):
        """
        生成bd_ticket_guard_client_data 不传参为cookieBD 传参则计算req_sign,(若t=sendMessage则计算reuqest_sign)
        :param privateKey: 私钥 不传参时生成
        :param cert: X509证书 '/passport/ticket_guard/'获取
        :param salt: 加密值例如：ticket=xxx&path=xxx&timestamp=xxx
        :param t: 类型
        :return:
        """
        uri = TikTokApi.host + '/dyapi/web/bd'
        ts = str(time.time()).split('.')[0]
        sign = self.set_sign
        data = {"privateKey": privateKey, "cert": cert, "salt": salt, "sign": sign, "t": t}
        headers = {
            'cid': self.cid,
            'timestamp': ts
        }
        result = requests.post(uri, data=data, headers=headers).text
        print("bd_ticket_guard_client_data", result)
        return result

    def live_relation(self, sec_user_id, liveUrl):
        """
        关注直播间主播
        :param sec_user_id: 你的sec_uid
        :param liveUrl: 主播的直播间链接，必需短链，例：https://v.douyin.com/zMxdyDqkKO4/
        :return:
        """
        res = self.get_room_info(liveUrl)
        room_id = res['data']['room']['id_str']
        uid = res['data']['room']['owner_user_id']
        sec_to_user_id = res['data']['room']['owner']['sec_uid']
        web_rid = res['data']['room']['owner']['web_rid']
        status = res['data']['room']['status']
        st = "正在直播" if status == 2 else "下播了"
        print(st)
        print('sec_uid', sec_to_user_id)
        print('room_id', room_id)
        print('uid', uid)
        print('web_rid', web_rid)

        s_sdk_server_cert_key = {
            "cert": "-----BEGIN CERTIFICATE-----\nMIIEfTCCBCKgAwIBAgIUXWdS2tzmSoewCWfKFyiWMrJqs/0wCgYIKoZIzj0EAwIw\nMTELMAkGA1UEBhMCQ04xIjAgBgNVBAMMGXRpY2tldF9ndWFyZF9jYV9lY2RzYV8y\nNTYwIBcNMjIxMTE4MDUyMDA2WhgPMjA2OTEyMzExNjAwMDBaMCQxCzAJBgNVBAYT\nAkNOMRUwEwYDVQQDEwxlY2llcy1zZXJ2ZXIwWTATBgcqhkjOPQIBBggqhkjOPQMB\nBwNCAASE2llDPlfc8Rq+5J5HXhg4edFjPnCF3Ua7JBoiE/foP9m7L5ELIcvxCgEx\naRCHbQ8kCCK/ArZ4FX/qCobZAkToo4IDITCCAx0wDgYDVR0PAQH/BAQDAgWgMDEG\nA1UdJQQqMCgGCCsGAQUFBwMBBggrBgEFBQcDAgYIKwYBBQUHAwMGCCsGAQUFBwME\nMCkGA1UdDgQiBCABydxqGrVEHhtkCWTb/vicGpDZPFPDxv82wiuywUlkBDArBgNV\nHSMEJDAigCAypWfqjmRIEo3MTk1Ae3MUm0dtU3qk0YDXeZSXeyJHgzCCAZQGCCsG\nAQUFBwEBBIIBhjCCAYIwRgYIKwYBBQUHMAGGOmh0dHA6Ly9uZXh1cy1wcm9kdWN0\naW9uLmJ5dGVkYW5jZS5jb20vYXBpL2NlcnRpZmljYXRlL29jc3AwRgYIKwYBBQUH\nMAGGOmh0dHA6Ly9uZXh1cy1wcm9kdWN0aW9uLmJ5dGVkYW5jZS5uZXQvYXBpL2Nl\ncnRpZmljYXRlL29jc3AwdwYIKwYBBQUHMAKGa2h0dHA6Ly9uZXh1cy1wcm9kdWN0\naW9uLmJ5dGVkYW5jZS5jb20vYXBpL2NlcnRpZmljYXRlL2Rvd25sb2FkLzQ4RjlD\nMEU3QjBDNUE3MDVCOTgyQkU1NTE3MDVGNjQ1QzhDODc4QTguY3J0MHcGCCsGAQUF\nBzAChmtodHRwOi8vbmV4dXMtcHJvZHVjdGlvbi5ieXRlZGFuY2UubmV0L2FwaS9j\nZXJ0aWZpY2F0ZS9kb3dubG9hZC80OEY5QzBFN0IwQzVBNzA1Qjk4MkJFNTUxNzA1\nRjY0NUM4Qzg3OEE4LmNydDCB5wYDVR0fBIHfMIHcMGygaqBohmZodHRwOi8vbmV4\ndXMtcHJvZHVjdGlvbi5ieXRlZGFuY2UuY29tL2FwaS9jZXJ0aWZpY2F0ZS9jcmwv\nNDhGOUMwRTdCMEM1QTcwNUI5ODJCRTU1MTcwNUY2NDVDOEM4NzhBOC5jcmwwbKBq\noGiGZmh0dHA6Ly9uZXh1cy1wcm9kdWN0aW9uLmJ5dGVkYW5jZS5uZXQvYXBpL2Nl\ncnRpZmljYXRlL2NybC80OEY5QzBFN0IwQzVBNzA1Qjk4MkJFNTUxNzA1RjY0NUM4\nQzg3OEE4LmNybDAKBggqhkjOPQQDAgNJADBGAiEAqMjT5ADMdGMeaImoJK4J9jzE\nLqZ573rNjsT3k14pK50CIQCLpWHVKWi71qqqrMjiSDvUhpyO1DpTPRHlavPRuaNm\nww==\n-----END CERTIFICATE-----",
            "sn": "533240336124694022040808462028007165443034493949", "createdTime": 1759049515473}
        str_web_protect = '{\"ticket\":\"hash.hOatW84yO4fhgMTU0hbLFc2Yls0n8XniBFL4vLEt2kE=\",\"ts_sign\":\"ts.2.d6320d9c3d88e3f3566a51fadeed5b925b50695a5a4f882c718628d9b7503311c4fbe87d2319cf05318624ceda14911ca406dedbebeddb2e30fce8d4fa02575d\",\"client_cert\":\"pub.BLEbbzThHElN7vK4PUjP76tBbfVOg+Gejh+rhKDXgzGlK9ALUXO7S8eK4dcKIGI2VtRk7whaKnyJ1vjc7jnmVG0=\",\"log_id\":\"20250927235036D682C411CCF8792D57E2\",\"create_time\":1758988236}'
        web_protect = json.loads(str_web_protect)
        cookies = {
            '__security_mc_1_s_sdk_crypt_sdk': '10f60dac-4180-9574',
            'passport_csrf_token': 'e0f3ddde0425c2b56e1a410ecf1186d3',
            'passport_csrf_token_default': 'e0f3ddde0425c2b56e1a410ecf1186d3',
            'n_mh': 'Wisfoo0O9_c_vt5Pvmn_dck6ztjKlVJyMrJZNmrgyQk',
            'is_staff_user': 'false',
            '__security_mc_1_s_sdk_cert_key': '5546f017-44e3-9f40',
            'enter_pc_once': '1',
            'UIFID_TEMP': '7b2f39d240dea4bf45abce07b021cb7f3b689a513c5a348a4b7d4e9669b5127e0c00292362fd799a450b0eaa41be141a2fe7d01fa2fd9e927f84512464934bb8ca88562169438e4fa79d5a40ef91e015',
            's_v_web_id': 'verify_mg1xe87z_kz2BWvHi_mwIK_454Q_B7vp_Ttf0592cfpVU',
            'dy_swidth': '1920',
            'dy_sheight': '1080',
            'my_rd': '2',
            'bd_ticket_guard_client_web_domain': '2',
            'fpk1': 'U2FsdGVkX19KSBJPXHq7Z5czGL3SEq1UZM3pZY4CV7jrLgIIER+iiv4Co1dCBCASlpEBzuGTJrHG5pBRWBiB2w==',
            'fpk2': 'acff52a1652901ae7e446fb41b9189b7',
            'publish_badge_show_info': '%220%2C0%2C0%2C1758956691410%22',
            'passport_assist_user': 'CkEKrScs19JrG2wa7RxS6QHPGJGsWBlwFWFxSZOpUh7DKrcbqOErUMjW-k1ojYR6asdh0W3XS_RZ7w8dTDIix2Xy0xpKCjwAAAAAAAAAAAAAT4YN7P9TABjLoLDH8KH0B6CJZbpSzRe7Qybk5d-07QF1jhHBTzthwlTfUnw_NgDUnHAQi6b9DRiJr9ZUIAEiAQMI2tCe',
            'uid_tt': 'cf602aeb29084e6e66721fc653d270ad',
            'uid_tt_ss': 'cf602aeb29084e6e66721fc653d270ad',
            'sid_tt': '9a883dd5c2fb7915cc24c3e500c83715',
            'sessionid': '9a883dd5c2fb7915cc24c3e500c83715',
            'sessionid_ss': '9a883dd5c2fb7915cc24c3e500c83715',
            'UIFID': '7b2f39d240dea4bf45abce07b021cb7f3b689a513c5a348a4b7d4e9669b5127e0c00292362fd799a450b0eaa41be141ad021c7d23f9461a743ff1bee6abcaf499c9caed90b4dc28627ad2976bb20277ee458c11398c1f05f00fb5a85da423f3189715846157c067f2feb5fd3c9db6348658b2c979be7687b90c753eb39c1c104adf102947a63943382dd2aa5aa53a592b0896d6c5ea4c02abe92ca2968c12dbb',
            'SelfTabRedDotControl': '%5B%5D',
            'hevc_supported': 'true',
            'passport_mfa_token': 'Cjdcp6Co%2FRlDL5dWzte5JPnVxAee17DrafPsmDUYF2v4sAzNautHjHLXO4axzrG%2BAnOANx6FbNytGkoKPAAAAAAAAAAAAABPhourlxupjVX8HODNmohyp16I9%2Bg8OU%2Bs9iV6jzEUK659nnPlG0O3IrYkPLUN%2FHEjhBCXqf0NGPax0WwgAiIBA%2FltMSg%3D',
            'd_ticket': '820c4c53dd2b51106180e9e93d4cbe35c739e',
            'sid_guard': '9a883dd5c2fb7915cc24c3e500c83715%7C1758988236%7C5152462%7CWed%2C+26-Nov-2025+07%3A04%3A58+GMT',
            'sid_ucp_v1': '1.0.0-KDUyZmQ5OTZmMGNhZThkZjE4NmJlMGE4NWYwMWRjNTM2MjFhZTZjZTkKIQjYr7CL7fX-BRDMj-DGBhjOPSAMMJ6vtO8FOAdA9AdIBBoCaGwiIDlhODgzZGQ1YzJmYjc5MTVjYzI0YzNlNTAwYzgzNzE1',
            'ssid_ucp_v1': '1.0.0-KDUyZmQ5OTZmMGNhZThkZjE4NmJlMGE4NWYwMWRjNTM2MjFhZTZjZTkKIQjYr7CL7fX-BRDMj-DGBhjOPSAMMJ6vtO8FOAdA9AdIBBoCaGwiIDlhODgzZGQ1YzJmYjc5MTVjYzI0YzNlNTAwYzgzNzE1',
            '_bd_ticket_crypt_doamin': '2',
            '_bd_ticket_crypt_cookie': '4a351d30953f980971f67712b9b850f4',
            '__security_mc_1_s_sdk_sign_data_key_web_protect': 'caceb258-4790-b317',
            '__security_server_data_status': '1',
            'is_dash_user': '1',
            'strategyABtestKey': '%221758988800.846%22',
            'download_guide': '%223%2F20250928%2F0%22',
            '__live_version__': '%221.1.4.539%22',
            'live_use_vvc': '%22false%22',
            'live_can_add_dy_2_desktop': '%220%22',
            'volume_info': '%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.01%7D',
            'totalRecommendGuideTagCount': '32',
            'playRecommendGuideTagCount': '0',
            'WallpaperGuide': '%7B%22showTime%22%3A1758988277960%2C%22closeTime%22%3A0%2C%22showCount%22%3A1%2C%22cursor1%22%3A32%2C%22cursor2%22%3A18%2C%22hoverTime%22%3A1758988745855%7D',
            '__ac_signature': '_02B4Z6wo00f01lJ.J-AAAIDDMXXniMu4ZkpSXyNAAPxWb5',
            '__ac_nonce': '068d91a5800bf6d3e294a',
            'session_tlb_tag': 'sttt%7C13%7Cmog91cL7eRXMJMPlAMg3Ff________-nnt3LfIb-U8M5o1OhrJ-ierYU4sNKJxDIvwmRV2NWn0E%3D',
            'sdk_source_info': '7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f27313c343731333d30353c303234272927676c715a75776a716a666a69273f2763646976602778',
            'bit_env': 'c6fqfCClCl-3J5LFOL4cBpHEPOBeYelfbDs9o_nf_mgLjjnj1bK8SiJ13figkPLPvRvD7joTZbpVKCPqCZuzRhw-AC_9dTn0kzEYzHAiUY-sTc7Zno5vS9_Gh96AsjiPy6Ck4Mqif3cFqLV-NGIutATJhaDMmaeK-BerajKaShv2hMInJUG-wKqO3UL_kupLjeej9exI2VUqyI9Ec7Qz4fywqyG0X1KlMZVi8LYtgBr9-wAtTgKTEkZcxku5R1bD49Fm2juhj0OOYNCDFwCYnGLGTS82hMl4SiZlpxB9W76zFftNC_m0Rk0l8X-V0z1BQ1Vr6an36ZuOHvdIZytqKhdoJMEz6qWpUe8BlvCVynvtsxFIBKDLnIVp40YOCqy9ooiUOBdZ4eRT4UF0voxvv1ypNJHYLDKeWZ8e-q5lXd-du8mbe7QzF_fKJsBi9emOljdHgDKiGcW7tVLtYTLj3nZAByrG2cOVsKwJ2sauJlf1dn4STxkN6lvyRfxV5F0A',
            'gulu_source_res': 'eyJwX2luIjoiNmY3NThiODk4NjYwY2E4N2MyZWRlMDRjN2UyYjliM2QzNTg1ZjgwMDgxYWJhNDExMDY1OGE5NzkzMjc5NjBiMyJ9',
            'passport_auth_mix_state': 'tgt2gaxdnlshmfzmrhaz016hxd98jze6ptvquno62mim8veh',
            'IsDouyinActive': 'true',
            'stream_recommend_feed_params': '%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22',
            'FOLLOW_LIVE_POINT_INFO': '%22MS4wLjABAAAA-IKEOrbtAzyhs8zgkOCqexwIF6qVkWFpfCinfHrBp4ILWyZpU6a4py7Bk90h84ts%2F1759075200000%2F0%2F0%2F1759059329019%22',
            'FOLLOW_NUMBER_YELLOW_POINT_INFO': '%22MS4wLjABAAAA-IKEOrbtAzyhs8zgkOCqexwIF6qVkWFpfCinfHrBp4ILWyZpU6a4py7Bk90h84ts%2F1759075200000%2F0%2F0%2F1759059929019%22',
            # 'bd_ticket_guard_client_data': 'eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTEViYnpUaEhFbE43dks0UFVqUDc2dEJiZlZPZytHZWpoK3JoS0RYZ3pHbEs5QUxVWE83UzhlSzRkY0tJR0kyVnRSazd3aGFLbnlKMXZqYzdqbm1WRzA9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D',
            'home_can_add_dy_2_desktop': '%221%22',
            'ttwid': '1%7C5R_nDzipYXXgyGYFx7PiEKE-bHqytrz1jp7Etg8C_3s%7C1759058734%7C38bb3adcd7197bb8183472a4e1c013ebb87ed58a72b3dbf139a023ae8ca4b26b',
            'biz_trace_id': '1f15dea6',
            'odin_tt': 'abeb7a22adce32e798ac2370f6221db6633db57640a49dee2f05e204e1666f456f9b2bb56c0c04107969acfd2534d6a95302193d24cafec029769a7557b9d69d',
            # 'bd_ticket_guard_client_data_v2': 'eyJyZWVfcHVibGljX2tleSI6IkJMRWJielRoSEVsTjd2SzRQVWpQNzZ0QmJmVk9nK0dlamgrcmhLRFhnekdsSzlBTFVYTzdTOGVLNGRjS0lHSTJWdFJrN3doYUtueUoxdmpjN2pubVZHMD0iLCJ0c19zaWduIjoidHMuMi5kNjMyMGQ5YzNkODhlM2YzNTY2YTUxZmFkZWVkNWI5MjViNTA2OTVhNWE0Zjg4MmM3MTg2MjhkOWI3NTAzMzExYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJocXZVZVBPbWlIZ2pRUE5YZjNFaFhkRXZCajdoQktTU0NDNVZ0N21VVW1zPSIsInNlY190cyI6IiMwUHp6OG16dHlwYjZnZjk2dE1EWTZ4ZkNYWDFzYjVvWk5sQXdYcFU4WmxZaFJHMTZOVTJzaC9OV0FrRFYifQ%3D%3D',
            'stream_player_status_params': '%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22',
        }

        # '{"ree_public_key":"BLEbbzThHElN7vK4PUjP76tBbfVOg+Gejh+rhKDXgzGlK9ALUXO7S8eK4dcKIGI2VtRk7whaKnyJ1vjc7jnmVG0="
        # ,"ts_sign":"ts.2.d6320d9c3d88e3f3566a51fadeed5b925b50695a5a4f882c718628d9b7503311c4fbe87d2319cf05318624ceda14911ca406dedbebeddb2e30fce8d4fa02575d"
        # ,"req_content":"sec_ts","req_sign":"hqvUePOmiHgjQPNXf3EhXdEvBj7hBKSSCC5Vt7mUUms="
        # ,"sec_ts":"#0Pzz8mztypb6gf96tMDY6xfCXX1sb5oZNlAwXpU8ZlYhRG16NU2sh/NWAkDV"}'

        # {"bd-ticket-guard-version":2,"bd-ticket-guard-iteration-version":1,
        # "bd-ticket-guard-ree-public-key":"BLEbbzThHElN7vK4PUjP76tBbfVOg+Gejh+rhKDXgzGlK9ALUXO7S8eK4dcKIGI2VtRk7whaKnyJ1vjc7jnmVG0=",
        # "bd-ticket-guard-web-version":2}'

        # '{"ts_sign":"ts.2.d6320d9c3d88e3f3566a51fadeed5b925b50695a5a4f882c718628d9b7503311c4fbe87d2319cf05318624ceda14911ca406dedbebeddb2e30fce8d4fa02575d"
        # ,"req_content":"ticket,path,timestamp","req_sign":"23Z2L3Ej1EGtKJaReUkogNY2HakP01LItBJEHN5zkc4=","timestamp":1759058809}'
        # 设置cookieBD
        cookieBD = self.getBd()
        result = json.loads(cookieBD)
        cookies['bd_ticket_guard_client_data'] = quote(result['result'])
        # 取私钥
        privateKey = result['privateKey']
        publicKey = result['reePublicKey']

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'bd-ticket-guard-client-data': 'eyJ0c19zaWduIjoidHMuMi5iMzFiMDVlMTc5MjY2NmU2MjU3NjkyYWIxNjk0NGZmOTU2ODZmMTc1ZGExZWJlMWMyMTBlYWRiZmVkZDk2YzhkYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50IjoidGlja2V0LHBhdGgsdGltZXN0YW1wIiwicmVxX3NpZ24iOiJMVXhRRVIxVzJxQU9hTk8yNlRWZWxlb2x2Uk96ekdsMDZ4WVlXMDl1NDVnPSIsInRpbWVzdGFtcCI6MTc1ODgwNjUyNn0=',
            'bd-ticket-guard-iteration-version': '1',
            # 'bd-ticket-guard-ree-public-key': 'BCIaMVBBBtGNAuW0TOEkQVCgCJCoqrwrYDmVx/CJqv3XALEka72qb/qUvBbwLF+q7kV7MbDwtRlMXxXyll6P04k=',
            'bd-ticket-guard-version': '2',
            'bd-ticket-guard-web-sign-type': '1',
            'bd-ticket-guard-web-version': '2',
            'cache-control': 'no-cache',
            # Already added when you pass json=
            # 'content-type': 'application/json',
            'origin': 'https://live.douyin.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://live.douyin.com/{web_rid}?anchor_id={uid}&category_name=all&follow_status=0&is_vs=0&page_type=main_category_page&vs_ep_group_id=&vs_episode_id=&vs_episode_stage=&vs_season_id=',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            # 'x-secsdk-csrf-token': '000100000001359bff6a98a71c67ef57221f56dd7f3b37d8242236d7b4c8e9873caac160b3181868893304d7fee6'
        }
        headers['bd-ticket-guard-ree-public-key'] = publicKey

        params = {
            'aid': '6383',
            'app_name': 'douyin_web',
            'live_id': '1',
            'device_platform': 'web',
            'language': 'zh-CN',
            'enter_from': 'web_live',
            'cookie_enabled': 'true',
            'screen_width': '1707',
            'screen_height': '1067',
            'browser_language': 'zh-CN',
            'browser_platform': 'Win32',
            'browser_name': 'Chrome',
            'browser_version': '140.0.0.0',
            'follow_type': '1',
            # 'current_room_id': '7553973405104507682',
            # 'sec_to_user_id': 'MS4wLjABAAAAY26a7g3F-q9Tavzlx8zZsq0xusaj7zRaN6NtyBOcTb0',
            # 'sec_user_id': '',
            # 'to_user_id': '63658076389',
            'channel_id': '200',
            # 'msToken': 'sfvAzmtZoQR9dh-XcY8lTZpXk8wSeK-MJnFyrp9YY6fa1Doys06OpOpu6mm8u9Cv29ZJlyX2kOV3uBoKyW8m_k8VlvKoK_nuS-DgnH8XGjPMb_Nw1Tm7ljcfmo0gECLk-ifwbQCH_IiadrZkrfrd0z5A_qjFDxDP-VX-3nVcfOcqvCmgZ8_rtw==',
            # 'a_bogus': 'Oys5hw6LDombOVMt8CDFS4KllFIlNB8yPPiOW9-KHNucOH0YMYNAgikOaqwXWjNLCYpshKI7rnQlbfEP0II3IZnpqmZvu84bST2A9tmLMqwVblkmENm2e84FzwBY85sNa5C3EIjR6s0i2xo5nqCiAdlSF/4x-cRD/13tVATSi2ymUASjhx2CaVjZNw7qmj==',
        }
        params['sec_to_user_id'] = sec_to_user_id
        params['sec_user_id'] = sec_user_id
        params['to_user_id'] = uid
        params['current_room_id'] = room_id

        # 设置headersBD
        ts = round(time.time())
        salt = f"ticket={web_protect['ticket']}&path=/webcast/user/relation/update/&timestamp={ts}"
        print(privateKey)
        print(s_sdk_server_cert_key['cert'])
        print(salt)
        headersBD = self.getBd(privateKey, s_sdk_server_cert_key['cert'], salt)
        result = json.loads(headersBD)
        # 组装bd_ticket_guard_client_data
        bd_ticket_guard_client_data = {
            "ts_sign": web_protect['ts_sign'],
            "req_content": "ticket,path,timestamp",
            "req_sign": result['req_sign'],
            "timestamp": ts
        }
        print(bd_ticket_guard_client_data)
        # encoded_string = base64.b64encode(
        #     json.dumps(bd_ticket_guard_client_data, separators=(',', ':')).encode('utf-8')).decode('utf-8')
        # headers['bd-ticket-guard-client-data'] = encoded_string

        json_data = {}
        uri = "https://live.douyin.com/webcast/user/relation/update/"
        url = uri + "?" + urlencode(params)
        a_bogus = self.getABogus(url, ua=headers["user-agent"])
        url += "&a_bogus=" + a_bogus['abogus']
        print(url)

        response = requests.post(
            url,
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        print("直播间关注测试", response.text)


    def getlive(self):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'agw-js-conv': 'str',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://compass.jinritemai.com/shop/chance/rank-product?from_page=%2Fshop%2Fchance%2Frank-search&btm_ppre=a6187.b44747.c0.d0&btm_pre=a6187.b85340.c0.d0&btm_show_id=01c29c03-2943-4c97-8bfb-83c9999c6def',
            'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
            'cookie': 'Hm_lvt_b6520b076191ab4b36812da4c90f7a5e=1759996609; qc_tt_tag=0; is_staff_user=false; use_biz_token=true; passport_csrf_token=160a91eb6705845b5b5f03ed94cbe2fb; passport_csrf_token_default=160a91eb6705845b5b5f03ed94cbe2fb; has_biz_token=false; csrf_session_id=df3292de7738ce5274519ff377efc9f9; passport_auth_status=b5e11d3324f8a72c79166a219b490348%2C; passport_auth_status_ss=b5e11d3324f8a72c79166a219b490348%2C; gfkadpd=4499,28161|4499,20590; ttwid=1%7Ckimy0lj6g3kkGnScZio9_HcjxwaCUkUSVYLufFm4Prw%7C1777107073%7Ce5ad78a7b9f47526b7f1a90d92045843d68cdb8a07256b63c7f82af4a305717c; s_v_web_id=verify_moe3orbr_ec319109_bba3_eb53_96ae_bbd6ac40986b; passport_mfa_token=CjF5%2FZuHXnFyR%2FW5zifhIrU7hH%2BAg6b%2FYTqdbs8DGKG2d49ug54Oq28lHaMEmIcTwW0QGkoKPAAAAAAAAAAAAABQWJISGqjsuWQBJUznYR%2FWNeMH7GJvW0NkJulSOE4BREJnD%2Flg3RvoW9LIP4EvJSkgORDD4I8OGPax0WwgAiIBAwufYPk%3D; odin_tt=6580a138b8c48bbaf0272407be8ffd578c4045e8260a29e0f303c464b6a6e317af89e824f7d8d2dc7ac65f866a200a52cb13e9519876df0e430975ec2f9802ef; uid_tt=256dda90587f4e5a46d368f2c115d902; uid_tt_ss=256dda90587f4e5a46d368f2c115d902; sid_tt=b141f0c75899b11d91674d4c597ffe0f; sessionid=b141f0c75899b11d91674d4c597ffe0f; sessionid_ss=b141f0c75899b11d91674d4c597ffe0f; ucas_c0_compass=CkEKBTEuMC4wEI-Ijd74nqD2aRjmJiDYuPCcwK2IASiwITCI8_DMqvWVBED9gbLPBkj9te7RBlCavLOOgsSd9GlYbxIUdDU1Wq-B9m2X57q1S1rmzysDQ5E; ucas_c0_ss_compass=CkEKBTEuMC4wEI-Ijd74nqD2aRjmJiDYuPCcwK2IASiwITCI8_DMqvWVBED9gbLPBkj9te7RBlCavLOOgsSd9GlYbxIUdDU1Wq-B9m2X57q1S1rmzysDQ5E; sid_guard=b141f0c75899b11d91674d4c597ffe0f%7C1777107197%7C5184000%7CWed%2C+24-Jun-2026+08%3A53%3A17+GMT; session_tlb_tag=sttt%7C20%7CsUHwx1iZsR2RZ01MWX_-D__________f-OBhPd63-xNTDKbREC4HafaL_GRAZwu2mmv4jWapGMI%3D; sid_ucp_v1=1.0.0-KDJjYzdkMTIwNDhlMGI1M2Q1N2RiM2M2ODhkNDRjOWQzNDI4MWE4NzEKGQiI8_DMqvWVBBD9gbLPBhiwISAMOAFA6wcaAmxxIiBiMTQxZjBjNzU4OTliMTFkOTE2NzRkNGM1OTdmZmUwZg; ssid_ucp_v1=1.0.0-KDJjYzdkMTIwNDhlMGI1M2Q1N2RiM2M2ODhkNDRjOWQzNDI4MWE4NzEKGQiI8_DMqvWVBBD9gbLPBhiwISAMOAFA6wcaAmxxIiBiMTQxZjBjNzU4OTliMTFkOTE2NzRkNGM1OTdmZmUwZg; LUOPAN_DT=session_7632616844062540038; COMPASS_LUOPAN_DT=session_7632616844062540038; ecom_us_lt_compass=16b8b47eefb3831fab56a3ab4e4efb2fb67d4de0a93f453b083ea37c57585a48; ecom_us_lt_ss_compass=16b8b47eefb3831fab56a3ab4e4efb2fb67d4de0a93f453b083ea37c57585a48',
        }

        params = {
            'page_no': '1',
            'page_size': '10',
            'industry_id': '13',
            'category_id': '1000001823',
            'brand_type': '-1',
            'price_bin': '不限',
            'search_info': '',
            'rank_data_type': '1',
            'begin_date': '2026/04/18 00:00:00',
            'end_date': '2026/04/24 00:00:00',
            'date_type': '21',
            'activity_id': '',
            '_lid': '085965688488',
            'msToken': '3JnvAxrfd5pACtXp3s5TyOKC7cXlmXzHWhgC-n5RCMr3VdD8bN5FU44iboL1nDFK9S0ZJKvZza5AK3nlGG3Neh-0QYYllCxaBBQHdtxIioSb8U1kS__ufrpQsIIG-pqC5xjjSCOp60QO2vBORg40ytnV2GDGMTjeZjOlxgdBD4mRfpmiaGePwQ==',
            # 'a_bogus': 'Q645kzSLEd5fPplSucQqtA1lK9VlNPSy5ei/bGKN9qPQa10Yy--kbce/axqQ-WVVKmM8ZMC7cpsMCjdbYUiiZ/-kwmhfux7y84VC9XfogqNZTFt8EHbOCz0zowMu057ieQ5tiIXUgUaoZVOWg1QD/3l9SA/F5RgZMHCjkoYbxIa31zglE3nePQGsYXiqDf==',
            'verifyFp': 'verify_moe3orbr_ec319109_bba3_eb53_96ae_bbd6ac40986b',
            'fp': 'verify_moe3orbr_ec319109_bba3_eb53_96ae_bbd6ac40986b',
        }
        url = 'https://compass.jinritemai.com/compass_api/shop/product/product_rank/live_product?'
        url += urlencode(params)
        a_bogus = self.getABogus(url, ua=headers["user-agent"])
        url += '&a_bogus=' + a_bogus['abogus']
        print(url)
        response = requests.get(
            url,
            params=params,
            headers=headers,
        )

        print(response.text)

    def sendMessage(self, content):
        # s_sdk_server_cert_key = {"data":"{\"ec_privateKey\":\"-----BEGIN PRIVATE KEY-----\\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgfidh6GJrlbC4s52OyjblDlychyRVUEyd1/kwOn+4qZqhRANCAAQiGjFQQQbRjQLltEzhJEFQoAiQqKq8K2A5lcfwiar91wCxJGu9qm/6lLwW8Cxfqu5FezGw8LUZTF8V8pZej9OJ\\n-----END PRIVATE KEY-----\",\"ec_publicKey\":\"-----BEGIN PUBLIC KEY-----\\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIhoxUEEG0Y0C5bRM4SRBUKAIkKiqvCtgOZXH8Imq/dcAsSRrvapv+pS8FvAsX6ruRXsxsPC1GUxfFfKWXo/TiQ==\\n-----END PUBLIC KEY-----\",\"ec_csr\":\"\"}"}
        web_protect = {
            "data": "{\"ticket\":\"hash.sRntt+EJgd0bu2V5IGtrlNQjgSGxXhqGnfo5sluB8YE=\",\"ts_sign\":\"ts.2.5c52a35ac7915eeaf8da840ca513831e4f97dfbd32bd191862d5a27926dd8067c4fbe87d2319cf05318624ceda14911ca406dedbebeddb2e30fce8d4fa02575d\",\"client_cert\":\"pub.BCIaMVBBBtGNAuW0TOEkQVCgCJCoqrwrYDmVx/CJqv3XALEka72qb/qUvBbwLF+q7kV7MbDwtRlMXxXyll6P04k=\",\"log_id\":\"202510021419552F87946A1613EFA1A576\",\"create_time\":1759385996}"}
        web_protect = json.loads(web_protect['data'])
        token = web_protect['ticket']
        ts_sign = web_protect['ts_sign']
        # s_sdk_server_cert_key = json.loads(s_sdk_server_cert_key['data'])
        # ec_privateKey = s_sdk_server_cert_key['ec_privateKey']
        # ec_publicKey = s_sdk_server_cert_key['ec_publicKey']
        # print("公钥", ec_publicKey)
        # print("私钥", ec_privateKey)
        print("token", token)

        cookies = {

        }
        # 设置cookieBD
        cookieBD = self.getBd()
        result = json.loads(cookieBD)
        biz_trace_id = TikTokApi.getTraceId()
        cookies['biz_trace_id'] = biz_trace_id
        cookies['bd_ticket_guard_client_data'] = quote(result['result'])
        # 取私钥
        privateKey = result['privateKey']
        # 取公钥
        publicKey = result['publicKey']
        print("公钥", publicKey)
        print("私钥", privateKey)

        headers = {
            'accept': 'application/x-protobuf',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-protobuf',
            'origin': 'https://www.douyin.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.douyin.com/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        }

        fp = cookies.get('s_v_web_id')

        params = {
            'msToken': '4xm7H8acwGrzCvYmg_xpojnDK6cUKoC0pjy41TmkHIlH2zwOkFlhfhAF8_OIIWFrmo6wj8zetdnUr0cWExevh-YLH65orH5QGko4C_PhhZbE3GAqXYf00F0fSJ5wiT9bEYZ2fvkLiqIs3DdUYX5vDoM6kyCujd--_f0NMHqbihNzf4xHsUWVkGk=',
            # 'a_bogus': 'Q74RkHtixdRbedFS8cP173pUu1LArBSyAPidbcKTCPT2c70Gk8PaLPegGoFYxRT-yYBzhoZ7ndPAYDVbz0UhZorkwmkDuEUy9z2C9tfL0qiXGzvkgrDKegYFww0eU5voeQ9nE1D5Is0jId959H9hAB5Cq/-rBRbDOp-7VlTSY2ym0WWjin2Va3vsuh3I',
            'verifyFp': fp,
            'fp': fp
        }
        meUID = '' # 自己的uid
        heUID = '' # 对方的uid
        uuid4 = str(uuid.uuid4())
        print("消息id", uuid4)
        stime = str(time.time() * 1000)
        print("时间戳", stime)

        data = {
            "headers": {
                "identity_security_token": "{\"token\":\"Cji4MTqGnTWOlWwDbPBrtBtQQyC1-0l0v-YVPobYuYiEtudsNpGrvdLfLrBQfz6icpRU-K6gs8Z1vBpKCjwAAAAAAAAAAAAAT4xTJzCF5h1cntbaljE2PEPO3OULHV-oAMgF3ZJ10XRwsGlh-znvg8LlYU4XdeaAxhsQier9DRj2sdFsIAIiAQMbVnAX\"}",
                "identity_security_device_id": "7552095721379038735",
                "identity_security_aid": "6383",
                "session_aid": "6383",
                "session_did": "0",
                "app_name": "douyin_pc",
                "priority_region": "cn",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                "cookie_enabled": "true",
                "browser_language": "zh-CN",
                "browser_platform": "Win32",
                "browser_name": "Mozilla",
                "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                "browser_online": "true",
                "screen_width": "1707",
                "screen_height": "1067",
                "referer": "",
                "timezone_name": "Asia/Shanghai",
                "deviceId": "0",
                "webid": "7552095721379038735",
                "fp": "verify_mg3lkflo_EiwGiSIa_TvvT_454Y_APaU_3N3i6R2wGNCw",
                "is-retry": "0"
            },
            "body": {
                "send_message_body": {
                    "conversation_id": f"0:1:{meUID}:{heUID}",  # '1:0'是接收，'0:1'是发送
                    "conversation_short_id": {
                        "high": 1724004548,
                        "low": 1401045540,
                        "unsigned": False
                    },
                    "conversation_type": 1,
                    "content": "{\"mention_users\":[],\"aweType\":700,\"richTextInfos\":[],\"text\":\"你好\"}",
                    "mentioned_users": [],
                    "client_message_id": uuid4,
                    "ticket": "1laWxwIOwRJOwVmkPP7hsf26UVrgVnTJe8KQqIp2db9VMdseRQZJFkwavIdKHHSP3XnHGz03mt29LGK80I7eD35zXPyiUNZLMYR67He332BynbuT2CUfB4gxU",
                    "message_type": 7,
                    "ext": {
                        "s:mentioned_users": "",
                        "s:client_message_id": uuid4,
                        "s:stime": stime
                    }
                }
            },
            "cmd": 100,
            "sequence_id": {
                "low": 10018,
                "high": 0,
                "unsigned": False
            },
            "refer": 3,
            "token": "",
            "device_id": "0",
            "sdk_version": "1.1.3",
            "build_number": "8aa2dcb:Detached: 8aa2dcb88b41538885168e4afbbd2b6bac8aefb2",
            "inbox_type": 0,
            "device_platform": "douyin_pc",
            "auth_type": 4,
            "biz": "douyin_web",
            "access": "web_sdk",
            "sdk_cert": "",
            "ts_sign": "",
            "reuqest_sign": ""
        }
        # 计算reuqest_sign
        contents = data['body']['send_message_body'].get('content')
        contents = contents.replace('你好', content)
        data['body']['send_message_body']['content'] = contents
        result = self.getBd(privateKey, publicKey, contents, 'sendMessage')
        reuqest_sign = json.loads(result)
        data['token'] = token
        data['ts_sign'] = ts_sign
        data['sdk_cert'] = reuqest_sign['sdk_cert']
        data['reuqest_sign'] = reuqest_sign['reuqest_sign']


        # 开始protobuf 组包
        short_id = data['body']['send_message_body'].get('conversation_short_id')
        sequence_id = data['sequence_id']
        if isinstance(short_id, dict):
            high = short_id['high']
            low = short_id['low']
            conversation_short_id = TikTokApi.convert_high_low_to_values(high, low)
            data['body']['send_message_body']['conversation_short_id'] = conversation_short_id
        if isinstance(sequence_id, dict):
            high = sequence_id['low'] if sequence_id['high'] == 0 else sequence_id['high']
            data['sequence_id'] = high

        serialized_data = ''
        # try:
        #     result = douyin_pb2.RequestMessage()
        #     ParseDict(data, result)
        #     serialized_data = result.SerializeToString()
        #     print("长度：", len(serialized_data))
        #     print("序列化后的二进制数据：", serialized_data)
        #     print("hex：", serialized_data.hex())
        # except Exception as e:
        #     print(e)

        # 开始计算abogus
        uri = "https://imapi.douyin.com/v1/message/send"
        url = uri + "?" + urlencode(params)
        a_bogus = self.getABogus(url, ua=headers["user-agent"], data=json.dumps(data,separators=(',',':')))
        url += "&a_bogus=" + a_bogus['abogus']
        print("url", url)

        # response = requests.post(url,
        #     cookies=cookies,
        #     headers=headers,
        #     data=serialized_data,
        #     # proxies={'http': 'http://127.0.0.1:7890'},
        # )
        # print("sendMessage:", response.text)


    def getSku2(self, product_id:str, douyinUserinfo:dict) -> dict:
        # 登录抖音网页版替换cookie、uifid、fp、mstoken、verifyFp
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://www.douyin.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.douyin.com/?recommend=1',
            'sec-ch-ua': '"Google Chrome";v="146", "Chromium";v="146", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'uifid': douyinUserinfo['uifid'],
            'user-agent': douyinUserinfo['user-agent'],
            'x-secsdk-csrf-token': 'DOWNGRADE',
            'cookie': douyinUserinfo['cookie'],
        }

        params = [
            ('device_platform', 'webapp'),
            ('aid', '6383'),
            ('channel', 'channel_pc_web'),
            ('app_name', 'aweme'),
            ('webid', douyinUserinfo['webid']),
            ('user_agent', douyinUserinfo['user-agent']),
            ('fp', douyinUserinfo['fp']),
            ('did', '0'),
            ('referer', ''),
            ('target', ''),
            ('pc_client_type', '1'),
            ('pc_libra_divert', 'Windows'),
            ('update_version_code', '170400'),
            ('support_h265', '1'),
            ('support_dash', '1'),
            ('version_code', '170400'),
            ('version_name', '17.4.0'),
            ('cookie_enabled', 'true'),
            ('screen_width', '1707'),
            ('screen_height', '1067'),
            ('browser_language', 'zh-CN'),
            ('browser_platform', 'Win32'),
            ('browser_name', 'Chrome'),
            ('browser_version', '149.0.0.0'),
            ('browser_online', 'true'),
            ('engine_name', 'Blink'),
            ('engine_version', '149.0.0.0'),
            ('os_name', 'macOS'),
            ('os_version', '10'),
            ('cpu_core_num', '32'),
            ('device_memory', '16'),
            ('platform', 'PC'),
            ('downlink', '10'),
            ('effective_type', '4g'),
            ('round_trip_time', '50'),
            ('uifid', douyinUserinfo['uifid']),
            ('verifyFp', douyinUserinfo['fp']),
            ('fp', douyinUserinfo['fp']),
            ('msToken', douyinUserinfo['msToken']),
        ]

        json_data = {
            'author_id': '0',
            'product_id': product_id,
        }

        url = f'https://www.douyin.com/aweme/v1/web/ecom/product/sku/list/?{urlencode(params)}'
        data = json.dumps(json_data, separators=(',', ':'))
        a_bogus = self.getABogus(url, ua=headers["user-agent"], data=data, t='ju')
        url += "&a_bogus=" + a_bogus['abogus']
        # print(url)

        response = tls_requests.post(
            url,
            headers=headers,
            data=data,
            impersonate='chrome146'
        )
        print("getSku2", response.text)
        return response.json()



    def getSkuPrice(self, product_id:str, skus:list[str], douyinUserinfo:dict):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.douyin.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.douyin.com/?recommend=1',
            'sec-ch-ua': '"Google Chrome";v="146", "Chromium";v="146", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'uifid': douyinUserinfo['uifid'],
            'user-agent': douyinUserinfo['user-agent'],
            'x-secsdk-csrf-token': 'DOWNGRADE',
            'cookie': douyinUserinfo['cookie'],
        }

        params = [
            ('device_platform', 'webapp'),
            ('aid', '6383'),
            ('channel', 'channel_pc_web'),
            ('app_name', 'aweme'),
            ('webid', douyinUserinfo['webid']),
            ('user_agent', douyinUserinfo['user-agent']),
            ('fp', douyinUserinfo['fp']),
            ('did', '0'),
            ('referer', ''),
            ('target', ''),
            ('pc_client_type', '1'),
            ('pc_libra_divert', 'Windows'),
            ('update_version_code', '170400'),
            ('support_h265', '1'),
            ('support_dash', '1'),
            ('version_code', '170400'),
            ('version_name', '17.4.0'),
            ('cookie_enabled', 'true'),
            ('screen_width', '1707'),
            ('screen_height', '1067'),
            ('browser_language', 'zh-CN'),
            ('browser_platform', 'Win32'),
            ('browser_name', 'Chrome'),
            ('browser_version', '149.0.0.0'),
            ('browser_online', 'true'),
            ('engine_name', 'Blink'),
            ('engine_version', '149.0.0.0'),
            ('os_name', 'Windows'),
            ('os_version', '10'),
            ('cpu_core_num', '32'),
            ('device_memory', '16'),
            ('platform', 'PC'),
            ('downlink', '10'),
            ('effective_type', '4g'),
            ('round_trip_time', '50'),
            ('uifid', douyinUserinfo['uifid']),
            ('verifyFp', douyinUserinfo['fp']),
            ('fp', douyinUserinfo['fp']),
            ('msToken', douyinUserinfo['msToken']),
        ]

        sku_ids = []
        # content_id是视频ID
        videoId = '7633454865993256234'
        for sku in skus:
            sku_ids.append(
                {'specify_sku_id': sku, 'specify_sku_num': 1, 'specify_activity_id': '0',
                 'guide_trade_transmit_info': '{"log_id":""}', 'product_id': product_id,
                 'sku_id': sku, 'sku_num': 1, 'content_id': videoId,
                 'promotion_id': product_id, 'origin_id': f'{videoId}_{product_id}',
                 'origin_type': '3002001000', 'new_source_type': 'product_detail',
                 'buyin_track': '', 'extra': '{}'}
            )
        data_str = {'first_enter': True, 'shape': 0, 'forbid_redpack': True, 'support_redpack': False, 'use_marketing_combo': False, 'auto_select_best_coupons': True, 'auto_apply_coupon': 1, 'cj_sdk': '', 'source_type': '1', 'marketing_channel': '', 'entrance_params': '', 'shop_requests': [{'shop_id': 'FfFhpbIP', 'product_requests': sku_ids}]}
        json_data =  {
            'json_form': json.dumps(data_str, separators=(',',':'), ensure_ascii=False),
        }
        data = f'json_form={quote(json_data['json_form'])}'
        url = f'https://www.douyin.com/aweme/v1/web/ecom/order/confirm/?{urlencode(params)}'
        a_bogus = self.getABogus(url, ua=headers["user-agent"], data=data)
        url += "&a_bogus=" + a_bogus['abogus']
        response = tls_requests.post(url, headers=headers, data=data, impersonate='chrome146')
        print("response", response.text)
        return response.json()


    def _ShopSku(self, biz_id, userinfo: dict) -> dict:
        """
        通过商品ID查询商品规格
        Args:
            biz_id: 商品ID
        Returns:
            商品SKU
        """
        from logindemo_ju import getEWID, api
        _cookie = userinfo.get('cookie', '')
        _msToken = userinfo.get('msToken', '')

        headers = self.JuLiangHeaders(_cookie)
        headers['content-type'] = 'application/json'
        headers['referer'] = f'https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?commodity_id={biz_id}&commodity_location=2&id={biz_id}&commodity_location=2&pick_first_source={quote('百应')}&pick_second_source={quote('选品广场')}&pick_third_source=category_recommend&pick_source_id=&recommend_reason_type=&recommend_reason_text=&recall_source=viking_pick_efficient_recalls%3A164%3A-3.56817%2CFIRST%23i2v_search_recalls%3A17%3A-9+%7C+&is_outside_log=1&only_query_params=1&universal_append=1'
        uuid_str = str(uuid.uuid4())
        _msToken = api().getMsToken(_cookie, _msToken, uuid_str)
        userinfo['msToken'] = _msToken
        ewid = getEWID(_msToken, userinfo, False, referer=headers['referer'])
        userinfo['ewid'] = ewid
        fp = self.get_cookie_value(_cookie, 's_v_web_id') or ''

        params = {
            'ewid': ewid,
            # 'seraph_did': '',
            'verifyFp': fp,
            'fp': fp,
            'msToken': _msToken,
        }

        body = {
            "scene_info":{"request_page":2},
            "other_params":{"colonel_activity_id":""},
            "biz_id":str(biz_id),
            "biz_id_type":2,
            "enter_from":"pc.selection_square.recommend_main",
            "data_module":"dynamic",
            "dynamic_params":{"param_type":6},
            "extra":{}
        }

        json_data = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
        headers['content-type'] = 'application/json'
        url = f'https://buyin.jinritemai.com/pc/selection/decision/pack_detail?{urlencode(params)}'
        a_bogus = self.getABogus(url, ua=headers["user-agent"], data=json_data, t='ju')
        url += "&a_bogus=" + a_bogus['abogus']
        _csrf_token = self.get_token(biz_id=biz_id, cookie_str=_cookie)
        headers['x-secsdk-csrf-token'] = _csrf_token
        print("x-secsdk-csrf-token", _csrf_token)
        response = tls_requests.post(
            url,
            headers=headers,
            data=json_data,
            impersonate='chrome146',

        ).content
        print("sku", response.decode('utf-8'))

        result = {
            "response": response.decode('utf-8'),
            "params": userinfo
        }
        return result

    def _ShopInfo(self, biz_id, userinfo, sale: bool = False):
        """
        通过商品ID查询商品详情
        Args:
            biz_id: 商品ID
            sale: 是否获取销量，默认否
        Returns:
            商品详情
        """
        from  logindemo_ju import getEWID, api
        _cookie = userinfo.get('cookie', '')
        _msToken = userinfo.get('msToken', '')
        headers = self.JuLiangHeaders(cookie_str=_cookie)
        headers['content-type'] = 'application/json'
        headers['referer'] = f'https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?commodity_id={biz_id}&commodity_location=1&id={biz_id}'
        uuid_str = str(uuid.uuid4())

        _msToken = api().getMsToken(_cookie, _msToken, uuid_str)
        userinfo['msToken'] = _msToken
        ewid = getEWID(_msToken, userinfo, False)
        userinfo['ewid'] = ewid
        fp = self.get_cookie_value(_cookie, 's_v_web_id') or ''
        params = {
            'ewid': ewid,
            'seraph_did': '',
            'verifyFp': fp,
            'fp': fp,
            'msToken': _msToken,
        }

        body = {
            'scene_info': {
                'request_page': 2,
            },
            'other_params': {
                'colonel_activity_id': '',
            },
            'biz_id': biz_id,
            'biz_id_type': 2,
            'enter_from': 'pc.selection_square.recommend_main',
            'data_module': 'core',
            'extra': {},
        }
        if sale:
            body = {
                'scene_info': {
                    'request_page': 2,
                },
                'biz_id': biz_id,
                'biz_id_type': 2,
                'enter_from': 'pc.selection_square.recommend_main',
                'data_module': 'pc-non-core',
                'extra': {
                    'use_kol_product': '1',
                },
            }

        json_data = json.dumps(body, separators=(',', ':'))
        url = f'https://buyin.jinritemai.com/pc/selection/decision/pack_detail?{urlencode(params)}'
        a_bogus = self.getABogus(url, ua=headers["user-agent"], data=json_data, t='ju')
        url += "&a_bogus=" + a_bogus['abogus']
        headers['content-type'] = 'application/json'
        response = tls_requests.post(
            url,
            headers=headers,
            data=json_data,
            impersonate='chrome146'
        ).text

        result = {
            "response": response,
            "params": userinfo,
        }
        # print("商品详情", response.text)
        return result

def test():
    # 使用146版本userAgent
    # pip install curl_cffi
    # uv add curl_cffi 或 uv pip install curl_cffi

    _page = 0
    userinfo = {
      "web_id": "",
      "user_id": "",
      "shop_id": "",
      "account_id": "",
      "cookie": "passport_csrf_token=cf83d8d43ccd3831ace5f62d71f69608; passport_csrf_token_default=cf83d8d43ccd3831ace5f62d71f69608; s_v_web_id=verify_mraohhuw_Hw0l9foO_3jOq_4srC_AEdi_z62hnMk2n4EE; is_staff_user=false; has_biz_token=false; _tea_utm_cache_3813=undefined; scmVer=1.0.2.1533; _tea_utm_cache_2631=undefined; MONITOR_WEB_ID=72b54189-035a-4141-ba62-50a23a1dce2e; ttcid=e2be7ab2795547da8c2f823c767ac46842; gfkadpd=2631,22740; csrf_session_id=13fe801e209ba5f181111ca7dd64e5b4; biz_trace_id=118b281d; __security_mc_1_s_sdk_crypt_sdk=fc3acb33-4442-b1f7; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSjN0L0dvdkdicmtYUFdIMVlqcDVEWkZMdzRmTW1DQS9RamxmZzhYUEx5VFRFR1o3RDA2QUk2ZXJmV2JpbDdrYUFhZnRWY3RuTWl0RE55ZnhPM2NWdDA9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; bd_ticket_guard_client_web_domain=2; ttwid=1%7CcLIFqeNgwcOPwGKobamb31-5Lv8s_uHBYy6iz27jFSE%7C1784635022%7C4a78d370339540e423015455b24fc88912c2ea92ee7b8fb7457d5e4c5fa52893; odin_tt=fdaf6dce92b7df11a421482ef1e800c6d1b6d01f6405b734628fc81c6d8da4704b3b78c24cf74fd7c0ca780039aeefd864882f79294d847e116e62757f5c15bc; passport_auth_status=26085d18a1d829d98e2038c5f6ea49f6%2C1fd50bf35107a4836a7314be3731b1c8; passport_auth_status_ss=26085d18a1d829d98e2038c5f6ea49f6%2C1fd50bf35107a4836a7314be3731b1c8; uid_tt=c846e84394fa84621929bd7668b23646; uid_tt_ss=c846e84394fa84621929bd7668b23646; sid_tt=42bb116b581495f5817382a4178e2729; sessionid=42bb116b581495f5817382a4178e2729; sessionid_ss=42bb116b581495f5817382a4178e2729; ucas_c0_buyin=CkEKBTEuMC4wEK6IhoSo0devahi9LyD7mODf2KztByiPETC6xPC5w6zdBECQvf3SBkiQ8bnVBlCbvKOo6L2qrGpYfhIUqrYbmML3BVo--sIjzlNCSHSD4Js; ucas_c0_ss_buyin=CkEKBTEuMC4wEK6IhoSo0devahi9LyD7mODf2KztByiPETC6xPC5w6zdBECQvf3SBkiQ8bnVBlCbvKOo6L2qrGpYfhIUqrYbmML3BVo--sIjzlNCSHSD4Js; sid_guard=42bb116b581495f5817382a4178e2729%7C1784635024%7C5184000%7CSat%2C+19-Sep-2026+11%3A57%3A04+GMT; session_tlb_tag=sttt%7C3%7CQrsRa1gUlfWBc4KkF44nKf_________egV5pMpCvNMiIaduCwoIGN-bJy4cw5U44h7iOdAMaGu8%3D; sid_ucp_v1=1.0.0-KDVmN2IzYmJhNDBlYTcyODg3MmE2NDdiOGU2OTMwOTRjNjA3ZGZhNmIKGgi6xPC5w6zdBBCQvf3SBhiPESAMOAhAJkgEGgJsZiIgNDJiYjExNmI1ODE0OTVmNTgxNzM4MmE0MTc4ZTI3Mjk; ssid_ucp_v1=1.0.0-KDVmN2IzYmJhNDBlYTcyODg3MmE2NDdiOGU2OTMwOTRjNjA3ZGZhNmIKGgi6xPC5w6zdBBCQvf3SBhiPESAMOAhAJkgEGgJsZiIgNDJiYjExNmI1ODE0OTVmNTgxNzM4MmE0MTc4ZTI3Mjk; SASID=SID2_7664948244137296180; BUYIN_SASID=SID2_7664948244137296180; buyin_shop_type=24; buyin_account_child_type=1128; buyin_app_id=1128; buyin_shop_type_v2=24; buyin_account_child_type_v2=1128; buyin_app_id_v2=1128; ecom_us_lt_buyin_top=10931bac0c31a37abc2bab2cdc2209384248d605e06fb9011bf14e91a43c92c0; ecom_us_lt_ss_buyin_top=10931bac0c31a37abc2bab2cdc2209384248d605e06fb9011bf14e91a43c92c0; ecom_us_lt_buyin=10931bac0c31a37abc2bab2cdc2209384248d605e06fb9011bf14e91a43c92c0; ecom_us_lt_ss_buyin=10931bac0c31a37abc2bab2cdc2209384248d605e06fb9011bf14e91a43c92c0; tt_scid=EWD3pBeqKSPJi5YFJi4VJ-tvVsAp5RfGISzQp7IRPRMn-NJDXWVjTtiC43rGMmjl5f78"
    }
    _msToken = userinfo.get('msToken', '')

    result = api.getShopList(shop_id='182473628', _page=_page, userInfo=userinfo)
    json_data = json.loads(result)
    for data in json_data['data']['summary_promotions']:
        _promotion_id = data['promotion_id']
        _product_id = data['product_id']
        sku_result = api._ShopSku(_promotion_id, userinfo)
        sku_result = sku_result
        print("商品sku_response:::", sku_result['response'])
        params_sku = sku_result['params']
        if '登录' in sku_result['response']:
            print("请重新登录")
            break
        sku_result_json = json.loads(sku_result['response'])
        # 复用msToken
        userinfo['msToken'] = params_sku['msToken']
        for item_sku in sku_result_json['data']['model']['sku_panel_data']['skus_spec_component']['sku_specs_list']:
            print(item_sku)


        time.sleep(1)



def test2():
    """一键获取店铺下所有商品sku信息"""
    userinfo = {
        "web_id": "",
        "user_id": "",
        "account_id": "",
        "msToken": "",
        "ewid": "",
        "cookie": "passport_csrf_token=c9e855f51e79183ff2d8623324d9253f; passport_csrf_token_default=c9e855f51e79183ff2d8623324d9253f; s_v_web_id=verify_mr5qc4ev_HDXChxEE_iNIX_4BLc_88Cz_u7jUqRF8iNYx; ttwid=1%7CEPynzswc9Te4XDLNPrFK9iIGj631SsaC4BzwWy5e73M%7C1783131309%7C9311634cee3c145127d96f361f629daa5de83d3fba903d30103569ea159103da; odin_tt=99021cb49270b40d1fb67465e27ad046534c90bd887c17fe2604777db357fb5e2061e072209d1ec1ae77d984d259aef671b4c6cc14379a4dfb021597cea49ca2; n_mh_daren=3_BiiUhKy3sgJX1q8p82m1zXXLISgjhbg5b4xQ_MIRA; passport_auth_status_daren=5d07be3bef03de43077e482c127c5d67%2C; passport_auth_status_ss_daren=5d07be3bef03de43077e482c127c5d67%2C; sso_uid_tt_daren=d9959703b58efe0076c43358be6cfe8d; sso_uid_tt_ss_daren=d9959703b58efe0076c43358be6cfe8d; toutiao_sso_user_daren=8dfb96b13e5a91df1885c35c524e0e4c; toutiao_sso_user_ss_daren=8dfb96b13e5a91df1885c35c524e0e4c; sid_ucp_sso_v1_daren=1.0.0-KDkyMzc4NzM1NWNlODExMjkyNDA3YTFhNzM5YzI5MzBlZjQ3NzI4OGIKHgips8C6x6zxBxCu2aHSBhiPESAMMNTqndIGOAhAJhoCbHEiIDhkZmI5NmIxM2U1YTkxZGYxODg1YzM1YzUyNGUwZTRj; ssid_ucp_sso_v1_daren=1.0.0-KDkyMzc4NzM1NWNlODExMjkyNDA3YTFhNzM5YzI5MzBlZjQ3NzI4OGIKHgips8C6x6zxBxCu2aHSBhiPESAMMNTqndIGOAhAJhoCbHEiIDhkZmI5NmIxM2U1YTkxZGYxODg1YzM1YzUyNGUwZTRj; passport_auth_status=375d9127a662da32b12e171b3cdf4fcf%2C; passport_auth_status_ss=375d9127a662da32b12e171b3cdf4fcf%2C; sid_guard=b9ec120cc1c05317eae314e4114d6dba%7C1783131313%7C5183999%7CWed%2C+02-Sep-2026+02%3A15%3A12+GMT; uid_tt=3253cd6ffeaa7bb6a8be9e55fa213712; uid_tt_ss=3253cd6ffeaa7bb6a8be9e55fa213712; sid_tt=b9ec120cc1c05317eae314e4114d6dba; sessionid=b9ec120cc1c05317eae314e4114d6dba; sessionid_ss=b9ec120cc1c05317eae314e4114d6dba; session_tlb_tag=sttt%7C3%7CuewSDMHAUxfq4xTkEU1tuv_________E2xFNspItHaHSH2UTShbxQ-DpPoEBSEQojJ2kErklgCA%3D; is_staff_user=false; has_biz_token=false; sid_ucp_v1=1.0.0-KDkzMDVhZTgxMzc3ZDdhNTJkOWM0NDYxMzc2ZTlhYzJkMGI5YTg4ODgKGAips8C6x6zxBxCx2aHSBhiPESAMOAhAJhoCbGYiIGI5ZWMxMjBjYzFjMDUzMTdlYWUzMTRlNDExNGQ2ZGJh; ssid_ucp_v1=1.0.0-KDkzMDVhZTgxMzc3ZDdhNTJkOWM0NDYxMzc2ZTlhYzJkMGI5YTg4ODgKGAips8C6x6zxBxCx2aHSBhiPESAMOAhAJhoCbGYiIGI5ZWMxMjBjYzFjMDUzMTdlYWUzMTRlNDExNGQ2ZGJh; ucas_sso_c0_daren=CkEKBTEuMC4wELaIkaq3lZukahi9LyC655DBx6zJAyiPETCps8C6x6zxB0Cw2aHSBkiwjd7UBlCzvIiYvoeSpGpYfhIUzrpp3U-neXc-uXl_q6rrIHWOUnQ; ucas_sso_c0_ss_daren=CkEKBTEuMC4wELaIkaq3lZukahi9LyC655DBx6zJAyiPETCps8C6x6zxB0Cw2aHSBkiwjd7UBlCzvIiYvoeSpGpYfhIUzrpp3U-neXc-uXl_q6rrIHWOUnQ; ucas_c0_buyin=CkEKBTEuMC4wEImIjuzQlZukahi9LyC655DBx6zJAyiPETCps8C6x6zxB0Cw2aHSBkiwjd7UBlCzvIiYvoeSpGpYfhIUzbOW5nVIz0jzddBybzDdz3X88-4; ucas_c0_ss_buyin=CkEKBTEuMC4wEImIjuzQlZukahi9LyC655DBx6zJAyiPETCps8C6x6zxB0Cw2aHSBkiwjd7UBlCzvIiYvoeSpGpYfhIUzbOW5nVIz0jzddBybzDdz3X88-4; SASID=SID2_7658489606759563556; buyin_shop_type=24; buyin_account_child_type=1128; buyin_app_id=1128; buyin_shop_type_v2=24; buyin_account_child_type_v2=1128; buyin_app_id_v2=1128; ecom_us_lt_buyin=bccf50782b1750d866af3e2a9a8109dd9d78fa2cf5ddce0779aa66eeb3ee3fa8; ecom_us_lt_ss_buyin=bccf50782b1750d866af3e2a9a8109dd9d78fa2cf5ddce0779aa66eeb3ee3fa8; BUYIN_SASID=SID2_7658489606759563556; ecom_us_lt_buyin_top=bccf50782b1750d866af3e2a9a8109dd9d78fa2cf5ddce0779aa66eeb3ee3fa8; ecom_us_lt_ss_buyin_top=bccf50782b1750d866af3e2a9a8109dd9d78fa2cf5ddce0779aa66eeb3ee3fa8;"
    }
    _page = 0
    _msToken = userinfo.get('msToken', '')
    result = api.getShopList(shop_id='182473628', page=_page, cookie_str=cookies, msToken=_msToken)
    dy_cookie = 'download_guide=%223%2F20260706%2F0%22; enter_pc_once=1; UIFID_TEMP=4f370c6d8fb718a382d31de50859ac71a63e1a5cc19a7a2de24e63803f467b413cabe378bcd6a6b159f4cccdf1df13310a250c128401629d52ae70efcb1414d8d95553b2f0fd844d9036b152d534dbd04ae5fb4992f1ed2ef0b0ac23b3699946b9bbfb8419897af74df03856c2723862; s_v_web_id=verify_mr81ywt2_olsxOosT_wDqW_4K70_8sab_0oYITF9ehQKR; dy_swidth=1707; dy_sheight=1067; hevc_supported=true; fpk1=U2FsdGVkX184wO9Pnvw1ndv3QaEHhd/kEN+Mkg5X5AgK+VtQYhO6YNuBHkHUCwOBzMlruYcR2hrUC1QdJNgQ4A==; fpk2=16fee37559dbd42b448204446d02089f; strategyABtestKey=%221783271776.336%22; passport_csrf_token=aecfc173c726d3d3a03292ef97ad77bb; passport_csrf_token_default=aecfc173c726d3d3a03292ef97ad77bb; bd_ticket_guard_client_web_domain=2; passport_assist_user=CkE_Z3ofToG1QAPoaEUkyMizufv6kH1S8w9LDWT41aYD-V0Bu1mJrxPg9o2yk-DlYqbfwxakFIq9Hn4wmUcVz48pIRpKCjwAAAAAAAAAAAAAUJ8dacd0MZo52vvREs6ysh2kOQYp-O7XY5tf7EkF_OdiNbS5pit1iYt474TKr34hUfYQoYOWDhiJr9ZUIAEiAQMDdY9l; n_mh=EyEgyFxFI5fiy-d_iT660NAbFEw22sfOXLkhKXhtwCs; sid_guard=c19554a5d142d2ac4746ca410d9ec0e3%7C1783271786%7C5184000%7CThu%2C+03-Sep-2026+17%3A16%3A26+GMT; uid_tt=eba75b5a7eec62e0401569abbce0981b; uid_tt_ss=eba75b5a7eec62e0401569abbce0981b; sid_tt=c19554a5d142d2ac4746ca410d9ec0e3; sessionid=c19554a5d142d2ac4746ca410d9ec0e3; sessionid_ss=c19554a5d142d2ac4746ca410d9ec0e3; session_tlb_tag=sttt%7C14%7CwZVUpdFC0qxHRspBDZ7A4__________YTdyD1AuufETbe47iZ4Uhstpf3pzyhqLLrD0n9vlu4zE%3D; is_staff_user=false; has_biz_token=false; sid_ucp_v1=1.0.0-KDc4ZDJlODg1NTIwMGQzMGNiNDgxYTQyNjdmM2UyZDAzNWRlZDJlZTAKIQj4ueCXiPTvAhDqoqrSBhjvMSAMMK3goPgFOAdA9AdIBBoCbHEiIGMxOTU1NGE1ZDE0MmQyYWM0NzQ2Y2E0MTBkOWVjMGUz; ssid_ucp_v1=1.0.0-KDc4ZDJlODg1NTIwMGQzMGNiNDgxYTQyNjdmM2UyZDAzNWRlZDJlZTAKIQj4ueCXiPTvAhDqoqrSBhjvMSAMMK3goPgFOAdA9AdIBBoCbHEiIGMxOTU1NGE1ZDE0MmQyYWM0NzQ2Y2E0MTBkOWVjMGUz; _bd_ticket_crypt_cookie=626e4312c1c40472566e59dd7409c3ef; __security_mc_1_s_sdk_sign_data_key_web_protect=34eef148-4d5f-bc50; __security_mc_1_s_sdk_cert_key=2da47526-4c83-b83e; __security_mc_1_s_sdk_crypt_sdk=58e87c28-45fb-84c2; __security_server_data_status=1; login_time=1783271785497; publish_badge_show_info=%220%2C0%2C0%2C1783271785927%22; DiscoverFeedExposedAd=%7B%7D; SelfTabRedDotControl=%5B%7B%22id%22%3A%227074567551921719304%22%2C%22u%22%3A202%2C%22c%22%3A0%7D%5D; UIFID=4f370c6d8fb718a382d31de50859ac71a63e1a5cc19a7a2de24e63803f467b413cabe378bcd6a6b159f4cccdf1df13310a250c128401629d52ae70efcb1414d8626c33bda95993e10afb3985a5795daab90d29a65f3bde86e63d86320f044162f69403a902b1f333c2657270bb92f232dd8318e4f3941a45120576d4706cc64fa0c2d3012df1bf9b7bf3259019d3787aaf892744bf5af0c592bcefc37f3fda18dcaa97797da8594b4c7fdea5e9c87847532665e444d6b9035212e822f916b067; ttwid=1%7CNMrtUFz2nQaW-Fi04DzK2GiNNdR5wFLZL7fctI_aRDk%7C1783271790%7Cbe59bec128862f9b50ac6cab384fe76ed0593aef79c4bf8e615e70109f51059f; is_dash_user=1; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; playRecommendGuideTagCount=1; totalRecommendGuideTagCount=1; __ac_signature=_02B4Z6wo00f010rG8TAAAIDAx25IuHOwWCtK5vWAALkG04; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAQ5zADansJK87lob69mserrY7ZF5taykVB1paHgO8APhx7dFs_YDkbWhVFf2dznp9%2F1783353600000%2F0%2F1783272683031%2F0%22; douyin.com; device_web_cpu_core=32; device_web_memory_size=16; architecture=amd64; is_support_rtm_web_ts=1; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1707%2C%5C%22screen_height%5C%22%3A1067%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A32%2C%5C%22device_memory%5C%22%3A16%2C%5C%22downlink%5C%22%3A1.5%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAQ5zADansJK87lob69mserrY7ZF5taykVB1paHgO8APhx7dFs_YDkbWhVFf2dznp9%2F1783353600000%2F0%2F1783345962556%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSERYRmw4YnFKcTJrWDRUMnRyNGVESWpUajh2cERPdk5nb0gzK3FhU0N3M1JyS0FSNWMxcG5QU1RheDF5UEZLV05PTmJUaUJreUVjUjNVYTR3QU5BZjg9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; biz_trace_id=cada1da9; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f2733343135323c303136363d3234272927676c715a75776a716a666a69273f2763646976602778; bit_env=WhnRlRnOvbwKhMpgRjAV9xpOcxxn1XY86-YD7eiZnnIqKO_AAIU3VZxek6SfP1Hw2E02ga3mKloPO51SHiHZNNZ4RVj7Lp3XuAaI0iE5v0DtSXNl_ngmR3eXTznfxzRkq_jTQ7osXUFSFPdjpjVJ-ojGVnytAiWogDeGgUPpNUrD-xsz5PXRSAyAf_a39qoev2GbI0W5OVII1cgLu2WyovSen1rWsiFTDgHeoLuVBf03lLim4gIdKlxQzpsvAxtmckRvznVMI4QjYPP7QxJr9LkJnfQdroQFvp_5_GSoeIqlRAv0gRscO5cXrH7s4N7QDBMVUkfVNKcEoAEkdwDxThH6gDfV2a_G_SUxcnImchZtayPtNsdFKLNdMXZrBHEf2lcEHu-ah757idrG2RjLpz3SrpYKyzmFsiRFqL8baum6V3CwF3hTBwwsmNRvyiME3pjgN0XXDPa-4zv-yzbhmiCgvqsUOgZ-aFj4MendmhjYO067p1DxPGxVkR-pRJRD; gulu_source_res=eyJwX2luIjoiN2M4YTc2ZWZiODlkOGY4ZWEzM2M0ZjM5OWM2MGY0Mjg5OTFmNmNmZjA5YTE5MmIxZTNhZjMzNzMxZjA2NDY3MSJ9; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJIRFhGbDhicUpxMmtYNFQydHI0ZURJalRqOHZwRE92TmdvSDMrcWFTQ3czUnJLQVI1YzFwblBTVGF4MXlQRktXTk9OYlRpQmt5RWNSM1VhNHdBTkFmOD0iLCJ0c19zaWduIjoidHMuMi4yYjA5YmVjNTEyZDZlYjQzMmNiYmUwZTI2MWM3OWEyOTAyZmQ2YmNjZmEyYjU4OWUyZDk4ZDBkMzJjZjgxMjVlYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiI3YXl5T2RzUHAzNUZFbm10dEpqNllxUEkyVW9ocDM0aU5iKzBnNHdYOGc4PSIsInNlY190cyI6IiMvbWpBdTdTQTdEQ2t2ZzNWcnhuTHpZUVFJSWZlTUozUE8rWWlzRFFOOExIOHkwQzNxUVhXd1VKNlFsZm0ifQ%3D%3D; odin_tt=770e502ba1e9523d0671bbea807e5950a0de491ac4cf3506da1472409e3a607bde8e4f00ef0c2706a8a0d6af4609ab331104e4b8068cfc6fd4376c12c2f5a81a; IsDouyinActive=false; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22'
    fp = dy_cookie.split('s_v_web_id=')[1].split(';')[0]
    uifid = dy_cookie.split('UIFID=')[1].split(';')[0]
    if not fp or not uifid:
        print("cookie不正确，请查看评论，使用评论接口的cookie")
        return {}
    douyinUserinfo = {
        'uifid': uifid,
        'fp': fp,
        'cookie': dy_cookie,
        'webid': '7658643419065959976',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'msToken': 'j7mYqo1pbBrzVXBU1d1lw4grxsaa7sPfXAwLvt8a-U_kxHh2a4Pr9LqG0y8n6w0_8fShqcb4IHSIKI_diP6L0aZ39YN4UJ00umS2wHCXzS6hyVvWdsK8UAGr3o0HXZQyaxFNj2HE-bdD_VIw-LzprjrS4bdsVt5w8aF0KdFS2AKgTKfECKMEBQ==',
    }
    json_data = json.loads(result)
    sku_info_list = []
    for data in json_data['data']['summary_promotions']:
        _promotion_id = data['promotion_id']
        _product_id = data['product_id']
        product_name = data['base_model']['product_info']['name']

        sku_result = api.getSku2(_product_id, douyinUserinfo)
        print("sku详情:", json.dumps(sku_result))
        skus = []
        sku_spec_dict = {}
        for sku_spec in sku_result['data']['specs']:
            sku_name = sku_spec['name']
            for sku_title in sku_spec['spec_items']:
                sku_spec_dict.update({
                    sku_title['id']: sku_name+":"+sku_title['name']
                })
        for sku_spec_id, sku_ids in sku_result['data']['skus'].items():
            sku_spec_list = sku_spec_id.split('_')
            if len(sku_spec_list) == 2:
                sku_name = sku_spec_dict.get(sku_spec_list[1]) + ' - ' + sku_spec_dict.get(sku_spec_list[0])
            else:
                sku_name = sku_spec_dict.get(sku_spec_list[0])
            sku_id = sku_ids['sku_id']
            skus.append({sku_id: sku_name})

        sks = [list(sk.keys())[0] for sk in skus]
        skul = [sks[i:i + 20] for i in range(0, len(sks), 20)]
        for skud in skul:
            print("skud", skud)
            skuPrice = api.getSkuPrice(_product_id, skud, douyinUserinfo)
            print("sku价格详情", json.dumps(skuPrice))
            sku_spec_dict = {}
            for pk in skuPrice['data']['shop_product_cards'][0]['invalid_product_cards']:
                sku_id = pk['sku_id']
                spec_info = pk['spec_info']
                # 简化sku名称,不要区服等信息,只取选中的结果
                sku_name = ','.join([sku_val['value'] for sku_val in spec_info])
                sku_spec_dict.update({sku_id: {
                    "sku_id": sku_id,
                    "sku_info": spec_info,
                    "sku_name": sku_name,
                    "sku_price": pk['price'],
                    "sku_image": pk['pic'],
                    "title": pk['title'],
                    "spec_info_desc": pk['spec_info_desc']
                }})

            sku_info_list.append({
                'product_name': product_name,
                'product_id': _product_id,
                'promotion_id': _promotion_id,
                'skus': sku_spec_dict,
            })
        print("汇总好的数据", sku_info_list)
    # 把结果存入本地
    with open('skus.json', 'w', encoding='utf-8') as f:
        json.dump(sku_info_list, f, ensure_ascii=False, indent=2)
    return sku_info_list


cid = 'd9ba8ae07d955b83c3b04280f3dc5a4a'

def run_buyin_sku(api, promotion_id, session_file=None):
    """Use the saved Chrome context and retain rotated session parameters."""
    path = (Path(session_file) if session_file is not None else
            Path(__file__).resolve().parent / 'fingerprintjs/private/chrome-session.json')
    session = json.loads(path.read_text('utf-8'))
    userinfo = session.get('userinfo')
    if not isinstance(userinfo, dict):
        raise ValueError('百应会话文件缺少 userinfo 对象')
    raw = api.getShopSku(promotion_id=str(promotion_id), userInfo=userinfo)
    try:
        result = json.loads(raw)
    except (ValueError, TypeError):
        return raw
    params = result.get('params') if isinstance(result, dict) else None
    if isinstance(params, dict) and params.get('cookie') and params.get('msToken'):
        session['promotion_id'] = str(promotion_id)
        session['userinfo'] = params
        path.write_text(json.dumps(session, ensure_ascii=False, indent=2), 'utf-8')
    return raw


if __name__ == '__main__':
    api = TikTokApi(cid)
    # device_id=1184648882315275 iid=7704017061957273145
    # cookie = "passport_csrf_token=0d7ccd6001f05818320183425ce06da9; passport_csrf_token_default=0d7ccd6001f05818320183425ce06da9; store-region=cn-jx; install_id=7704017061957273145; ttreq=1$9d284cedf8ea2b6de8b2916c1af255675013ebab; passport_mfa_token=Cja326%2FXYRcMLQPc7tNMpLmPNJC3tdwkZFn8asaeDvz%2BoilifzL2X10jJNrw0S16PEYztEWXN9caSgo8AAAAAAAAAAAAAFEgAaIREALG3E0FqFydz4UraRWm%2FkQeEIOqxjUFbHLBTf88iw1cc%2Bl2F%2F%2F7eXfiUK3gEOWroQ4Y9rHRbCACIgEDvuQyFg%3D%3D; d_ticket=7f0a3e1abce0ae407ce472e6a6e817bb2a0cb; multi_sids=4140102066118552%3A70e87315796a2961c288e7e05346e988; passport_assist_user=ClDhnvLmRVKHXugriJJbSJR_yT9qNhsVnfL7sxCwK1cixWRQDHFyoR0gj4Fa-eDdtAkHO7dokODFeOtMZ393VtfH1XsiLcZ9zs0LBA1vAJ2CphpKCjwAAAAAAAAAAAAAUSC9k6pO-Hgv_EjSWO-mTYoJZup9UVxOXOXk8qrjUai81xg8nHwUKO7-nXPMOGiR59gQ5auhDhiJr9ZUIAEiAQOkueRN; n_mh=RFTaY-jAojtCt7jWGcid8TjPYNkvtyNT6WLQMlafxgE; sid_guard=70e87315796a2961c288e7e05346e988%7C1794393816%7C5184000%7CSun%2C+10-Jan-2027+10%3A43%3A36+GMT; uid_tt=d657a6c64dc79a3ffca9aa0d702c02a9; uid_tt_ss=d657a6c64dc79a3ffca9aa0d702c02a9; sid_tt=70e87315796a2961c288e7e05346e988; sessionid=70e87315796a2961c288e7e05346e988; sessionid_ss=70e87315796a2961c288e7e05346e988; session_tlb_tag=sttt%7C15%7CcOhzFXlqKWHCiOfgU0bpiP_________wnyFI5fclNl86_bLVJ31zFADsYva37XxTJCZQDZOWsDQ%3D; is_staff_user=false; has_biz_token=false; store-region-src=uid; ticket_guard_has_set_public_key=1; odin_tt=7cd8e23bbdfc4537601b9ec7684016aa50a9f80a6c7bc2c86326f2b82fffdac76afdfe7ff46daf1b15fb2197425689360404dff0245b678ec0187a9dbc63b7b5eed1939492fe8d68915cff8b631bf6bc"
    # device = {"iid": "3506821196193386", "device_id": "3506821196189290", "klink_egdi": "AAJZ4JuyIl59E6nQJratgj5Ho-GmYJ8zKTvYlPg49Zqrrd91xiUw-8Ma", "device_token": "AAA4VU3TOEBKBTRWB7M6SS7T32IAWZQT665HKBSS7SDNGSQN76SYCKZY5MKJZO5DVWQ2466KI4IPVOZ43XTNLU3QZLR2LHPR32UNGH5EGWI4GEFS62P6TEREX7HWU", "cdid": "43d17ed3-10d8-454c-8cfe-d552aad9d6a9", "dtrait_token": "v0_WsaRWyYmkQIiQw+GfJ3AesHmzkHb+bRgySLA24PXCmlQUBSDuBSmHSXJ6sNIO3S5Y7y58Ly0e9d6FrfytmEzZ4HoiHphMAs4KO6aJN3Khp9/olX0eZaqdhvR5lTIxP/XO/UtOjXg06Di0nQCpYvz/kxs1ACqzuQj7thBpv5x1bpeec0QAuVHxImhit3u6r2Y"}
    ApiInfo = api.get_ApiInfo()
    print('Api信息:' + ApiInfo)
    # app取设备号
    device = api.get_device()
    video_id = '7401951329180077331'
    print("发送验证码", api.app_send_code('',device))
    # print("评论详情", api.app_comment_list(video_id, device))
    # print("播放上报", api.app_play_report(video_id, device, ''))
    # api.getlive()



    # api.get_ac_sign('')
    # cookie = ''
    # 测试直播间关注主播
    live_url = 'https://v.douyin.com/Grx06q_bJzA/'
    sec_uid = 'MS4wLjABAAAA-IKEOrbtAzyhs8zgkOCqexwIF6qVkWFpfCinfHrBp4ILWyZpU6a4py7Bk90h84ts'
    # api.live_relation(sec_uid, live_url)

    # 发送消息示例
    # api.sendMessage('哎哟~你干嘛')

    # 通过直播链接转直播间id https://v.douyin.com/iYLUkS3o/
    # res = api.get_room_info(live_url)
    # room_id = res['data']['room']['id_str']
    # uid = res['data']['room']['owner_user_id']
    # sec_uid = res['data']['room']['owner']['sec_uid']
    # web_rid = res['data']['room']['owner']['web_rid']
    # status = res['data']['room']['status']
    # st = "正在直播" if status == 2 else "下播了"
    # print(st)
    # print('sec_uid', sec_uid)
    # print('room_id', room_id)
    # print('uid', uid)
    # print('web_rid', web_rid)

    # web版获取cookie
    # cookie: str = api.get_web_cookie()
    # print('ret_cookie:', cookie)
    page = 0

    # device_id = device['data'][0]['device_id']
    # iid = device['data'][0]['install_id']
    # ttdt = device['data'][0]['device_token']

    # web获取视频信息
    video_list = [7613474260056684874]
    # api.get_video_info(video_list)

    # 获取作品列表
    # api.get_video_list('100698990140')
    # api.get_shop_product('MS4wLjABAAAAU9dYHqMwYvVV9_pF479JEqAWPYxEGYjJcLU-T4GNqNk')
    # api.get_video(sec_uid, page=str(page), iid="3138482516028953", device_id="4297303816414455")

    # web版获取小黄车商品
    # api.get_web_promotions(room_id=room_id, uid=uid, web_rid=web_rid)

    # 获取web评论示例
    # api.get_web_comment(video_id, 0)

    # xbogus,abogus示例
    # uri = "aavid=1846697808765961&gfversion=1.0.1.7602&verifyFp=verify_mh266pqw_M6bkfbLw_qe7x_4vhr_BQJw_8jxayRZLfPND&fp=verify_mh266pqw_M6bkfbLw_qe7x_4vhr_BQJw_8jxayRZLfPND&msToken=au2xtVfD8sIgM-yYZCa70oQfqo1zodY1C-AYAkrRleKknsJohb61Irp_eOX1QuvNfD2aeFJF_ZrV6bFgKFSTwaKCTJEI0xuEiqO3XzDpLeY_0sytndMhVMvT64nSvrI%3D&msToken=au2xtVfD8sIgM-yYZCa70oQfqo1zodY1C-AYAkrRleKknsJohb61Irp_eOX1QuvNfD2aeFJF_ZrV6bFgKFSTwaKCTJEI0xuEiqO3XzDpLeY_0sytndMhVMvT64nSvrI%3D"
    # body = '{"ModuleId":"7469344271120744486","FilterParams":{},"aavid":"1846697808765961"}'
    # ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    # api.getABogus(uri, ua, body, 'qc')
    # api.getxBogus('https://ttwid.bytedance.com/ttwid/union/register/?msToken=1231231312321312312123123123213')
    # api.encode_login('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTgxMjg1Njk1MjMsImV4cCI6MTc1ODEyOTE2OTUyM30.PUjc7T8yRwuAE-1p2sVVQIPM_YOw_RxzIOYOLLQT6Ro', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')

    keyword = quote('哈士奇')

    # app视频搜索
    # api.get_keyword("0", "0", keyword, "12")

    # 获取评论示例
    # device_id=4323692175176509 install_id=2184085302687243
    # api.get_comment(video_id, device_id=device_id, iid=iid, page='20', ttdt=ttdt)
    # api.get_old_comment(video_id, page="30")

    # 获取用户信息
    # api.get_userinfo(sec_uid)

    # 通过链接查询商品信息
    # api.JuLiang_BatchLink(
    #     "https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3725012931763634178,https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3654381246617882711"
    # )

    cookies = 's_v_web_id=verify_mtth3x8u_vqK1wU4f_V1W4_4Gn0_9j3i_92onnaIwbZml; passport_csrf_token=0f265254ea21a789ccee1052cb9907a0; passport_csrf_token_default=0f265254ea21a789ccee1052cb9907a0; is_staff_user=false; has_biz_token=false; qc_tt_tag=0; ttwid=1%7CKifMDj-B_NmN5MCT00jeQTXDmTV6m3WZjrIllLseMBY%7C1793448100%7C981e6afa8d6924425f1c51da8be921e333476ba16d8d7915922bce43f808710d; odin_tt=c39116e3e5bb78458f78350778da205e239e32cef8f0067ba0e995e4fee5291234d3e6f2252bb4fc149ef23576325745783690711f16ffcae5cc045c447b7bb9; passport_auth_status=d4113eff0a72e05851f59213177522a3%2C; passport_auth_status_ss=d4113eff0a72e05851f59213177522a3%2C; buyin_shop_type=24; buyin_shop_type_v2=24; buyin_account_child_type_v2=1128; buyin_app_id_v2=1128; _tea_utm_cache_3813=undefined; gfkadpd=2631,22740; ucas_c0_buyin=CkEKBTEuMC4wEKuIkN65i4P1ahi9LyCb2eGWoK3hAyiPETCK8YDZ8K24A0DsmKjXBkjszOTZBlCavLW8s8SF0GpYfhIUV3CAzdiKo9ztNABjGENaWU73osQ; ucas_c0_ss_buyin=CkEKBTEuMC4wEKuIkN65i4P1ahi9LyCb2eGWoK3hAyiPETCK8YDZ8K24A0DsmKjXBkjszOTZBlCavLW8s8SF0GpYfhIUV3CAzdiKo9ztNABjGENaWU73osQ; sid_guard=72080d5dd5d6c706a8686a1be4eec36b%7C1793723500%7C5184000%7CSat%2C+02-Jan-2027+16%3A31%3A40+GMT; uid_tt=d035d9bf9101235a888947d2c6f6578a; uid_tt_ss=d035d9bf9101235a888947d2c6f6578a; sid_tt=72080d5dd5d6c706a8686a1be4eec36b; sessionid=72080d5dd5d6c706a8686a1be4eec36b; sessionid_ss=72080d5dd5d6c706a8686a1be4eec36b; session_tlb_tag=sttt%7C1%7CcggNXdXWxwaoaGob5O7Da__________Uz3gXivc92IlKOMI_D4iqSbBa38QpgWEDLPTObnGEKx0%3D; sid_ucp_v1=1.0.0-KDZkN2ZlY2I5Mjg2MTRlNzAwM2VhNzI0NmUzZGYwYmUzOGEwN2M3ZDQKFgiK8YDZ8K24AxDsmKjXBhiPETgIQCYaAmhsIiA3MjA4MGQ1ZGQ1ZDZjNzA2YTg2ODZhMWJlNGVlYzM2Yg; ssid_ucp_v1=1.0.0-KDZkN2ZlY2I5Mjg2MTRlNzAwM2VhNzI0NmUzZGYwYmUzOGEwN2M3ZDQKFgiK8YDZ8K24AxDsmKjXBhiPETgIQCYaAmhsIiA3MjA4MGQ1ZGQ1ZDZjNzA2YTg2ODZhMWJlNGVlYzM2Yg; SASID=SID2_7703983414944989501; BUYIN_SASID=SID2_7703983414944989501; buyin_account_child_type=1128; buyin_app_id=1128; ecom_us_lt_buyin_top=cc7a86f7ff9a1b50cab491c4b7a8c822ac0298d1b1ec6714eb3b5d66fb9ded2b; ecom_us_lt_ss_buyin_top=cc7a86f7ff9a1b50cab491c4b7a8c822ac0298d1b1ec6714eb3b5d66fb9ded2b; ecom_us_lt_buyin=cc7a86f7ff9a1b50cab491c4b7a8c822ac0298d1b1ec6714eb3b5d66fb9ded2b; ecom_us_lt_ss_buyin=cc7a86f7ff9a1b50cab491c4b7a8c822ac0298d1b1ec6714eb3b5d66fb9ded2b; scmVer=1.0.2.2100; tt_scid=lw9XTcEZUeuANYfJGGvVgkCGpD1YOlqn0ejOJ39RCNxWX-wEzK.OgXKYLm1ZSXyuc5d2; csrf_session_id=e56066920570dc7bd8f87d8b0e00ec51'
    if not cookies:
        print("请输入cookie")
    # test()
    # test2()
    # "product_id":"3804415375286862084","promotion_id":"3808579876391354600"
    # headers = api.JuLiangHeaders(cookie_str=cookies)
    # print(headers)
    # uuid_str = str(uuid.uuid4())
    # msToken = api.getMsToken(head=headers, uuid_str=uuid_str)
    # print("生成msToken", msToken)
    # msToken = api.getMsToken(head=headers, msToken=msToken, uuid_str=uuid_str)
    # print("更新msToken", msToken)
    # strData = "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"
    # decrypt_strData = api.decryptStrData(strData)
    # print(decrypt_strData)
    # print("strData解密：", json.dumps(json.loads(decrypt_strData['plaintext']), indent=2))
    # decrypt_strData = open(r'ewid/demo2.json', encoding='utf-8').read()
    # encrypt_strData = api.encryptStrData(json.dumps(json.loads(decrypt_strData), separators=(',',":")))
    # print("strData加密：", encrypt_strData)
    #
    # print(len(encrypt_strData))
    msToken = 'fl8ZUZ9-9VieGFp_-vPmHSizqHyTJNW_XEvRabxjZH-0xCatcOPDPLNdVj8I-DG1C734vlpPH_qWEYaYhOJj-CrV3r7kuadJamOwDo6Ded6iO_bFCBPKPrYL_kQgsxuCOA1-EH0-_xA7wqxFfV3mZe64AMcXL2qM6_MLLFusHuCWNa5n3Dtdog=='
    csrf_token = ''
    _promotion_id = '3764711900810707138'
    # sku_result = run_buyin_sku(api, _promotion_id)
    # sku_result = json.loads(sku_result)
    # params_sku = sku_result['params']
    # sku_result_json = json.loads(sku_result['response'])
    # print("商品sku_response:::", sku_result_json)
    #
    # msToken = params_sku['msToken']
    # csrf_token = params_sku['csrf_token']
    #
    # print("msToken", msToken)
    # print("csrf_token", csrf_token)

    # 店铺商品
    # api.getShopList(shop_id='182473628', page=0, cookie_str=cookies, msToken=msToken)

    # 商品详情/销量（使用现成API仅支持Windows谷歌浏览器149版本）
    # shop_result = api.JuLiang_ShopInfo(promotion_id=promotion_id, cookie_str=cookies, msToken=msToken, csrf_token=csrf_token)
    # shop_result = json.loads(shop_result)
    # params_shop = shop_result['params']
    # shop_result_json = json.loads(shop_result['response'])
    # print("商品详情response:::", shop_result_json)
    #
    # msToken = params_shop['msToken']
    # csrf_token = params_shop['csrf_token']
    #
    # print("msToken", msToken)
    # print("csrf_token", csrf_token)



    # 选品广场
    # api.JuLiang_material_list()




    # 生成Cookie bd_ticket_guard_client_data
#     result = api.getBd()
#
#     # 生成Headers bd_ticket_guard_client_data 下面X509cert仅为示例非固定
#     X509cert = """
#     -----BEGIN CERTIFICATE-----
# MIIEfTCCBCKgAwIBAgIUXWdS2tzmSoewCWfKFyiWMrJqs/0wCgYIKoZIzj0EAwIw
# MTELMAkGA1UEBhMCQ04xIjAgBgNVBAMMGXRpY2tldF9ndWFyZF9jYV9lY2RzYV8y
# NTYwIBcNMjIxMTE4MDUyMDA2WhgPMjA2OTEyMzExNjAwMDBaMCQxCzAJBgNVBAYT
# AkNOMRUwEwYDVQQDEwxlY2llcy1zZXJ2ZXIwWTATBgcqhkjOPQIBBggqhkjOPQMB
# BwNCAASE2llDPlfc8Rq+5J5HXhg4edFjPnCF3Ua7JBoiE/foP9m7L5ELIcvxCgEx
# aRCHbQ8kCCK/ArZ4FX/qCobZAkToo4IDITCCAx0wDgYDVR0PAQH/BAQDAgWgMDEG
# A1UdJQQqMCgGCCsGAQUFBwMBBggrBgEFBQcDAgYIKwYBBQUHAwMGCCsGAQUFBwME
# MCkGA1UdDgQiBCABydxqGrVEHhtkCWTb/vicGpDZPFPDxv82wiuywUlkBDArBgNV
# HSMEJDAigCAypWfqjmRIEo3MTk1Ae3MUm0dtU3qk0YDXeZSXeyJHgzCCAZQGCCsG
# AQUFBwEBBIIBhjCCAYIwRgYIKwYBBQUHMAGGOmh0dHA6Ly9uZXh1cy1wcm9kdWN0
# aW9uLmJ5dGVkYW5jZS5jb20vYXBpL2NlcnRpZmljYXRlL29jc3AwRgYIKwYBBQUH
# MAGGOmh0dHA6Ly9uZXh1cy1wcm9kdWN0aW9uLmJ5dGVkYW5jZS5uZXQvYXBpL2Nl
# cnRpZmljYXRlL29jc3AwdwYIKwYBBQUHMAKGa2h0dHA6Ly9uZXh1cy1wcm9kdWN0
# aW9uLmJ5dGVkYW5jZS5jb20vYXBpL2NlcnRpZmljYXRlL2Rvd25sb2FkLzQ4RjlD
# MEU3QjBDNUE3MDVCOTgyQkU1NTE3MDVGNjQ1QzhDODc4QTguY3J0MHcGCCsGAQUF
# BzAChmtodHRwOi8vbmV4dXMtcHJvZHVjdGlvbi5ieXRlZGFuY2UubmV0L2FwaS9j
# ZXJ0aWZpY2F0ZS9kb3dubG9hZC80OEY5QzBFN0IwQzVBNzA1Qjk4MkJFNTUxNzA1
# RjY0NUM4Qzg3OEE4LmNydDCB5wYDVR0fBIHfMIHcMGygaqBohmZodHRwOi8vbmV4
# dXMtcHJvZHVjdGlvbi5ieXRlZGFuY2UuY29tL2FwaS9jZXJ0aWZpY2F0ZS9jcmwv
# NDhGOUMwRTdCMEM1QTcwNUI5ODJCRTU1MTcwNUY2NDVDOEM4NzhBOC5jcmwwbKBq
# oGiGZmh0dHA6Ly9uZXh1cy1wcm9kdWN0aW9uLmJ5dGVkYW5jZS5uZXQvYXBpL2Nl
# cnRpZmljYXRlL2NybC80OEY5QzBFN0IwQzVBNzA1Qjk4MkJFNTUxNzA1RjY0NUM4
# Qzg3OEE4LmNybDAKBggqhkjOPQQDAgNJADBGAiEAqMjT5ADMdGMeaImoJK4J9jzE
# LqZ573rNjsT3k14pK50CIQCLpWHVKWi71qqqrMjiSDvUhpyO1DpTPRHlavPRuaNm
# ww==
# -----END CERTIFICATE-----
#     """
#     result = json.loads(result)
#     t = "ticket=hash.5mRugUrX7/8qSW6JIhH7Os7aABLOCjxPbjLDf3hdnKc=&path=/webcast/user/relation/update/&timestamp=1758810234"
#     api.getBd(result['privateKey'], X509cert, t)
