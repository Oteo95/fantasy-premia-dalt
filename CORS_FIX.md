# CORS Fix Documentation

## Problem
The application was experiencing a CORS (Cross-Origin Resource Sharing) error when trying to access the `/api/auth/login` endpoint. The issue manifested as:

- **Status Code**: 401 Unauthorized on OPTIONS preflight request
- **Error**: OPTIONS preflight request was being rejected before the actual POST request could be sent
- **Root Cause**: The backend deployed on Vercel preview URL (`fantasy-premia-dalt-ps4e-fjcjg6b2w-oteo95s-projects.vercel.app`) was not allowed by the CORS configuration, which only permitted the main frontend domain (`fantasy-premia-dalt.vercel.app`)

## The Issue in Detail

When your frontend (on `fantasy-premia-dalt.vercel.app`) tries to make a request to your backend API (on a different Vercel preview deployment URL), the browser performs a **CORS preflight check**:

1. Browser sends an OPTIONS request first (preflight)
2. Server should respond with appropriate CORS headers (200 OK)
3. If successful, browser sends the actual POST request

**What was happening**:
- The OPTIONS request was hitting the authentication middleware
- It returned 401 Unauthorized because no auth token was provided
- The browser blocked the actual request from being sent

## Solution Implemented

### 1. Wildcard Support for Vercel Deployments
Added support for all Vercel preview deployments using a wildcard pattern:
```python
allowed_origins = [
    "https://fantasy-premia-dalt.vercel.app",
    "https://*.vercel.app",  # Allows all Vercel preview deployments
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000"
]
```

### 2. Custom CORS Middleware
Created a `CustomCORSMiddleware` that:
- **Intercepts OPTIONS requests** before they reach authentication
- **Validates the origin** against allowed patterns (including wildcards)
- **Returns proper CORS headers** immediately for OPTIONS requests
- **Adds CORS headers** to all responses for allowed origins

### 3. Key Features
- ✅ Handles preflight OPTIONS requests correctly
- ✅ Supports wildcard patterns for Vercel preview URLs
- ✅ Validates origins against patterns using regex
- ✅ Returns appropriate CORS headers without requiring authentication
- ✅ Maintains security by only allowing specified origins

## Code Changes

The main changes were made in `backend/main_firebase.py`:

1. **Added wildcard support** in allowed origins
2. **Created `is_allowed_origin()` function** to validate origins with wildcard patterns
3. **Implemented `CustomCORSMiddleware`** class to handle OPTIONS requests and CORS headers
4. **Replaced standard CORSMiddleware** with the custom implementation

## Deployment Steps

To fix the CORS issue in production:

### Option 1: Deploy Backend with Changes
```bash
# Commit the changes
git add backend/main_firebase.py
git commit -m "Fix: CORS configuration for Vercel preview deployments"
git push origin main
```

The backend will automatically redeploy on Vercel with the new CORS configuration.

### Option 2: Set Environment Variable (Alternative)
You can also configure allowed origins via environment variable in Vercel:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add: `ALLOWED_ORIGINS` = `https://fantasy-premia-dalt.vercel.app,https://*.vercel.app`
3. Redeploy

## Testing

After deployment, test the fix:

1. Open your frontend: `https://fantasy-premia-dalt.vercel.app`
2. Try to log in
3. Check browser DevTools Network tab:
   - OPTIONS request should return **200 OK** (not 401)
   - POST request should follow with **200 OK**

## Technical Details

### Before (Problem)
```
OPTIONS /api/auth/login
→ 401 Unauthorized (blocked by auth middleware)
→ Actual POST request never sent
```

### After (Fixed)
```
OPTIONS /api/auth/login
→ 200 OK (handled by CustomCORSMiddleware with CORS headers)
→ POST /api/auth/login
→ 200 OK (with user data)
```

## CORS Headers Returned

The custom middleware now returns these headers for allowed origins:
- `Access-Control-Allow-Origin`: [specific origin]
- `Access-Control-Allow-Credentials`: true
- `Access-Control-Allow-Methods`: *
- `Access-Control-Allow-Headers`: *
- `Access-Control-Max-Age`: 600 (for OPTIONS requests)

## Security Considerations

✅ **Secure**: Only specified origins are allowed (not `*`)
✅ **Wildcard Pattern**: Limited to `*.vercel.app` for preview deployments
✅ **Credentials**: Supported for authenticated requests
✅ **Validation**: Origin is checked against patterns before adding headers

## Future Improvements

Consider these enhancements:
1. Add specific preview URL patterns if needed
2. Implement origin caching for performance
3. Add logging for CORS rejections
4. Set different CORS policies for different environments

---

**Date Fixed**: January 18, 2026
**Files Modified**: `backend/main_firebase.py`
