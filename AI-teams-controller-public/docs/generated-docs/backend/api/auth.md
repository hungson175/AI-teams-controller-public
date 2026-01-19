# Authentication API

JWT-based authentication endpoints.

## Endpoints

### Register

```http
POST /api/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "username": "user",
  "password": "securepass"
}
```

**Response:**
```json
{
  "user": {"id": 1, "email": "user@example.com", "username": "user"},
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Login

```http
POST /api/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass"
}
```

### Refresh Token

```http
POST /api/auth/refresh
```

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

## Token Lifetimes

| Token | Lifetime |
|-------|----------|
| Access | 15 minutes |
| Refresh | 7 days |

## Usage

```typescript
// Frontend: Include in requests
fetch('/api/teams', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
```
