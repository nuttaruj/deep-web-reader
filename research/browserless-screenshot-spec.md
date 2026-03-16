# Browserless API Specification - Screenshot

## 🎯 Overview
API Payload สำหรับแคปหน้าจอเว็บด้วย Browserless `/screenshot` endpoint

## 🔗 Endpoint
```
POST https://api.browserless.io/v1/screenshot
```

## 📋 Required Headers
```
Authorization: Bearer ${BROWSERLESS_TOKEN}
Content-Type: application/json
```

## 📤 Request Body Schema
```json
{
  "url": "https://example.com",
  "fullPage": true,
  "viewport": {
    "width": 1920,
    "height": 1080
  },
  "timeout": 30000
}
```

### Parameters
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | ✅ | - | URL ของหน้าเว็บที่ต้องการแคป |
| `fullPage` | boolean | ❌ | `true` | แคปทั้งหน้า (ไม่ใช่แค่ viewport) |
| `viewport` | object | ❌ | `{1920x1080}` | ขนาดหน้าจอ |
| `viewport.width` | integer | ❌ | `1920` | ความกว้าง |
| `viewport.height` | integer | ❌ | `1080` | ความสูง |
| `timeout` | integer | ❌ | `30000` | timeout (ms) |

## 📥 Response
- **Success (200):** Binary image data (PNG)
- **Error (400):** `{ "error": "message" }`
- **Error (401):** Unauthorized (Invalid token)
- **Error (408/504):** Timeout

## ⚠️ Error Handling
- **401:** เช็คว่า `BROWSERLESS_TOKEN` ถูกต้องหรือไม่
- **408/504:** เพิ่ม `timeout` หรือลองใหม่
- **404:** URL ไม่ถูกต้องหรือเข้าถึงไม่ได้

## 📌 Example (cURL)
```bash
curl -X POST "https://api.browserless.io/v1/screenshot" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "fullPage": true,
    "viewport": {"width": 1920, "height": 1080},
    "timeout": 30000
  }' \
  -o screenshot.png
```

## 🔧 Python Example
```python
import requests
import os

BROWSERLESS_TOKEN = os.getenv('BROWSERLESS_TOKEN')

payload = {
    "url": "https://example.com",
    "fullPage": True,
    "viewport": {"width": 1920, "height": 1080},
    "timeout": 30000
}

response = requests.post(
    "https://api.browserless.io/v1/screenshot",
    json=payload,
    headers={"Authorization": f"Bearer {BROWSERLESS_TOKEN}"}
)

if response.status_code == 200:
    with open("screenshot.png", "wb") as f:
        f.write(response.content)
```

## 🚨 Rate Limits & Quotas
- ตรวจสอบได้ที่ Browserless dashboard
- Default: 100 requests/นาที (อาจแตกต่างกันตาม subscription)

---
**Source:** Browserless Official Documentation
**Last Updated:** 2026-03-16