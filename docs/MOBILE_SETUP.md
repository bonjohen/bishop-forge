# Mobile Device Setup Guide

## 🎯 Overview

This guide explains how to use BishopForge on mobile devices (Android/iOS) and configure the backend API connection.

---

## 🔧 Problem: Backend Connection on Mobile

**Issue:** Mobile devices cannot access `http://localhost:8000` because:
- `localhost` refers to the mobile device itself, not your desktop computer
- The backend server is running on your desktop/laptop

**Solution:** Configure the frontend to use your computer's IP address instead of localhost.

---

## ✅ Quick Fix: Offline Mode

**Good News:** The app now has an **offline fallback mode**!

If the backend is unreachable, the opponent will automatically use client-side random move selection:
- ✅ Works without any backend connection
- ✅ Instant moves (no network delay)
- ✅ Shows "(offline mode)" in the move message
- ⚠️ Only "Random" opponent profile available (no strategic AI)

**You'll see:**
```
Opponent played: e5 (offline mode)
```

---

## 🌐 Full Setup: Connect to Backend from Mobile

### Step 1: Find Your Computer's IP Address

**On Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" under your active network adapter (e.g., `192.168.1.100`)

**On Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```
Look for your local IP (e.g., `192.168.1.100`)

### Step 2: Start Backend Server

Make sure the backend is accessible from the network:

```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Important:** Use `--host 0.0.0.0` to allow connections from other devices on your network.

### Step 3: Configure Frontend

**Option A: Environment Variable (Recommended)**

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://192.168.1.100:8000
```

Replace `192.168.1.100` with your computer's actual IP address.

**Option B: Edit Source Code**

Edit `frontend/src/api/backendClient.js`:

```javascript
const API_BASE = "http://192.168.1.100:8000";  // Change this line
```

### Step 4: Rebuild Frontend

```powershell
cd frontend
npm run build
```

### Step 5: Access from Mobile

**Option A: Using Vite Dev Server**

Start the dev server on all network interfaces:

```powershell
cd frontend
npm run dev -- --host 0.0.0.0
```

Then access from mobile browser:
```
http://192.168.1.100:5173
```

**Option B: Deploy Built Files**

Serve the built files from `frontend/dist` using any web server.

---

## 🔥 Firewall Configuration

If you still can't connect, check your firewall:

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Allow Python (for backend) and Node.js (for frontend)

**Or temporarily disable firewall for testing:**
```powershell
# Run as Administrator
netsh advfirewall set allprofiles state off
# Remember to turn it back on!
netsh advfirewall set allprofiles state on
```

---

## 🧪 Testing the Connection

### Test Backend from Mobile Browser

Open mobile browser and navigate to:
```
http://192.168.1.100:8000/docs
```

You should see the FastAPI documentation page.

### Test Opponent API

Try this URL in mobile browser:
```
http://192.168.1.100:8000/opponent/gpu-status
```

Should return JSON like:
```json
{
  "gpu_available": true,
  "gpu_enabled": true,
  "backend_info": "GPU (CuPy) - NVIDIA GeForce RTX 4070"
}
```

---

## 📱 Offline Mode Details

### How It Works

1. **User makes a move** → Frontend tries to contact backend
2. **Backend unreachable** → Frontend detects network error
3. **Automatic fallback** → Uses client-side random move selection
4. **Move is made** → Game continues without interruption

### What You'll See

**Messages:**
```
Opponent is thinking...
Backend unreachable, using offline mode...
Opponent played: e5 (offline mode)
```

**Limitations:**
- Only random moves (no strategic AI profiles)
- No GPU acceleration
- No position evaluation scores

### When to Use Offline Mode

✅ **Good for:**
- Testing the UI on mobile
- Playing casual games
- When backend is not available
- Quick testing without server setup

❌ **Not suitable for:**
- Strategic opponent profiles (aggressive, defensive, etc.)
- GPU-accelerated analysis
- Position evaluation

---

## 🐛 Troubleshooting

### "Failed to fetch" Error

**Cause:** Backend is unreachable

**Solutions:**
1. Check backend is running: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Verify IP address is correct
3. Check firewall settings
4. Ensure mobile and computer are on same WiFi network
5. **Or just use offline mode** (automatic fallback)

### "CORS Error"

**Cause:** Backend doesn't allow requests from mobile device

**Solution:** Backend already has CORS configured for all origins (`allow_origins=["*"]`)

If you still see CORS errors, check `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be "*" for mobile access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Offline Mode Not Working

**Check:**
1. Make sure you're using the latest version of `boardView.js`
2. Check browser console for JavaScript errors
3. Verify chess.js library is loaded

---

## ✅ Summary

**Two Ways to Use on Mobile:**

1. **Offline Mode (Easiest)**
   - No configuration needed
   - Automatic fallback
   - Random moves only

2. **Full Backend Connection**
   - Configure IP address
   - All opponent profiles available
   - GPU acceleration (if available)

**Recommended:** Try offline mode first, then configure backend connection if you need strategic opponents.


