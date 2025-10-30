# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import json
import random
import time
import re
from urllib.parse import urlencode, quote, urljoin
import requests
import math
import douyin_pb2
from google.protobuf.json_format import ParseDict
import uuid



class TikTokApi:
    host = 'http://api2.52jan.com'

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
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign

        data = {
            'url': url,
            'ua': ua,
            'data': data,
            't': t,
            'sign': sign
        }
        resp = requests.post(sign_url, data=data, headers=header).json()
        print('aBogus:', resp['abogus'], 'aBogus长度:', len(resp['abogus']))
        return resp

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

    def get_xgorgon(self, url, cookie, params, ver, headers=None):
        """
        获取x-gorgon
        :param url:
        :param cookie:
        :param params: post提交
        :param ver: 版本号
        :param headers:
        :return:
        """
        sign_url = TikTokApi.host + '/dyapi/xgorgon'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign
        self.array['url'] = url
        self.array['sign'] = sign
        self.array['cookie'] = cookie
        self.array['ver'] = ver
        self.array['params'] = params
        self.array['headers'] = json.dumps(headers)
        resp = requests.post(sign_url, data=self.array, headers=header)
        print('xgorgon', resp.text)
        return resp.json()

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

    def get_device(self):
        """
        获取设备号
        :return:
        """
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign
        params = {
            'sign': sign,
            'set_ip': '0',
            'num': '1'
        }

        """
        set_ip：0=随机设备池，1=根据ip分配固定设备池
        num: 获取设备的数量
        """
        device_url = TikTokApi.host + '/dyapi/get_device'
        resp = requests.post(device_url, data=params, headers=header)
        print('设备id:', resp.text)
        return resp.json()

    def __md5(self, string):
        post_data = gzip.compress(bytes(json.dumps(string), encoding="utf8"))
        m = hashlib.md5()
        m.update(bytes(post_data))
        str_md5 = m.hexdigest()
        return str_md5.upper()

    def get_shop_product(self, uid):
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
        sig = self.get_xgorgon(uri, headers["Cookie"], '', 'max', headers)
        headers.update(sig)
        # headers["X-Gorgon"] = sig["xgorgon"]
        # headers["X-Khronos"] = sig["xkhronos"]
        # headers["X-SS-REQ-TICKET"] = sig["X-SS-REQ-TICKET"]
        res = requests.get(uri, headers=headers, proxies=proxies).text
        print("橱窗列表", res)
        return res

    def get_keyword(self, device_id, iid, keyword, page):
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
        sig = self.get_xgorgon(url, '', urlencode(data), 'max', headers)
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

        sig = self.get_xgorgon(url, '', '', 'max', headers)
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

    def JuLiangHeaders(self, cookie=''):
        return {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'cookie': cookie,
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Google Chrome";v="139", "Chromium";v="139", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
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

    def JuLiang_ShopSku(self, biz_id, cookies=None):
        """
        通过商品ID查询商品规格
        :param cookies:
        :param biz_id:
        :return:
        """

        headers = self.JuLiangHeaders(cookies)
        headers.update({"content-type": "application/json"})

        data = {"scene_info": {"request_page": 2}, "other_params": {}, "biz_id": biz_id, "biz_id_type": 2,
                "enter_from": "pc.shopwindow.goods_manager", "data_module": "dynamic",
                "dynamic_params": {"param_type": 6}, "extra": {"seraph_did": ""}}
        fp = TikTokApi.get_cookie_value_oneliner(cookies, 's_v_web_id')
        msToken = TikTokApi.get_cookie_value_oneliner(cookies, 'msToken') or ""
        params = {
            'verifyFp': fp,
            'fp': fp,
            'msToken': msToken
        }
        url = "https://buyin.jinritemai.com/pc/selection/decision/pack_detail?" + urlencode(params)
        data = json.dumps(data, separators=(',', ':'))
        a_bogus = self.getABogus(url, ua=headers["user-agent"], t="ju", data=data)
        url += "&a_bogus=" + a_bogus['abogus']
        resp = requests.post(url, data=data, headers=headers).text
        print("巨量百应商品规格:", resp)
        return resp

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

    def get_video(self, secUid, page="0", iid='', device_id=''):
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

        sig = self.get_xgorgon(url, '', '', 'max', headers)
        headers.update(sig)
        response = requests.get(url, headers=headers)
        print("作品列表", response.text)
        # if len(response.json()['aweme_list']) == 0:
        #     print(url)
        return response

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
        url = TikTokApi.host + '/video_info'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts
        }
        sign = self.set_sign
        byte = requests.post(url, data={'video_list': str(video), 'sign': sign}, headers=header).content
        resp = gzip.decompress(byte).decode('utf-8')
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
        try:
            result = douyin_pb2.RequestMessage()
            ParseDict(data, result)
            serialized_data = result.SerializeToString()
            print("长度：", len(serialized_data))
            print("序列化后的二进制数据：", serialized_data)
            print("hex：", serialized_data.hex())
        except Exception as e:
            print(e)

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


