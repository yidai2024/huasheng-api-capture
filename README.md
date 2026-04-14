# 花生网 (huasheng.cn) API 接口文档

> 抓取时间: 2026-04-14
> 工具: Playwright
> 网站: https://www.huasheng.cn
> 实质: B站 AI 视频创作平台 InnoVideo

---

## 一、平台概述

**花生网 (huasheng.cn)** 是哔哩哔哩(B站)旗下的 **AI 视频创作平台**，内部名称为 **InnoVideo**。

**核心功能：**
- AI 视频生成（文字转视频、图文转视频）
- AI 配音（多种声音风格：解说、播客、角色扮演等）
- 视频模板系统
- B站账号体系打通

**技术栈：**
- 前端: Next.js + React
- 后端: Go (从响应格式判断)
- 认证: B站统一登录 (passport)
- 数据分析: B站自研埋点系统
- 风控: B站 Gaia 风控系统

---

## 二、域名架构

| 域名 | 用途 |
|------|------|
| `www.huasheng.cn` | 主站 (前端 + API) |
| `api.huasheng.cn` | 核心业务 API |
| `passport.huasheng.cn` | 登录认证 (B站统一登录) |
| `data.huasheng.cn` | 数据埋点上报 |
| `api.bilibili.com` | B站基础设施 (KV配置/风控/指纹) |
| `data.bilibili.com` | B站数据上报 |
| `*.hdslb.com` | B站 CDN 资源 |

---

## 三、核心 API 接口详解

### 3.1 平台配置 API

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/api/innovideo/config` | 获取平台配置（配音列表等） | 否 |
| GET | `/api/innovideo/abtest` | A/B 测试配置 | 否 |

```
GET https://www.huasheng.cn/api/innovideo/config

Response:
{
  "voices": [
    {"id": "5", "voice": "male-qn-jingying", "desc": "生动解说"},
    {"id": "6", "voice": "hutong_daye", "desc": "北京小伙"},
    {"id": "7", "voice": "audiobook_female_2", "desc": "新闻主播"},
    {"id": "8", "voice": "audiobook_male_1", "desc": "..."},
    ...
  ]
}

GET https://www.huasheng.cn/api/innovideo/abtest?ab_var=front_montage

Parameters:
  ab_var: A/B测试变量名
    - front_montage: 前端蒙太奇
    - montage_composite: 蒙太奇合成
    - podcast_mtq: 播客
    - local_recall: 本地召回

Response:
{
  "ab_flag": ""  // 空表示未命中实验组
}
```

### 3.2 VIP/会员 API

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/api/vip/info` | 获取VIP会员信息 | 是 |

```
GET https://www.huasheng.cn/api/vip/info

Response (未登录):
{
  "code": 401,
  "reason": "账号未登录",
  "message": "账号未登录",
  "metadata": {}
}

Response (已登录):
{
  "code": 0,
  "data": {
    "vip_type": 0|1|2,
    "vip_status": 0|1,
    "vip_due_date": 1234567890,
    ...
  }
}
```

### 3.3 素材 API

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/api/innovideo/material/tts/list` | 获取TTS配音列表 | 否 |

```
GET https://www.huasheng.cn/api/innovideo/material/tts/list?category_id=0

Parameters:
  category_id: 分类ID
    - 0: 全部
    - 1740254: 解说类
    - 1740253: 播客类

Response:
{
  "materials": [
    {
      "id": "5866403",
      "name": "生动解说",
      "cover": "http://i0.hdslb.com/bfs/creative/xxx.png",
      "download_url": "",
      "extra": "{\"voice_type\":2,\"voice\":\"male-qn-jingying\"}"
    },
    ...
  ]
}
```

### 3.4 项目 API

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/api/innovideo/project/info` | 获取项目详情 | 是 |

```
GET https://www.huasheng.cn/api/innovideo/project/info?pid=<项目ID>

Parameters:
  pid: 项目ID (数字)

Response (无效ID):
{
  "code": 400,
  "reason": "CODEC",
  "message": "parsing field \"pid\": strconv.ParseInt: parsing \"undefined\": invalid syntax",
  "metadata": {}
}
```

### 3.5 用户/导航 API

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/x/web-interface/nav` | 获取用户导航信息 | 否 |

```
GET https://api.huasheng.cn/x/web-interface/nav

