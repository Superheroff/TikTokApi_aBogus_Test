# -*- coding: utf-8 -*-
import gzip
import hashlib
import json
import random
import time
from urllib.parse import urlencode, quote
import requests


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

    def get_web_xbogus(self, url, ua):
        """
        获取web xbogus
        :param url:
        :param ua:
        :return:
        """
        sign_url = TikTokApi.host + '/dyapi/web/xbogus'
        ts = str(time.time()).split('.')[0]
        header = {
            'cid': self.cid,
            'timestamp': ts,
            'user-agent': 'okhttp/3.10.0.12'
        }
        sign = self.set_sign
        params = {
            'url': url,
            'ua': ua,
            'sign': sign
        }
        resp = requests.post(sign_url, data=params, headers=header).json()
        print('web_xbogus', resp)
        return resp

    def get_web_abogus(self, url, ua, data=None, ck=None, t=None):
        """
        获取a_bogus
        :param url:
        :param ua:
        :param data:
        :param ck:
        :param t: aBogus版本,默认douyin=1.0.1.19-fix,ju_old=巨量百应1.0.1.15,tuan=团长1.0.1.15,ju=巨量百应1.0.1.20,doudian=1.0.1.1
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
        '''
        获取x-gorgon
        :param url:
        :param cookie:
        :param params: post提交
        :param ver: 版本号
        :param headers:
        :return:
        '''
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
        '''
        获取设备号
        :return:
        '''
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
        a_bogus = self.get_web_abogus(url, ua=headers["User-Agent"], ck=headers["Cookie"])
        resp = requests.get(url + "&a_bogus=" + a_bogus['abogus'], headers=headers).text
        print('web评论列表：', resp)
        return resp

    def JuLiang_BatchLink(self, urls):
        """
        通过链接查询巨量百应商品信息，最大30个链接
        :param urls:
        :return:
        """

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'store-region-src=uid; d_ticket=c3a7b78fda67d3bac21947bb685f2927ad046; passport_assist_user=CkFo7-ugFSgwppENxw1SrEZftnHaTSpfxVZkA5nB2P4aAoWw_ysNzIS9DPPQfrPDU0iZxOrxidVGdNFL7crdvCMwQBpKCjyhtj4u9Ea0p6lU1CYrOIqxzR8XfSOcOdVYK5Irzzf5x6vFNiEpyJT9T92zkfHVR8E_8MRQCEwEj4WNeXsQl4LgDRiJr9ZUIAEiAQM8UGI0; n_mh=RFTaY-jAojtCt7jWGcid8TjPYNkvtyNT6WLQMlafxgE; s_v_web_id=verify_m3pyuj09_e02851c6_fd50_d7b8_87c0_6d97774e8d52; is_staff_user=false; scmVer=1.0.1.8354; passport_csrf_token=ce347ff5549b3331313257c903352196; passport_csrf_token_default=ce347ff5549b3331313257c903352196; passport_auth_status=04a9e3a860e65aa088eb10b48a9658de%2C; passport_auth_status_ss=04a9e3a860e65aa088eb10b48a9658de%2C; COMPASS_LUOPAN_DT=session_7456021435276656905; gfkadpd=2631,22740; _tea_utm_cache_3813=undefined; tt_scid=3rX58QFJZgSEYheu5b4Q909Qp-KZWDPl3EYqEwIMwiMykv-mywuUNc.kvZ2neluI2b90; csrf_session_id=a789b0479559d484ecdc4f0a8901cede; ttwid=1%7CuHZhz1_1r4fU9_DbK9Oopb8Et_Iji8UCAF3dEOKarqg%7C1736238285%7Cefaa6044f2c28fd32fb162217f97773ac2de1841b696a406ef947d18e0fe15e2; uid_tt=1c7bbdbf8cd13bf45f556ec146bb6118; uid_tt_ss=1c7bbdbf8cd13bf45f556ec146bb6118; sid_tt=25dd573ef51b1cb8dd6271862ecd8b53; sessionid=25dd573ef51b1cb8dd6271862ecd8b53; sessionid_ss=25dd573ef51b1cb8dd6271862ecd8b53; store-region=cn-jx; odin_tt=a629d196ad7e3f2e91b59a1ad6051b4776cb8eb4664293599167ec8b1d4d6f1bb4f47eb98f73966fb0f15586cc465b88d5a71d62c6f93c502d986e590d88e85a; ucas_c0_buyin=CkEKBTEuMC4wEKOIksC6mbm-Zxi9LyCEnaDIisztBiiPETDt4ICur_TDBEDQyfO7BkjQ_a--BlCzvJjOic_8hWZYfhIUh8L-HM62z5bY9QsNw1_ppZNRHT8; ucas_c0_ss_buyin=CkEKBTEuMC4wEKOIksC6mbm-Zxi9LyCEnaDIisztBiiPETDt4ICur_TDBEDQyfO7BkjQ_a--BlCzvJjOic_8hWZYfhIUh8L-HM62z5bY9QsNw1_ppZNRHT8; sid_guard=25dd573ef51b1cb8dd6271862ecd8b53%7C1736238289%7C5183999%7CSat%2C+08-Mar-2025+08%3A24%3A48+GMT; sid_ucp_v1=1.0.0-KDI0ZTIyMjMyMzBjYzIwY2IxMGIyMDA5YWZlZTYzMzQ1MWJmNmE1ZTEKGAjt4ICur_TDBBDRyfO7BhiPESAMOAhAJhoCbHEiIDI1ZGQ1NzNlZjUxYjFjYjhkZDYyNzE4NjJlY2Q4YjUz; ssid_ucp_v1=1.0.0-KDI0ZTIyMjMyMzBjYzIwY2IxMGIyMDA5YWZlZTYzMzQ1MWJmNmE1ZTEKGAjt4ICur_TDBBDRyfO7BhiPESAMOAhAJhoCbHEiIDI1ZGQ1NzNlZjUxYjFjYjhkZDYyNzE4NjJlY2Q4YjUz; SASID=SID2_7457082378843832602; BUYIN_SASID=SID2_7457082378843832602; buyin_shop_type=24; buyin_account_child_type=1128; buyin_app_id=1128; buyin_shop_type_v2=24; buyin_account_child_type_v2=1128; buyin_app_id_v2=1128',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://buyin.jinritemai.com/dashboard/shopwindow/goods-list?pre_universal_page_params_id=&universal_page_params_id=b1325880-cca4-4d55-9d0b-314bb57c14b0',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
        }

        params = {
            'urls': urls,
            'scene': '1',
            'verifyFp': 'verify_m3pyuj09_e02851c6_fd50_d7b8_87c0_6d97774e8d52',
            'fp': 'verify_m3pyuj09_e02851c6_fd50_d7b8_87c0_6d97774e8d52',
            'request_from': '203',
            'msToken': 'rde3LdGvoz2yzQsg44ISndxp2uowmjOQq1NfjcVkejAeWrJX4bYxH2Hmha3nKzm_9ZJZfTWvcgCIC79AD3pGS3nmWNIF13AdoUaBI3PQizM5QG5fMV6Ger5sk-XpRKg2Y7svs3LL-1Z_9UbrR6Wwuau2PuP_ZRfQ31TopsP1YWyz'
        }
        a_bogus = self.get_web_abogus(urlencode(params), ua=headers["user-agent"], t="ju")
        params['a_bogus'] = a_bogus['abogus']
        resp = requests.get("https://buyin.jinritemai.com/pc/selection_tool/batch_link", params=params,
                            headers=headers).text
        print("巨量百应商品信息:", resp)
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
        abogus = self.get_web_abogus(url, headers["User-Agent"], headers["Cookie"])
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

    # 通过直播链接转直播间id https://v.douyin.com/iYLUkS3o/
    live_url = 'https://v.douyin.com/ihF24589/'
    res = api.get_room_info(live_url)
    room_id = res['data']['room']['id_str']
    uid = res['data']['room']['owner_user_id']
    web_rid = res['data']['room']['owner']['web_rid']
    status = res['data']['room']['status']
    st = "正在直播" if status == 2 else "下播了"
    print(st)
    print('room_id', room_id)
    print('uid', uid)
    print('web_rid', web_rid)

    # web版获取cookie
    # cookie: str = api.get_web_cookie()
    # print('ret_cookie:', cookie)

    video_id = '7361479239318768950'
    page = 0

    # device_id = device['data'][0]['device_id']
    # iid = device['data'][0]['install_id']
    # ttdt = device['data'][0]['device_token']

    # web获取视频信息
    video_list = [7444518837912964388, 7445547661677169931, 7456796563868765450]
    api.get_video_info(video_list)

    sec_uid = 'MS4wLjABAAAAx85E5eHTZn5MfmvdN_9-bqSReegB2KjL5p5rsMkX4mE'

    # 获取作品列表
    # api.get_video_list('100698990140')
    # api.get_shop_product('MS4wLjABAAAAU9dYHqMwYvVV9_pF479JEqAWPYxEGYjJcLU-T4GNqNk')
    # api.get_video(sec_uid, page=str(page), iid="3138482516028953", device_id="4297303816414455")

    # web版获取小黄车商品
    # api.get_web_promotions(room_id=room_id, uid=uid, web_rid=web_rid)

    # 获取web评论示例
    # api.get_web_comment(video_id, 0)

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
    # api.JuLiang_BatchLink("https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3725012931763634178,https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?id=3654381246617882711")
