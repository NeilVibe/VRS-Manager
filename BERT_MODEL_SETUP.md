# BERT Model Setup for StrOrigin Analysis (Optional Feature)

## What is this?

**StrOrigin Change Analysis** is an optional feature in VRS Manager v1119.0+ that uses AI (BERT) to analyze how different StrOrigin changes really are.

**If you don't have the model:**
- VRS Manager works perfectly fine WITHOUT it
- All other features work normally
- You'll see a message: "BERT model not found - StrOrigin analysis unavailable"
- The "StrOrigin Change Analysis" sheet won't be created (but everything else works)

**If you want this feature:**
- Download the 447MB Korean BERT model (one-time setup)
- Takes 5-10 minutes depending on internet speed
- Enables automatic analysis: "Punctuation/Space Change" or "XX.X% similar"

---

## Option 1: For .exe Users (Recommended)

### Step 1: Download Python (if not installed)
1. Go to: https://www.python.org/downloads/
2. Download Python 3.10 or newer
3. Install with "Add to PATH" checkbox checked

### Step 2: Download the Model
1. Open Command Prompt (cmd) or PowerShell
2. Navigate to VRS Manager folder:
   ```
   cd C:\path\to\VRSManager
   ```
3. Run the download script:
   ```
   python download_bert_model.py
   ```
4. Wait 5-10 minutes for download (447MB)
5. Done! Model is now available offline

### Step 3: Verify
Run VRS Manager .exe again. You should see:
- "Running StrOrigin analysis (punctuation/space + BERT similarity)..."
- New sheet: "StrOrigin Change Analysis"

---

## Option 2: Manual Download (Advanced Users)

If you have Python and pip installed:

```bash
# Install required packages
pip install sentence-transformers

# Download model
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
