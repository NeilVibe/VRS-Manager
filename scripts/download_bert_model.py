#!/usr/bin/env python3
"""
One-time setup script to download Korean BERT model for StrOrigin analysis.
This downloads the model and saves it locally for offline use.
"""

from sentence_transformers import SentenceTransformer
import os

def download_model():
    """Download and save the Korean BERT model locally"""

    print("=" * 60)
    print("Downloading Korean BERT Model for Phase 2.3")
    print("=" * 60)
    print()

    model_name = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'
    local_model_path = './models/kr-sbert'

    print(f"Model: {model_name}")
    print(f"Destination: {local_model_path}")
    print(f"Size: ~500MB (this will take a few minutes)")
    print()

    # Create directory if it doesn't exist
    os.makedirs(local_model_path, exist_ok=True)

    print("📥 Downloading model from Hugging Face...")
    print("(This requires internet connection - first time only)")
    print()

    try:
        # Download and load model
        model = SentenceTransformer(model_name)

        print("💾 Saving model locally...")
        model.save(local_model_path)

        print()
        print("=" * 60)
        print("✅ MODEL DOWNLOAD COMPLETE!")
        print("=" * 60)
        print()
        print(f"Model saved to: {os.path.abspath(local_model_path)}")
        print()
        print("📂 Model files:")
        for root, dirs, files in os.walk(local_model_path):
            level = root.replace(local_model_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")

        print()
        print("🎯 Next steps:")
        print("  1. Model is ready for Phase 2.3 implementation")
        print("  2. VRS Manager will now work OFFLINE (no internet needed)")
        print("  3. Run git add models/ to track the model in git")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR DOWNLOADING MODEL")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Common issues:")
        print("  - No internet connection")
        print("  - Hugging Face API is down")
        print("  - Not enough disk space (~500MB needed)")
        print()
        return False

    return True

if __name__ == '__main__':
    success = download_model()
    exit(0 if success else 1)
