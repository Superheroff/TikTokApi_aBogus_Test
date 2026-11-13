# -*- coding: utf-8 -*-
"""拼多多 SKU 直连示例：anti-token 由 /pddapi/sign 生成，再直接请求拼多多接口。

本文件包含两部分，互不依赖：

一、anti-token 签名：只调包装服务 ``POST /pddapi/sign``
    ``request_anti_token(url)`` → ``{'anti-token': '2ah...'}``
    本地不实现、也不缓存算法；每次请求都向 /sign 现取。

二、直连拼多多 SKU（不再经过包装服务）
    ``fetch_sku_direct(goods_id, cookie, access_token)``
    请求 ``POST https://api.pinduoduo.com/api/oak/integration/render/sku``，
    头里带 ``AccessToken`` / ``ETag`` / ``Cookie`` / ``anti-token`` / App UA。
    会话必须是同一登录态：``PDDAccessToken``、``ETag``、UA 三者要配套，
    否则拼多多返回 ``HTTP 403 code=40001 请登录后再操作``。

附：``PddApi`` / ``make_sign`` / ``auth_headers`` 是调用包装服务
（``/pddapi/sku`` 等）时才需要的接口鉴权，与 anti-token 不是一回事。
"""

from __future__ import annotations

import csv
import hashlib
import json
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

DEFAULT_HOST = 'http://124.220.179.225:5050'
DEFAULT_CID = 'd9ba8ae07d955b83c3b04280f3dc5a4a'
DEFAULT_TIMEOUT = 45
APP_KEY_SALT = '5c6b8r9a'
# 手动填写同一登录会话的完整 Cookie 和 token。
COOKIE = 'ETag=GcVbAFB4; PDDAccessToken=NJHPLUAP372BDYWDLTP4U47LGSQH6MZOQCHSPZTHVVHYJIBYOB2A123be4e; install_token=0218daf4-69d3-4741-9668-d3ed11d1654e; pdd_user_id=6109745355710; pdd_user_uin=PZOI66RT4FRTECOQRBP5HSOK5I_GEXDA'
ACCESS_TOKEN = 'NJHPLUAP372BDYWDLTP4U47LGSQH6MZOQCHSPZTHVVHYJIBYOB2A123be4e'
SEED_ID_SEPARATOR = '<->'
#: 签名固定前缀，服务端 string_to_md5 里拼的就是它。
SIGN_PREFIX = '1005'


def derive_app_key(cid: str) -> str:
    """由 cid 派生应用密钥：``sha256(cid + '5c6b8r9a')``。"""
    return hashlib.sha256(f'{cid}{APP_KEY_SALT}'.encode('utf-8')).hexdigest()


def make_sign(cid: str, timestamp: str | int | None = None) -> tuple[str, str]:
    """生成 ``(timestamp, sign)``。

    服务端算法（``dependencies.verify_signature``）::

        sign = md5('1005' + cid + timestamp + sha256(cid + '5c6b8r9a'))

    Args:
        cid: 32 位客户 ID。
        timestamp: 秒级时间戳；缺省取当前时间。必须与发出去的 ``timestamp``
            同一个值，跨秒或超过 30 秒窗口都会 404 签名无效。

    Returns:
        ``(timestamp, sign)``，两者配套使用。

    Examples:
        >>> ts, sign = make_sign('d9ba8ae07d955b83c3b04280f3dc5a4a', '1794580820')
        >>> len(sign)
        32
    """
    timestamp = str(int(time.time())) if timestamp is None else str(timestamp)
    app_key = derive_app_key(cid)
    sign = hashlib.md5(
        f'{SIGN_PREFIX}{cid}{timestamp}{app_key}'.encode('utf-8')
    ).hexdigest()
    return timestamp, sign


def auth_headers(cid: str = DEFAULT_CID) -> dict[str, str]:
    """返回一套可直接使用的鉴权请求头（cid / timestamp / sign）。"""
    timestamp, sign = make_sign(cid)
    return {
        'cid': cid,
        'timestamp': timestamp,
        'sign': sign,
        'content-type': 'application/json',
    }

