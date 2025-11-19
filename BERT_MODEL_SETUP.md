# BERT Model Setup for StrOrigin Analysis (Optional Feature)

## What is this?

**StrOrigin Change Analysis** is an optional feature in VRS Manager v1119.0+ that uses AI (BERT) to analyze how different StrOrigin changes really are.

## How It Works (Smart Dual-Mode System)

VRS Manager **automatically** tries to use the BERT model in this order:

1. **Online Mode (Default)** - If you have internet, it automatically downloads the model from Hugging Face when first needed
2. **Offline Mode (Fallback)** - If no internet, it uses a locally-installed model
3. **Graceful Skip** - If neither works, all other features continue working normally

**This means:**
- ✅ Computers WITH internet: **Works automatically!** No setup needed!
- ✅ Computers WITHOUT internet: Use `download_model.bat` first, then works offline
- ✅ VRS Manager works perfectly fine WITHOUT the model (all other features continue)

---

## For Users WITH Internet (Automatic Mode)

### No Setup Required!

Just run VRS Manager normally. When you process a file with StrOrigin changes:
- First time: Downloads model automatically (~5-10 minutes, 447MB)
- After that: Uses cached model (instant)
- Works seamlessly!

**Requirements:**
- Internet connection (first use only)
- ~1GB free disk space
- Python packages will auto-install

**You'll see:**
```
→ Attempting to load BERT model from Hugging Face (online mode)...
  [Downloading model...]
✓ Model loaded successfully from Hugging Face
→ Running StrOrigin analysis...
```

---

## For Users WITHOUT Internet (Offline Mode)

### Step 1: Prepare on a Computer WITH Internet

1. Download VRS Manager to a computer that HAS internet
2. Navigate to VRS Manager folder in Command Prompt:
   ```
   cd C:\path\to\VRSManager
   ```
3. Run the offline setup script:
   ```
   download_model.bat
   ```
4. Wait 5-10 minutes for download (447MB)
5. You'll see: `SUCCESS! Model downloaded and ready for offline use.`

### Step 2: Transfer to Offline Computer

1. Copy the entire `models` folder (next to VRSManager.exe)
2. Transfer to your offline computer
3. Place the `models` folder next to VRSManager.exe on the offline computer
4. Done! VRS Manager will use the offline model

**You'll see:**
```
→ Attempting to load BERT model from Hugging Face (online mode)...
ℹ️  Online mode unavailable: [connection error]
→ Trying local cache...
✓ Model loaded from local cache: models/kr-sbert/
→ Running StrOrigin analysis...
```

---

## Alternative: Manual Download (Advanced Users)

If you have Python and pip installed:

```bash
# Install required package
pip install sentence-transformers

# Download model to local cache
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS').save('./models/kr-sbert')"
```

---

## What Does This Feature Do?

When you run **Working VRS Check** on files with StrOrigin changes:

**Without model:**
- Standard output (Work Transform, Deleted Rows, Summary)
- Warning message about missing model

**With model:**
- All standard output PLUS
- New sheet: "StrOrigin Change Analysis"
- Shows which changes are trivial vs substantial:
  - `"Punctuation/Space Change"` - Only punctuation/spaces differ
  - `"94.5% similar"` - Minor wording change
  - `"30.2% similar"` - Major content change

---

## Frequently Asked Questions

**Q: Do I need this?**
A: No, it's optional. VRS Manager works fine without it.

**Q: Is it safe?**
A: Yes, it's an official Korean language model from Seoul National University.

**Q: Does it work offline?**
A: Yes! After the one-time download, no internet is needed.

**Q: How much disk space?**
A: 447MB (about the size of a smartphone photo album)

**Q: Can I delete it later?**
A: Yes, just delete the `models/` folder. VRS Manager will continue working.

**Q: Will this slow down my processing?**
A: Slightly. StrOrigin analysis adds ~2-5 seconds for files with many StrOrigin changes.

---

## Troubleshooting

**"Module not found: sentence_transformers"**
```bash
pip install sentence-transformers
```

**"BERT model not found" even after download**
- Make sure `models/kr-sbert/` folder exists next to VRSManager.exe
- Re-run: `python download_bert_model.py`

**Download fails / internet error**
- Check internet connection
- Try again later (Hugging Face servers may be busy)
- Use manual download method

---

## Technical Details

- **Model**: `snunlp/KR-SBERT-V40K-klueNLI-augSTS`
- **Size**: 447MB
- **Type**: Korean Sentence-BERT for semantic similarity
- **Source**: Hugging Face / Seoul National University
- **License**: Open source
- **Storage**: `models/kr-sbert/` directory

---

**Questions?** Check the main README or visit: https://github.com/NeilVibe/VRS-Manager
