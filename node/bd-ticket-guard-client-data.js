
const crypto = require('crypto');

const cert = "-----BEGIN PRIVATE KEY-----\n" +
    "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgskxBKqQeBxyVpySx\n" +
    "qYHwmZRPBm71AnNEry/xzK9Zz/mhRANCAARXxfk/4HXX7kbxpVWlRv3gC+VV2A+v\n" +
    "hJ9iqwors6jc41/IMpTGhmf9NVypvKu45N4waMf2zH3ywAnMc76YtNcy\n" +
    "-----END PRIVATE KEY-----"

function m(t) {
    const e = [];
    for (let r = 0; r < t.length; r += 3) {
        const n = t[r] << 16 | t[r + 1] << 8 | t[r + 2];
        for (let i = 0; i < 4; i++) {
            if (8 * r + 6 * i <= 8 * t.length) {
                e.push("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charAt(n >>> (6 * (3 - i)) & 63));
            } else {
                e.push("=");
            }
        }
    }
    return e.join("");
}

var y ={};
function b(t) {
    if (t) {
        if (y[t])
            return y[t];
        var e = m(function (t) {
            for (var e = new Uint8Array(t.length / 2), r = 0; r < t.length; r += 2)
                e[r / 2] = parseInt(t.substr(r, 2), 16);
            return e
        }(getKey()));
        return y[t] = e,
            e
    }
    return ""
}

function getKey(){

    // 使用 crypto.createPublicKey 解析证书
    const publicKey = crypto.createPublicKey(cert);

    // 检查公钥是否是 ECDSA 类型
    if (publicKey.asymmetricKeyType === 'ec') {
        // 获取公钥的原始数据 (x 和 y 坐标)
        const keyData = publicKey.export({type: 'spki', format: 'der'});

        // 从 DER 编码中提取 ECDSA 公钥的 x 和 y 坐标
        const xStart = 22;  // ECDSA 公钥 X 坐标在 DER 编码中的偏移位置
        const yStart = xStart + 1 + keyData[xStart];  // Y 坐标的偏移位置

        const xHex = keyData.slice(xStart + 1, yStart).toString('hex');
        const yHex = keyData.slice(yStart + 1).toString('hex');

        // console.log('X:', xHex, xHex.length);
        // console.log('Y:', yHex, yHex.length);
        // console.log('XY:', XY, XY.length);
        return xHex.slice(6,) + "3f" + yHex
    } else {
        console.log('证书不包含 ECDSA 公钥');
    }

}

function cookie_bd() {
    let key = b(cert);
    let data = {"bd-ticket-guard-version":2,"bd-ticket-guard-iteration-version":1,"bd-ticket-guard-ree-public-key":key,"bd-ticket-guard-web-version":2}
    return Buffer.from(JSON.stringify(data, null, 0)).toString("base64")
}

function getBd(ts_sign, path, ticket="") {
    ticket = ticket === "" ? "hash.66OZXDANUNqBMwcudIU0pBAkWIMxlpAvkpnoZYD+WWg=": ticket
    let time = Math.floor(new Date().getTime() / 1e3)
    let message = `ticket=${ticket}&path=${path}&timestamp=${time}`;
    const signature = crypto.createSign('SHA256')
    .update(message)
    .sign(cert);
    let str_data = JSON.stringify({
        ts_sign: ts_sign,
        req_content: "ticket,path,timestamp",
        req_sign: signature.toString("base64"),
        timestamp: time
    },null, 0)
    return Buffer.from(str_data).toString("base64")
}

console.log(cookie_bd())
v = "ts.2.67256ef3065f9cc0fe98241c0390034c0439f4c1a48b6f79bfc52110d64a7de9c4fbe87d2319cf05318624ceda14911ca406dedbebeddb2e30fce8d4fa02575d"
console.log(getBd(v, "/aweme/v1/web/comment/list/reply/", ""))