# =============================================================================
# 一、anti-token：不本地实现算法，统一调包装服务的 POST /pddapi/sign
#     /sign 只生成 token，不会向传入的 url 发请求。
# =============================================================================

SIGN_PATH = '/pddapi/sign'


def request_anti_token(
        url: str,
        cookie: str | None = None,
        *,
        host: str = DEFAULT_HOST,
        cid: str = DEFAULT_CID,
        timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, str]:
    """调 ``POST /pddapi/sign`` 取 anti-token。

    Args:
        url: 目标拼多多接口地址，例如 :data:`SKU_URL`。服务端只用于生成，不会请求它。
        cookie: 可选，随 token 一起回显；不传则响应里没有 Cookie。

    Returns:
        ``{'anti-token': '2ah...'}``（可能附带 ``Cookie``）。

    Raises:
        RuntimeError: 服务端非 200、返回非 JSON，或响应里没有 ``anti-token``。
    """
    timestamp, sign = make_sign(cid)
    headers = {
        'cid': cid,
        'timestamp': timestamp,
        'sign': sign,
        'content-type': 'application/json',
    }
    payload: dict[str, Any] = {'url': url}
    if cookie is not None:
        payload['cookie'] = cookie

    response = requests.post(f'{host.rstrip("/")}{SIGN_PATH}',
                             json=payload, headers=headers, timeout=timeout)
    try:
        data = response.json()
    except ValueError:
        raise RuntimeError('sign 接口返回非 JSON: %s %s'
                           % (response.status_code, response.text[:200])) from None
    if response.status_code != 200 or not isinstance(data, dict) or not data.get('anti-token'):
        raise RuntimeError('sign 失败: %s %s' % (response.status_code, data))
    return data


# =============================================================================
# 二、直接用 anti-token 请求拼多多 SKU（不再经过包装服务）
# =============================================================================


#: App 8.29.0 的 UA，必须与会话同源，否则拼多多侧直接 403。
APP_USER_AGENT = (
    'android Mozilla/5.0 (Linux; Android 16; 2407FRK8EC Build/BP2A.250605.031.A3; wv) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.192 '
    'Mobile Safari/537.36  phh_android_version/8.29.0 '
    'phh_android_build/63d729aff699808c109a23f2579294f430b782a2 '
    'phh_android_channel/xm pversion/0'
)


def parse_cookie(cookie: str) -> dict[str, str]:
    """把 Cookie 串解析成小写键的字典（值里的 ``=`` 不会被截断）。"""
    values: dict[str, str] = {}
    for part in cookie.split(';'):
        part = part.strip()
        if not part or '=' not in part:
            continue
        name, _, value = part.partition('=')
        values[name.strip().lower()] = value.strip()
    return values


def build_sku_headers(
        cookie: str = COOKIE,
        access_token: str | None = None,
        anti_token: str | None = None,
) -> dict[str, str]:
    """拼装直连拼多多 SKU 所需的请求头。

    AccessToken 取 Cookie 里的 ``PDDAccessToken``，ETag 取 ``ETag``，
    两者都能被显式参数覆盖；``anti-token`` 由本地签名生成。
    """
    values = parse_cookie(cookie)
    token = access_token or values.get('pddaccesstoken') or values.get('accesstoken') or ''
    etag = values.get('etag') or values.get('pdd_id') or ''
    if not token:
        raise ValueError('Cookie 里没有 PDDAccessToken，请单独传 access_token')
    if not etag:
        raise ValueError('Cookie 里没有 ETag，拼多多 SKU 接口会拒绝')
    headers = {
        'User-Agent': APP_USER_AGENT,
        'AccessToken': token,
        'ETag': etag,
        'Referer': 'Android',
        'Content-Type': 'application/json;charset=UTF-8',
        'p-appname': 'pinduoduo',
        'Cookie': cookie,
    }
    if anti_token:
        headers['anti-token'] = anti_token
    return headers


