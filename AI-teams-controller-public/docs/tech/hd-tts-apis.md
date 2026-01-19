# HD-TTS API Quick Guide

## Base URL

- **Production:** `https://hd-tts-backend.hungson175.com`
- **Local:** `http://localhost:17603`

## Authentication

**Test API Key:** `vvtts_7e1647c466a68a36cfa401a08e1ec4a2`

```bash
# Method 1: Header (recommended)
-H "X-API-Key: vvtts_7e1647c466a68a36cfa401a08e1ec4a2"

# Method 2: Query parameter
?api_key=vvtts_7e1647c466a68a36cfa401a08e1ec4a2
```

**Note:** Localhost requests bypass authentication.

---

## Quick Examples

### 1. Basic Synthesis

```bash
curl -X POST https://hd-tts-backend.hungson175.com/synthesize \
  -H "X-API-Key: vvtts_7e1647c466a68a36cfa401a08e1ec4a2" \
  -H "Content-Type: application/json" \
  -d '{"text": "Xin chào các bạn"}' \
  --output audio.wav
```

### 2. Female Voice, Northern Accent, Happy Emotion

```bash
curl -X POST https://hd-tts-backend.hungson175.com/synthesize \
  -H "X-API-Key: vvtts_7e1647c466a68a36cfa401a08e1ec4a2" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Chào mừng bạn đến với HD-TTS",
    "gender": "female",
    "area": "northern",
    "emotion": "happy",
    "quality": "high"
  }' \
  --output welcome.wav
```

### 3. Fast Quality for Quick Preview

```bash
curl -X POST https://hd-tts-backend.hungson175.com/synthesize \
  -H "X-API-Key: vvtts_7e1647c466a68a36cfa401a08e1ec4a2" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Đây là bản xem trước nhanh",
    "quality": "fast"
  }' \
  --output preview.wav
```

### 4. Health Check

```bash
curl "https://hd-tts-backend.hungson175.com/health?api_key=vvtts_7e1647c466a68a36cfa401a08e1ec4a2"
```

---

## Parameters

| Parameter | Type | Options | Default |
|-----------|------|---------|---------|
| `text` | string | Any Vietnamese text | **Required** |
| `gender` | string | `male`, `female` | `female` |
| `area` | string | `northern`, `southern`, `central` | `northern` |
| `emotion` | string | `neutral`, `happy`, `sad`, `angry`, `surprised`, `serious` | `neutral` |
| `group` | string | `story`, `news`, `audiobook`, `interview`, `review` | `news` |
| `speed` | float | 0.5 - 2.0 | 1.0 |
| `quality` | string | `high` (NFE=32, ~5s), `fast` (NFE=16, ~2.5s) | `high` |

---

## Python Example

```python
import requests

url = "https://hd-tts-backend.hungson175.com/synthesize"
headers = {
    "X-API-Key": "vvtts_7e1647c466a68a36cfa401a08e1ec4a2",
    "Content-Type": "application/json"
}
data = {
    "text": "Xin chào, đây là ví dụ bằng Python",
    "gender": "female",
    "area": "northern",
    "quality": "high"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("Audio saved to output.wav")
else:
    print(f"Error: {response.status_code}")
```

---

## JavaScript Example

```javascript
const axios = require('axios');
const fs = require('fs');

const url = 'https://hd-tts-backend.hungson175.com/synthesize';
const headers = {
  'X-API-Key': 'vvtts_7e1647c466a68a36cfa401a08e1ec4a2',
  'Content-Type': 'application/json'
};
const data = {
  text: 'Xin chào, đây là ví dụ bằng JavaScript',
  gender: 'female',
  area: 'northern',
  quality: 'high'
};

axios.post(url, data, { headers, responseType: 'arraybuffer' })
  .then(response => {
    fs.writeFileSync('output.wav', response.data);
    console.log('Audio saved to output.wav');
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

---

## Managing API Keys

```bash
cd backend
source ../venv/bin/activate

# Create new key
python manage_keys.py create "Friend Name"

# List all keys with usage stats
python manage_keys.py list

# Show key details
python manage_keys.py info <key_id>

# Revoke key
python manage_keys.py delete <key_id>
```

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/synthesize` | POST | Generate speech (returns WAV binary) |
| `/health` | GET | Health check + worker status |
| `/voices` | GET | List available voice options |

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success - audio file returned |
| 400 | Bad request - invalid parameters |
| 401 | Unauthorized - invalid/missing API key |
| 500 | Server error - check backend logs |

---

**Project:** https://github.com/hungson175/hd-tts
**Live Demo:** https://hd-tts.hungson175.com
