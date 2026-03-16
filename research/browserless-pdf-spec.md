# Browserless API Specification - PDF

## 🎯 Overview
API Payload สำหรับแปลงหน้าเว็บเป็น PDF ด้วย Browserless `/pdf` endpoint

## 🔗 Endpoint
```
POST https://api.browserless.io/v1/pdf
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
  "printBackground": true,
  "format": "A4",
  "margin": {
    "top": "10mm",
    "right": "10mm",
    "bottom": "10mm",
    "left": "10mm"
  },
  "timeout": 60000
}
```

### Parameters
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | ✅ | - | URL ของหน้าเว็บที่ต้องการแปลงเป็น PDF |
| `printBackground` | boolean | ❌ | `true` | พิมพ์พื้นหลังด้วย |
| `format` | string | ❌ | `"A4"` | ขนาดกระดาษ: `"Letter"`, `"A4"`, `"Legal"`, `"Tabloid"` |
| `orientation` | string | ❌ | `"portrait"` | `"portrait"` หรือ `"landscape"` |
| `margin` | object | ❌ | `10mm` | ขอบกระดาษ |
| `margin.top` | string | ❌ | `"10mm"` | ขอบบน |
| `margin.right` | string | ❌ | `"10mm"` | ขอบขวา |
| `margin.bottom` | string | ❌ | `"10mm"` | ขอบล่าง |
| `margin.left` | string | ❌ | `"10mm"` | ขอบซ้าย |
| `timeout` | integer | ❌ | `60000` | timeout (ms) |

## 📥 Response
- **Success (200):** Binary PDF data
- **Error (400):** `{ "error": "message" }`
- **Error (401):** Unauthorized (Invalid token)
- **Error (408/504):** Timeout

## ⚠️ Error Handling
- **401:** เช็คว่า `BROWSERLESS_TOKEN` ถูกต้องหรือไม่
- **408/504:** เพิ่ม `timeout` หรือลองใหม่
- **404:** URL ไม่ถูกต้องหรือเข้าถึงไม่ได้

## 📌 Example (cURL)
```bash
curl -X POST "https://api.browserless.io/v1/pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "printBackground": true,
    "format": "A4",
    "margin": {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
    "timeout": 60000
  }' \
  -o output.pdf
```

## 🔧 Python Example
```python
import requests
import os

BROWSERLESS_TOKEN = os.getenv('BROWSERLESS_TOKEN')

payload = {
    "url": "https://example.com",
    "printBackground": True,
    "format": "A4",
    "margin": {
        "top": "10mm",
        "right": "10mm",
        "bottom": "10mm",
        "left": "10mm"
    },
    "timeout": 60000
}

response = requests.post(
    "https://api.browserless.io/v1/pdf",
    json=payload,
    headers={"Authorization": f"Bearer {BROWSERLESS_TOKEN}"}
)

if response.status_code == 200:
    with open("output.pdf", "wb") as f:
        f.write(response.content)
```

## 🚨 Rate Limits & Quotas
- ตรวจสอบได้ที่ Browserless dashboard
- Default: 100 requests/นาที (อาจแตกต่างกันตาม subscription)
- PDF อาจใช้เวลานานกว่า screenshot (แนะนำ timeout 60s)

---
**Source:** Browserless Official Documentation
**Last Updated:** 2026-03-16