def normalize_sku_payload(payload: dict, goods_id: str, status_code: int = 200) -> dict:
    """按 sku.py 的规则校验响应：必须商品匹配且有非空 sku 列表。"""
    requested = str(goods_id)
    if not isinstance(payload, dict):
        raise ValueError('拼多多响应不是 JSON 对象')
    error_code = payload.get('error_code')
    if status_code != 200 or payload.get('success') is False or error_code not in (None, 0, '0'):
        raise ValueError('拼多多拒绝: HTTP %s code=%s %s'
                         % (status_code, error_code, payload.get('error_msg')))
    goods = payload.get('goods') or {}
    if str(goods.get('goods_id')) != requested:
        raise ValueError('响应商品 ID 与请求不一致: %r' % (goods.get('goods_id'),))
    rows = payload.get('sku') or []
    if not isinstance(rows, list) or not rows:
        raise ValueError('HTTP 200 但没有 sku 列表，检查会话/ETag')
    skus = []
    for row in rows:
        group = row.get('group_price')
        normal = row.get('normal_price')
        skus.append({
            'sku_id': str(row.get('sku_id')),
            'group_price_yuan': None if group is None else f'{group // 100}.{group % 100:02d}',
            'normal_price_yuan': None if normal is None else f'{normal // 100}.{normal % 100:02d}',
            'specs': row.get('specs') or [],
            'thumb_url': row.get('thumb_url'),
            'quantity': row.get('quantity'),
            'is_onsale': row.get('is_onsale'),
        })
    return {
        'goods_id': requested,
        'goods_name': goods.get('goods_name'),
        'sku_count': len(skus),
        'skus': skus,
    }