Response (未登录):
{
  "code": -101,
  "message": "账号未登录",
  "ttl": 1,
  "data": {
    "isLogin": false,
    "wbi_img": {
      "img_url": "https://i0.hdslb.com/bfs/wbi/xxx.png",
      "sub_url": "https://i0.hdslb.com/bfs/wbi/xxx.png"
    }
  }
}
```

### 3.6 活动 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/x/activity_components/eva_operation/list` | 获取活动组件列表 |

```
GET https://api.huasheng.cn/x/activity_components/eva_operation/list
    ?source_id=29ERAmwloghvktd00
    &pn=1
    &ps=50

Response:
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "30ERA4wloghviey00",
        "source_id": "29ERAmwloghvktd00",
        "object_id": "BV14NUVBTEjU",
        "object_type": 1,
        "state": 1
      },
      ...
    ]
  }
}
```

---

## 四、登录认证系统 (passport.huasheng.cn)

花生网使用 **B站统一登录系统**。

### 4.1 登录流程

```
┌─────────────────────────────────────────────────┐
│  1. 访问 huasheng.cn                            │
│  2. 点击登录                                    │
│  3. 跳转 passport.huasheng.cn                  │
│  4. 选择登录方式:                               │
│     - 扫码登录 (B站APP扫码)                     │
│     - 密码登录 (需要验证码)                     │
│  5. 登录成功 → 返回 huasheng.cn                │
│  6. 设置 Cookie (SESSDATA, bili_jct 等)        │
└─────────────────────────────────────────────────┘
```

### 4.2 登录相关 API

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/x/passport-login/web/qrcode/generate` | 生成登录二维码 |
| GET | `/x/passport-login/web/qrcode/poll` | 轮询扫码状态 |
| GET | `/x/passport-login/captcha` | 获取验证码 |

```
GET https://passport.huasheng.cn/x/passport-login/web/qrcode/generate
    ?source=ttv_pc
    &go_url=https://www.huasheng.cn/

Response:
{
  "code": 0,
  "data": {
    "url": "https://account.bilibili.com/h5/account-h5/auth/scan-web?...",
    "qrcode_key": "28d78cebbb748722dbe13d9d9f3ca98f"
  }
}

GET https://passport.huasheng.cn/x/passport-login/web/qrcode/poll
    ?qrcode_key=28d78cebbb748722dbe13d9d9f3ca98f

Response (未扫码):
{
  "code": 0,
  "data": {
    "code": 86101,
    "message": "未扫码"
  }
}

Response (已扫码待确认):
{
  "code": 0,
  "data": {
    "code": 86090,
    "message": "已扫码，待确认"
  }
}

Response (登录成功):
{
  "code": 0,
  "data": {
    "code": 0,
    "url": "https://www.huasheng.cn/?sid=xxx",
    "refresh_token": "xxx",
    "timestamp": 1234567890
  }
}

GET https://passport.huasheng.cn/x/passport-login/captcha?source=ttv_pc

Response:
{
  "code": 0,
  "data": {
    "type": "geetest",
    "token": "47be5f...9ef2",
    "geetest": {
      "challenge": "a0ec1ca026b88146766a65b4ca4ee640",
      "gt": "ac597a4506fee079629df5d8b66dd4fe"
    }
  }
}
```

---

## 五、B站基础设施 API

花生网复用了大量B站的基础设施：

### 5.1 KV 配置系统

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/x/kv-frontend/namespace/data` | 获取KV配置数据 |

```
GET https://api.bilibili.com/x/kv-frontend/namespace/data
    ?appKey=333.1333
    &nscode=0
    &unlimit=true

Parameters:
  appKey: 应用标识 (333.1333=花生网主配置)
  nscode: 命名空间代码
  unlimit: 是否不限制
  versionId: 版本ID (用于缓存)

Response:
{
  "code": 0,
  "data": {
    "versionId": "1772162031366",
    "data": {
      "bilimirror.minilogin": "{...}",
      // 各种功能开关和配置
    }
  }
}
```

### 5.2 设备指纹系统

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/x/frontend/finger/spi_v2` | 获取设备指纹 |

```
GET https://api.bilibili.com/x/frontend/finger/spi_v2

Response:
{
  "code": 0,
  "data": {
    "b_3": "143E0AF9-46E1-41A5-720C-47D0549B5B9A56655infoc",
    "b_4": "0C3419E0-AC33-B6D9-7DC4-06073ACC500G56655-026041503-..."
  }
}
```

### 5.3 风控系统 (Gaia)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/x/internal/gaia-gateway/ExGetAxe` | 获取风控公钥 |
| POST | `/x/internal/gaia-gateway/ExClimbCongLing` | 风控数据上报 |
| POST | `/x/internal/gaia-gateway/ExClimbWuzhi` | 无感风控上报 |

