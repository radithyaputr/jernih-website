# OpenRouter API Setup Instructions

## Why OpenRouter?
- **Higher Quota**: 200 requests/minute (vs Gemini's 20 requests/day)
- **Free Tier**: No credit card required
- **Multiple Models**: Access to Gemini, Claude, GPT-4, and 400+ models with one key
- **OpenAI Compatible**: Easy integration with existing code

## Quick Setup (5 minutes)

### Step 1: Create Free Account
1. Go to https://openrouter.ai/
2. Click "Sign Up" (top right)
3. Sign up with Google, GitHub, or Email
4. **No credit card required for free tier**

### Step 2: Generate API Key
1. After login, go to https://openrouter.ai/keys
2. Click "Create Key"
3. Give it a name (e.g., "JERNIH-LKS-2026")
4. Copy the key (starts with `sk-or-v1-...`)

### Step 3: Add Key to .env File
1. Open `backend/.env`
2. Replace the placeholder with your real key:
   ```
   OPENAI_API_KEY=sk-or-v1-your-actual-key-here
   ```
3. Save the file

### Step 4: Restart Backend
```cmd
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Test AI Endpoint
```cmd
curl -X POST http://localhost:8000/api/copilot/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Saya butuh bantuan PIP untuk anak saya\"}"
```

## Free Tier Limits
- **Daily**: 50 requests/day
- **Per Minute**: 20 requests/minute
- **Models**: Only models ending with `:free` (e.g., `google/gemini-2.0-flash-exp:free`)

## Paid Tier (Optional)
If you need unlimited usage:
1. Add $5-$20 credits to your account
2. Access to ALL models (not just `:free` ones)
3. Pay-per-token pricing (very affordable)
4. Credits never expire

## Current Configuration
The app is already configured to use OpenRouter with:
- **Model**: `google/gemini-2.0-flash-exp:free`
- **Endpoint**: `https://openrouter.ai/api/v1`
- **API Key Source**: `OPENAI_API_KEY` env variable

## Troubleshooting

### "401 Unauthorized"
- API key is invalid or missing
- Check `.env` file has correct key
- Restart backend after changing `.env`

### "429 Rate Limit"
- Free tier limit reached (50/day or 20/min)
- Wait a few minutes or add credits to account

### "Model not found"
- Make sure using a `:free` model on free tier
- Change model in `gemini_service.py` if needed

## Alternative: Use Gemini Direct
If you prefer to stick with Google's Gemini API directly:
1. Remove or comment out `OPENAI_API_KEY` in `.env`
2. Keep `GEMINI_API_KEY` 
3. Code will automatically fall back to Gemini (20 req/day limit)

---
**Documentation**: https://openrouter.ai/docs
**Pricing**: https://openrouter.ai/pricing
