# FRED API Setup Guide for SOFR Integration

## What is FRED?
**FRED** (Federal Reserve Economic Data) is the official database maintained by the Federal Reserve Bank of St. Louis. It provides access to over 800,000 economic time series, including the **SOFR** (Secured Overnight Financing Rate).

## Why Use FRED for SOFR?
- ✅ **Official Source**: Direct from the Federal Reserve Bank of New York
- ✅ **Free API**: No cost for non-commercial use
- ✅ **Reliable**: Updated daily with official rates
- ✅ **Easy Integration**: Simple REST API

## Setup Instructions

### Step 1: Get Your Free FRED API Key

1. Visit: https://fred.stlouisfed.org/
2. Click **"My Account"** (top right) → **"Create Account"** (if you don't have one)
3. After logging in, go to: https://fred.stlouisfed.org/docs/api/api_key.html
4. Click **"Request API Key"**
5. Fill out the form (takes 1 minute)
6. You'll receive your API key instantly!

**Example API Key format**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### Step 2: Set the Environment Variable

Choose your operating system:

#### **Windows (PowerShell)**
```powershell
# Temporary (current session only)
$env:FRED_API_KEY="your_api_key_here"

# Permanent (all sessions)
[System.Environment]::SetEnvironmentVariable('FRED_API_KEY', 'your_api_key_here', 'User')
```

#### **Windows (Command Prompt)**
```cmd
# Temporary (current session only)
set FRED_API_KEY=your_api_key_here

# Permanent (all sessions)
setx FRED_API_KEY "your_api_key_here"
```

#### **macOS / Linux**
```bash
# Temporary (current session only)
export FRED_API_KEY="your_api_key_here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export FRED_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify the Setup

Run the test script to verify everything works:

```bash
cd Portfolio
python test_fred_sofr.py
```

You should see output like:
```
[Risk-Free Rate] Using SOFR from FRED: 4.33% (as of 2024-10-18)
✅ FRED API is working! SOFR Rate: 4.33%
```

## Fallback Behavior

If FRED API is not available, the system automatically falls back to:
1. **13-Week Treasury Bill (^IRX)** from Yahoo Finance
2. **Default rate of 4.33%** if neither source is available

This ensures your Sharpe Ratio calculations always work, even without the API key.

## API Usage Limits

FRED API allows:
- **120 requests per minute**
- **Unlimited total requests per day**

Your portfolio app only makes **1 request per analysis**, so you won't hit any limits.

## Troubleshooting

### "FRED_API_KEY not found"
- Make sure you've set the environment variable correctly
- Restart your terminal/IDE after setting it
- Verify with: `echo %FRED_API_KEY%` (Windows) or `echo $FRED_API_KEY` (macOS/Linux)

### "Could not fetch SOFR from FRED"
- Check your internet connection
- Verify your API key is correct
- The app will automatically fallback to ^IRX (Treasury Bill)

### Still having issues?
The system will work fine without FRED API - it will use the 13-Week Treasury Bill (^IRX) as the risk-free rate, which is a standard industry practice.

## Additional FRED Data Sources

Once you have the API key, you can access other useful financial data:
- **DFF** - Federal Funds Rate
- **DGS10** - 10-Year Treasury Constant Maturity Rate
- **T5YIE** - 5-Year Breakeven Inflation Rate
- **UNRATE** - Unemployment Rate

See full list at: https://fred.stlouisfed.org/categories

## Questions?

For FRED API support: https://fred.stlouisfed.org/docs/api/fred/
For portfolio app issues: Check the main README.md


