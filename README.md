# TikTokApiTest

# aBogus、XGorgon版本

| 版本名                   | 使用平台   |
|-----------------------|--------|
| aBogus_1.0.1.1        | 抖店     |
| aBogus_1.0.1.19-fix   | 抖音     |
| aBogus_1.0            | 巨量千川   |
| aBogus_1.0.1.20       | 巨量百应   |
| X-Gorgon、X-Khronos... | 安卓41.0 |


## 响应示例
```json
{
  "X-Gorgon": "840480600406305192eebcc2ed57a852966826411904bae37516",
  "X-Khronos": "1794437656",
  "X-Argus": "GPL0ag==",
  "X-Helios": "7k/6Qh0uSocjHgaiEz+DadvWYt/XYfgsDhCQIAJa1ASXBSrD",
  "X-Ladon": "1SYY7Q==",
  "X-Medusa": "H/L0anNo30BaaVv7mTj2ANrEUJR91gANLI42fchLOXsCQ7udtLWL9P1mANkEmN4azILCgA/WhbFSF5vpu3J8o6IFimiKVZmxbV+7OGxUchkTmy9lxzTYpzFWy8DpeDz/P/QwJnsg5xhRaK/lLC1BQ7NwewSJjwXGIO0ASAAXwmwrb9tE5Vy9nxRK1zH82/mYh1OaZXETuMkWRSyLUrwoltPRWyzNQwOugwGiFBzGSkD/35G38jVaCy39kNxnctBl9PhZOJMqq6tMhX18ro7ePhbwBa7LZmmxKtlaYP68i48pOeeMMEnBaEKms2BHMV8PJDHxBOKmXxeUvWNf718VgdGyhEsyYmBNk/eco6w6gA7cwYhKAj85Ce4CXALxg/OxHrxUqKWU1isbHEQG//70q6zxJc+I0SLgyJnz7k/c//9P3Pn7FjU=",
  "X-Perseus": "RCRRRo9u+CeMsGdSQgrr3aYej2hhQuXac5aNEbci1N6H1lrV842YLkSAYQ2sYVW3t874LfESqfh2cdAQ1qamPctFXEClc2zHQmr5/zC1fJiX3m48h4jJAHwwiDsw+rlbfuz04wOF+zxFLT6TaXx3VfYsBc0Te7+2HJY1AqoP5cVcT03K77JOJLS3rhlRh4GbUCvd4Uf0wJJ7sdqALGaBGE9bRSybAmElqpJzRM1mtBgd9adCGoFk3G90r9g2qgEoaRCYxRx5iOTlOIgStRL/LK38Jl9gvXP4CgigVyJWg0+0NVtbvIFbiO1qOyS+tP269EI3F6/BRJz2rKrOkqW/EHaLlKlg2fEr5426Limsi6UtVBXo+v/C0275N3RCSYSFlnjoywV3xNjqKD6dIctrd7kG/ubuO5YvtUqEg0pdDetr0vbyT2J9ieAtD2y/0G4R3s+mNV+IUfHBGkdDHBtuYVGqayuqzKNujUEW0BVnkFpJ5LjYPSoVYe+G9qvfnS6xLDN7uNCnSngUeOgdAY4rV1JNfPeLFZUj3lmlMxH4o2kXcgUdLGyUTTTySL8izuwWWioc+Q7qmcWrEtTOT4KBSn21GZwYNjaQlZw6RBAgJI6aG5begOGhuOH/DC8m9nQRbtqlB3aqUaf+WfB5OFwDp1D/5inRyBlkdm6pFDSKZk+ghBjC3D7hFndb4NekWDyuwxmlVZaOkWKsep0gvW/J1EJGTr0YqwrEXN6op9wd54evr4UruN9O/1BXHa5+QPraYmUOexmiQK0GbC6HcJuO/DcpW7b3GzLhu11nGDmkIp4TGyRJ84J3cGPexcD4KhXJuUxpNpBvHv69sN9f+/GdXknYy30+/q/SHQuzTCwvgvKvhpbZWd/UFbT9Kvuy5WO781gv6vhNqjT34Zv9/oYSMUrYfHFNDA9zoHZVv+yJTgJTsSC=",
  "X-SS-STUB": "F678B2E0E2CACEBFA870E677DEF4C78C",
  "activity_now_client": "1794437656558",
  "x-bb-signal": "1794437656558",
  "x-ss-req-ticket": "1794437656558",
  "x-tt-passport-trace-id": "login_8a34fb6ea485dbf414f918a236199c58",
  "x-tt-passport-verify-portrait-outer": "6cd8ee8d-c2e2-40d7-a0d2-cafac0238d63.login",
  "bd-ticket-guard-version": "3",
  "bd-ticket-guard-display-os-version": "BP2A.250605.031.A3",
  "bd-ticket-guard-iteration-version": "3"
}
```


# bd_ticket_guard_client_data
- Cookie bd_ticket_guard_client_data生成
- Headers bd-ticket-guard-client-data req_sign计算
- Headers bd-ticket-guard-client-data reuqest_sign计算

# 使用接口
- ①：`/pc/selection_tool/batch_link`
- ②：`/pc/selection/decision/pack_detail`
- ③：`/web/comment/list/reply/`
- ④：`/web/commit/item/digg/`
- ⑤：`/shop/mall/product_rank/search`


# 限制
- **每日200**

# 声明
- **仅测试学习使用，如有侵权请[联系我](https://www.app966.cn)或前往[issues留言](https://github.com/Superheroff/TikTokApi_aBogus_Test/issues)删除**
- **禁止频繁大量请求**