```
GET https://api.bilibili.com/x/internal/gaia-gateway/ExGetAxe

Response:
{
  "code": 0,
  "data": {
    "version": "v1",
    "public_key": "-----BEGIN rsa public key-----\nMIICIjANBg..."
  }
}

POST https://api.bilibili.com/x/internal/gaia-gateway/ExClimbCongLing

Body:
{
  "header": {
    "encode_type": 2,
    "payload_type": 4,
    "encoded_aes_key": "oIVwkjdScPVHGsasnH+UZgUNlEyCKK/zGygvibza7+lc7C7Q4uAold1h1EVCWkuL6fD3VKw0CyhlqCVd2m30bJYS4Mk1zXT66q+hqHrF4+9lU6BdqpgoWvTJx5tT/AtcGUp8+CW/C..."
  }
}
```

### 5.4 Ticket 系统

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/bapis/bilibili.api.ticket.v1.Ticket/GenWebTicket` | 生成 Web Ticket |

```
POST https://api.bilibili.com/bapis/bilibili.api.ticket.v1.Ticket/GenWebTicket
    ?key_id=ec02
    &hexsign=79922d9dfbdf7aeed1e41dc6fc1e8d9a419be99153438fa0115efe98e0eddf85
    &context[ts]=1776195642
    &csrf=

Body:
{"biliCSRF":""}

Response:
{
  "code": 0,
  "data": {
    "ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 5.5 数据上报系统

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/v2/log/web` | Web埋点上报 |

```
POST https://data.huasheng.cn/v2/log/web?content_type=pbrequest&logid=021436

// Protobuf 格式的埋点数据
// 包含: 页面访问、点击事件、曝光事件、风险检测等
```

---

## 六、完整 API 端点列表

### www.huasheng.cn (主站 API)
```
GET  /api/innovideo/config              # 平台配置
GET  /api/innovideo/abtest              # A/B测试
GET  /api/vip/info                      # VIP信息
GET  /api/innovideo/material/tts/list   # TTS配音列表
GET  /api/innovideo/project/info        # 项目详情
```

### api.huasheng.cn (业务 API)
```
GET  /x/web-interface/nav               # 用户导航/登录状态
GET  /x/activity_components/eva_operation/list  # 活动组件
```

### passport.huasheng.cn (登录 API)
```
GET  /x/passport-login/web/qrcode/generate  # 生成二维码
GET  /x/passport-login/web/qrcode/poll      # 轮询扫码状态
GET  /x/passport-login/captcha              # 获取验证码
```

### api.bilibili.com (B站基础设施)
```
GET  /x/kv-frontend/namespace/data          # KV配置
GET  /x/frontend/finger/spi_v2              # 设备指纹
GET  /x/internal/gaia-gateway/ExGetAxe      # 风控公钥
POST /x/internal/gaia-gateway/ExClimbCongLing  # 风控上报
POST /x/internal/gaia-gateway/ExClimbWuzhi     # 无感风控
POST /bapis/bilibili.api.ticket.v1.Ticket/GenWebTicket  # Web Ticket
```

### data.huasheng.cn / data.bilibili.com (数据上报)
```
POST /v2/log/web                            # 埋点上报
```

---

## 七、页面路由

| 路由 | 说明 | 状态 |
|------|------|------|
| `/` | 首页 | 200 |
| `/video` | 视频页 | 301→200 |
| `/blackboard/era/xvQno42uu09wWtUl.html` | 隐私政策 | 200 |
| `/blackboard/era/1Cra21NxnhLjS5ji.html` | 服务协议 | 200 |
| `/project.txt` | 项目配置 (RSC) | 200 |
| `/index.txt` | 索引配置 (RSC) | 200 |
| `/create` | 创作页 | 404 (需登录) |
| `/workspace` | 工作台 | 404 (需登录) |

---

## 八、技术发现

1. **登录方式**: B站统一扫码登录 + 极验验证码
2. **风控系统**: B站 Gaia 风控，使用 RSA 加密上报数据
3. **设备指纹**: B站自研指纹系统 (b_3, b_4)
4. **A/B测试**: 支持多维度实验 (蒙太奇/播客/本地召回)
5. **配音系统**: 多种TTS声音 (解说/播客/角色/方言)
6. **Go后端**: 从错误消息格式判断使用 Go 语言开发

---

*文档由 Playwright 自动抓取生成*
