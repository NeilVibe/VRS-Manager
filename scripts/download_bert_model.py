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
    print("Downloading Korean BERT Model for Phase 3.0")
    print("=" * 60)
    print()

    model_name = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'
    local_model_path = './models/kr-sbert'
    abs_path = os.path.abspath(local_model_path)

    print(f"Model: {model_name}")
    print(f"Destination: {abs_path}")
    print(f"Size: ~500MB (this will take a few minutes)")
    print()

    # Create directory if it doesn't exist
    try:
        os.makedirs(local_model_path, exist_ok=True)
        print(f"✓ Created directory: {abs_path}")
    except Exception as e:
        print(f"❌ Failed to create directory: {e}")
        return False

    print("📥 Downloading model from Hugging Face...")
    print("(This requires internet connection - first time only)")
    print()

    try:
        # Download and load model
        print("  → Downloading model...")
        model = SentenceTransformer(model_name)
        print("  ✓ Model downloaded")

        print("💾 Saving model locally...")
        model.save(local_model_path)
        print(f"  ✓ Model saved to: {abs_path}")

        # CRITICAL: Verify the model was actually saved
        required_files = ['config.json', 'pytorch_model.bin']
        for req_file in required_files:
            file_path = os.path.join(local_model_path, req_file)
            if not os.path.exists(file_path):
                print(f"❌ CRITICAL: Missing required file: {req_file}")
                print(f"   Expected at: {os.path.abspath(file_path)}")
                return False

        print("  ✓ Verified required model files exist")

        print()
        print("=" * 60)
        print("✅ MODEL DOWNLOAD COMPLETE!")
        print("=" * 60)
        print()
        print(f"Model saved to: {abs_path}")
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
        print("🎯 Model is ready for FULL version build!")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR DOWNLOADING MODEL")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print(f"Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
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