def fetch_sku_direct(
        goods_id: str,
        cookie: str = COOKIE,
        access_token: str | None = ACCESS_TOKEN,
        *,
        use_anti_token: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """取 /sign 的 anti-token 后直连拼多多 SKU 接口，返回归一化后的 SKU 数据。

    Args:
        goods_id: 商品 ID（纯数字）。
        cookie: 同一登录会话的完整 Cookie。
        access_token: 会话令牌；缺省用模块常量，为空则从 Cookie 里取。
        use_anti_token: 为 True 时带 ``/pddapi/sign`` 返回的 ``anti-token`` 头。
    """
    requested = str(goods_id)
    if not requested.isdigit():
        raise ValueError('goods_id 必须是纯数字')
    url = 'https://api.pinduoduo.com/api/oak/integration/render/sku'
    anti_token = None
    if use_anti_token:
        anti_token = request_anti_token(url)['anti-token']

    headers = build_sku_headers(cookie, access_token or None, anti_token)
    body = {
        'goods_id': requested,
        'address_list': [],
        'page_sn': '10014',
        'phone_model': '2407FRK8EC',
        'client_time': str(int(time.time() * 1000)),
        'is_sys_minor': 0,
        'system_language': 'zh',
    }
    print('URL', url)
    print('AccessToken', headers['AccessToken'])
    print('anti-token', anti_token)
    response = requests.post(url, headers=headers, json=body, timeout=timeout, allow_redirects=False)
    return response.json()


#: SKU 导出 CSV 的表头，顺序即列顺序。
SKU_CSV_HEADER = ('商品ID', '商品标题', 'sku_id', '价格', 'sku名', 'sku图')

#: 每列在 dict 行数据中可接受的键名，按优先级排列。
_SKU_KEY_CANDIDATES = (
    ('goods_id', '商品ID'),
    ('title', '商品标题'),
    ('sku_id',),
    ('price', '价格'),
    ('sku_name', 'sku名'),
    ('img', 'sku图'),
)


@dataclass(frozen=True)
class PddTaskItem:
    """月任务 CSV 中的一条记录。

    Attributes:
        goods_id: 拼多多商品 ID，例如 ``709015686168``。
        title: 商品标题，例如 ``【10斤28粗卷】金博仕卫生纸…囤货超值``。
        line_no: 在 CSV 中的行号（含表头，从 1 开始），便于回溯原始数据。
    """

    goods_id: str
    title: str
    line_no: int = 0


def parse_seed_id(seed_id: str) -> tuple[str, str]:
    """从 ``seed_id`` 中取出商品 ID 和商品标题。

    ``seed_id`` 形如::

        709015686168<->【10斤28粗卷】金博仕卫生纸…囤货超值<->681344785<-><->1

    字段之间用 ``<->`` 分隔，依次为商品 ID、商品标题、店铺 ID、
    店铺名称、序号。本函数只取前两个字段。

    Args:
        seed_id: CSV 中 ``seed_id`` 列的原始内容。

    Returns:
        ``(goods_id, title)`` 二元组。

    Raises:
        ValueError: 缺少分隔符、商品 ID 不是纯数字或标题为空时抛出。
    """
    fields = seed_id.split(SEED_ID_SEPARATOR)
    if len(fields) < 2:
        raise ValueError(f'seed_id 缺少 {SEED_ID_SEPARATOR!r} 分隔符: {seed_id!r}')

    goods_id = fields[0].strip()
    title = fields[1].strip()
    if not goods_id.isdigit():
        raise ValueError(f'商品 ID 不是纯数字: {goods_id!r}')
    if not title:
        raise ValueError('商品标题为空')
    return goods_id, title


def load_task_items(
    csv_path: str | Path,
    encoding: str = 'utf-8-sig',
) -> list[PddTaskItem]:
    """读取 PDD 月任务 CSV，取出每条记录的商品 ID 和商品标题。

    文件为两列（``market_code,seed_id``），其中标题可能包含英文逗号且
    未加引号（例如第 555 行），因此这里按行切分、只按第一个逗号拆分列，
    不使用 :mod:`csv` 模块，避免标题被拆散。

    Args:
        csv_path: CSV 文件路径。
        encoding: 文件编码，默认 ``utf-8-sig``（兼容带 BOM 的文件）。

    Returns:
        按文件顺序排列的 :class:`PddTaskItem` 列表。

    Raises:
        ValueError: 某行无法解析时抛出，异常信息包含行号。

    Examples:
        >>> items = load_task_items('PDD-商品详情-月任务_202609.csv')
        >>> items[0].goods_id
        '709015686168'
        >>> items[0].title
        '【10斤28粗卷】金博仕卫生纸加厚学生宿舍必备好物家庭囤货超值'
    """
    path = Path(csv_path)
    items: list[PddTaskItem] = []

    with path.open('r', encoding=encoding, newline='') as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip('\r\n')
            if not line.strip():
                continue

            # 只按第一个逗号拆分，标题里的逗号原样保留在 seed_id 中。
            market_code, sep, seed_id = line.partition(',')
            if not sep:
                raise ValueError(f'{path.name} 第 {line_no} 行缺少逗号分隔符: {line!r}')
            if line_no == 1 and market_code.strip() == 'market_code':
                continue  # 表头

            try:
                goods_id, title = parse_seed_id(seed_id.strip())
            except ValueError as exc:
                raise ValueError(
                    f'{path.name} 第 {line_no} 行解析失败: {exc}'
                ) from None

            items.append(
                PddTaskItem(goods_id=goods_id, title=title, line_no=line_no)
            )

    return items


def _sku_row_values(row: Any) -> list[Any]:
    """把一条 SKU 数据统一成按表头顺序排列的 6 个值。

    Args:
        row: dict（键可为 ``goods_id``/``商品ID`` 等）或长度为 6 的
            list/tuple。

    Returns:
        与 :data:`SKU_CSV_HEADER` 一一对应的值列表。

    Raises:
        TypeError: 传入 set 或其它不支持的类型。
        ValueError: dict 缺列，或 list/tuple 长度不是 6。
    """
    if isinstance(row, Mapping):
        values = []
        for candidates in _SKU_KEY_CANDIDATES:
            for key in candidates:
                if key in row:
                    values.append(row[key])
                    break
            else:
                raise ValueError(
                    f'数据缺少字段 {candidates[0]!r}，实际键: {sorted(map(str, row))}'
                )
        return values

    if isinstance(row, (set, frozenset)):
        raise TypeError(
            'data 中的元素是 set，元素顺序不确定，无法对应表头；'
            '请改用 tuple/list（如 (goods_id, title, sku_id, price, sku_name, img)）'
            '或带键的 dict。'
        )

    if isinstance(row, Sequence) and not isinstance(row, (str, bytes)):
        if len(row) != len(SKU_CSV_HEADER):
            raise ValueError(
                f'每行需要 {len(SKU_CSV_HEADER)} 个值，实际收到 {len(row)} 个: {row!r}'
            )
        return list(row)

    raise TypeError(f'不支持的行类型: {type(row).__name__}')


def export_sku_csv(
    data: Iterable[Any],
    csv_path: str | Path,
    *,
    append: bool = False,
    bom: bool = True,
    excel_text_ids: bool = False,
) -> Path:
    """把 SKU 数据导出为 CSV。

    表头固定为 ``商品ID, 商品标题, sku_id, 价格, sku名, sku图``；每行可以是
    与表头同序的 tuple/list，也可以是带键的 dict。单个值中的逗号、换行、
    引号由 :mod:`csv` 模块自动转义，不会撑破列。

    Args:
        data: SKU 记录集合，例如::

            [
                ('709015686168', '【10斤28粗卷】金博仕…', '681344785',
                 '9.90', '10斤28卷', 'https://…jpg'),
                {'goods_id': '709015686168', 'title': '…', 'sku_id': '…',
                 'price': '9.90', 'sku_name': '…', 'img': '…'},
            ]

        csv_path: 输出文件路径，父目录不存在时会自动创建。
        append: 为 ``True`` 时追加到已有文件（不重复写表头/BOM），便于断点续跑。
        bom: 为 ``True``（默认）时写入 UTF-8 BOM，Excel 打开中文才不乱码。
        excel_text_ids: 为 ``True`` 时把商品 ID、sku_id 写成 ``="709015686168"``，
            防止 Excel 把 12 位数字显示成科学计数法；用程序读取时请保持默认 ``False``。

    Returns:
        实际写入的文件路径。

    Raises:
        TypeError: 行数据是 set 或不支持的类型。
        ValueError: dict 缺列或序列长度不为 6。
    """
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    has_content = path.exists() and path.stat().st_size > 0
    write_header = not (append and has_content)

    with path.open('a' if append else 'w', encoding='utf-8', newline='') as handle:
        if write_header and bom:
            handle.write('\ufeff')  # UTF-8 BOM，供 Excel 正确识别中文

        writer = csv.writer(handle)
        if write_header:
            writer.writerow(SKU_CSV_HEADER)
        for row in data:
            values = _sku_row_values(row)
            if excel_text_ids:
                values[0] = f'="{values[0]}"'
                values[2] = f'="{values[2]}"'
            writer.writerow(values)

    return path


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
        return derive_app_key(self.cid)

    def _auth_headers(self) -> dict[str, str]:
        """生成鉴权请求头，timestamp 与 sign 使用同一时间戳。"""
        return auth_headers(self.cid)

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


def run():
    cookie = COOKIE
    access_token = ACCESS_TOKEN
    if any(not isinstance(value, str) or not value.strip()
           for value in (cookie, access_token)):
        raise ValueError('请手动填写 COOKIE 和 ACCESS_TOKEN')
    api = PddApi()
    items = load_task_items('PDD-商品详情-月任务_202609.csv')
    data = []
    for index, item in enumerate(items):
        goods_id = item.goods_id
        print(f"当前进度：{round(index/len(items)*100,1)}%,商品id：{goods_id}")
        time.sleep(2)
        result = api.get_shop_sku(goods_id, cookie, access_token)
        print("res", result)
        skus = result.get('skus', [])
        if not skus:
            break
        for i in skus:
            sku_id = i['sku_id']
            price = i['group_price_yuan']
            img = i['thumb_url']
            sku_name = i['specs'][0]['spec_value']
            data.append((goods_id, item.title, sku_id, price, sku_name, img))

    path = export_sku_csv(data, 'PDD-SKU-导出2.csv')
    print(f'已导出 {len(data)} 条 SKU 数据到 {path}')






if __name__ == '__main__':
    result = fetch_sku_direct('709015686168')
    print('result', result)
    # run()