if __name__ == '__main__':
    api = TikTokApi('d9ba8ae07d955b83c3b04280f3dc5a4a')
    cookie = ""
    device = {}
    ApiInfo = api.get_ApiInfo()
    print('Api信息:' + ApiInfo)

    # app取设备号
    # device = api.get_device()

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
    video_id = '7361479239318768950'
    page = 0

    # device_id = device['data'][0]['device_id']
    # iid = device['data'][0]['install_id']
    # ttdt = device['data'][0]['device_token']

    # web获取视频信息
    # video_list = [7444518837912964388,7445547661677169931,7456796563868765450]
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

    # 通过链接查询巨量百应商品信息
    # api.JuLiang_BatchLink(
    #     "https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3725012931763634178,https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3654381246617882711")

    cookies = 'ttcid=3d3c0f31a1d241e89c75dfceaa639b1e12; tt_scid=96aEmVJNCjafaBr2oRytoHoyOvgQSllyuKshmVpGy4be3Z76VBqzSpqT-34emy9Df872; gfkadpd=2631,22740; s_v_web_id=verify_mgt4m2b8_2BTffP9a_0O1O_4My9_Agx8_si5a1bOXk8Cr; passport_csrf_token=255c9518da7aa75d341f370f063faffa; passport_csrf_token_default=255c9518da7aa75d341f370f063faffa; ttwid=1%7CA62kHO_fEpUzz34QER10djeGm09OKGPwPjN59Q1_eUQ%7C1760598336%7C5f53d9e9e12266416d2691ebb712c6eded8119377538888d1f2f947c8e941770; odin_tt=e2d610c30508df90fe9790054bc82a4376941c9a1cbcc02dcf000d844e8472d0714ba7d71fb3bfdd6f8c2476caf3846984d97e1a273e2b898bbb719246009239; passport_auth_status=819ca882b87945ed2606c412cb0d3cd8%2C; passport_auth_status_ss=819ca882b87945ed2606c412cb0d3cd8%2C; uid_tt=d1bc2145ae5050470acf3e55382d9e7d; uid_tt_ss=d1bc2145ae5050470acf3e55382d9e7d; sid_tt=3a0f1968049244dfdaedc18042f45941; sessionid=3a0f1968049244dfdaedc18042f45941; sessionid_ss=3a0f1968049244dfdaedc18042f45941; is_staff_user=false; ucas_c0_buyin=CkEKBTEuMC4wEICIiPT7p6n4aBi9LyCEnaDIisztBiiPETDt4ICur_TDBEDBysLHBkjB_v7JBlCzvJjOic_8hWZYfhIURpdytysio_tjYlV5itdwZJhXUmc; ucas_c0_ss_buyin=CkEKBTEuMC4wEICIiPT7p6n4aBi9LyCEnaDIisztBiiPETDt4ICur_TDBEDBysLHBkjB_v7JBlCzvJjOic_8hWZYfhIURpdytysio_tjYlV5itdwZJhXUmc; sid_guard=3a0f1968049244dfdaedc18042f45941%7C1760601409%7C5184000%7CMon%2C+15-Dec-2025+07%3A56%3A49+GMT; session_tlb_tag=sttt%7C13%7COg8ZaASSRN_a7cGAQvRZQf_________istwuinrDSNvM6wQqg3A14jNkAPFEBndlXcJ6EuKU3VA%3D; sid_ucp_v1=1.0.0-KGRhMmViOWM2YzdiODllNTI3ZTgxYTE2YTI4ZmM2YzI4NWI4OTAwNWMKGAjt4ICur_TDBBDBysLHBhiPESAMOAhAJhoCbHEiIDNhMGYxOTY4MDQ5MjQ0ZGZkYWVkYzE4MDQyZjQ1OTQx; ssid_ucp_v1=1.0.0-KGRhMmViOWM2YzdiODllNTI3ZTgxYTE2YTI4ZmM2YzI4NWI4OTAwNWMKGAjt4ICur_TDBBDBysLHBhiPESAMOAhAJhoCbHEiIDNhMGYxOTY4MDQ5MjQ0ZGZkYWVkYzE4MDQyZjQ1OTQx; SASID=SID2_7561723820806848810; BUYIN_SASID=SID2_7561723820806848810; buyin_shop_type=24; buyin_account_child_type=1128; buyin_app_id=1128; buyin_shop_type_v2=24; buyin_account_child_type_v2=1128; buyin_app_id_v2=1128; x-web-secsdk-uid=056e66e9-5d42-4737-b6dc-cb851d7a81bc; _tea_utm_cache_3813=undefined; scmVer=1.0.1.9400; csrf_session_id=6cec376249cb8e423b09e7a6f93b2cdd'
    # 通过商品id查询巨量百应商品规格
    # api.JuLiang_ShopSku(biz_id='3723383251344225544', cookies=cookies)

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
