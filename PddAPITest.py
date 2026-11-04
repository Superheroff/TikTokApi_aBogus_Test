# -*- coding: utf-8 -*-
"""拼多多商品接口
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

import requests

DEFAULT_HOST = 'http://124.220.179.225:5050'
DEFAULT_CID = 'd9ba8ae07d955b83c3b04280f3dc5a4a'
DEFAULT_TIMEOUT = 45
APP_KEY_SALT = '5c6b8r9a'


class PddApi:
    """拼多多接口客户端。"""

    def __init__(
        self,
        cid: str = DEFAULT_CID,
        host: str = DEFAULT_HOST,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.cid = cid
        self.host = host.rstrip('/')
        self.timeout = timeout

    @property
    def _app_key(self) -> str:
        """服务端约定的应用密钥，由 cid 派生。"""
        return hashlib.sha256(f'{self.cid}{APP_KEY_SALT}'.encode('utf-8')).hexdigest()

    def _auth_headers(self) -> dict[str, str]:
        """生成鉴权请求头，timestamp 与 sign 使用同一时间戳。"""
        timestamp = str(int(time.time()))
        sign = hashlib.md5(
            f'1005{self.cid}{timestamp}{self._app_key}'.encode('utf-8')
        ).hexdigest()
        return {
            'cid': self.cid,
            'timestamp': timestamp,
            'sign': sign,
            'content-type': 'application/json',
        }

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        """向本地服务发送 JSON 请求，返回解析后的 JSON，非 JSON 响应返回原文。"""
        url = f'{self.host}{path}'
        response = requests.post(
            url,
            json=payload,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )
        try:
            return response.json()
        except ValueError:
            return response.text

    def get_shop_sku(self, goods_id: str, cks: str, access_token: str) -> Any:
        """按商品 ID 查询拼多多商品规格。

        Args:
            goods_id: 拼多多商品 ID。
            cks: 拼多多 Cookie。
            access_token: 同一账号的访问令牌。

        Returns:
            接口返回的 JSON；响应非 JSON 时返回文本。
        """
        return self._post(
            '/pddapi/sku',
            {
                'goods_id': goods_id,
                'cookie': cks,
                'access_token': access_token,
            },
        )

    def search(
        self,
        keyword: str,
        page: int,
        cks: str,
        access_token: str,
        flip: str = '',
        list_id: str = '',
    ) -> Any:
        """按关键词搜索拼多多商品。

        第一页只传 page=1；后续页传入上一页返回的 next_cursor 中的
        page、flip、list_id，且 keyword 保持一致。

        Args:
            keyword: 搜索关键词。
            page: 页码，首页为 1。
            cks: 拼多多 Cookie。
            access_token: 同一账号的访问令牌。
            flip: 翻页令牌，首页不需要。
            list_id: 搜索列表标识，首页不需要。

        Returns:
            接口返回的 JSON；响应非 JSON 时返回文本。
        """
        payload = {
            'keyword': keyword,
            'page': page,
            'cookie': cks,
            'access_token': access_token,
        }
        if page != 1:
            payload['flip'] = flip
            payload['list_id'] = list_id
        return self._post('/pddapi/search', payload)


if __name__ == '__main__':
    cookie = 'PDDAccessToken=KQ3M3C7RE7YCORP3IYC4ZZNPKOTXZRUKOUMFMJT7HGNGGPZJVASQ123be4e; pdd_user_id=6109745355710; pdd_user_uin=PZOI66RT4FRTECOQRBP5HSOK5I_GEXDA; ETag=GcVbAFB4; install_token=0218daf4-69d3-4741-9668-d3ed11d1654e'
    access_token = 'KQ3M3C7RE7YCORP3IYC4ZZNPKOTXZRUKOUMFMJT7HGNGGPZJVASQ123be4e'
    api = PddApi()
    print(api.search('海飞丝洗发水', 1, cookie, access_token))
    print(api.get_shop_sku('1006146563677', cookie, access_token))
