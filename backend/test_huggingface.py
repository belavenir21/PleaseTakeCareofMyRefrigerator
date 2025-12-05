"""
Test script to verify Hugging Face API connection
"""
from django.conf import settings
from huggingface_hub import InferenceClient
from PIL import Image
import requests
from io import BytesIO

# Get API token from settings
api_token = settings.HUGGINGFACE_API_TOKEN

print(f"🔑 API Token exists: {bool(api_token)}")
print(f"🔑 Token starts with 'hf_': {api_token.startswith('hf_') if api_token else False}")

if not api_token:
    print("❌ No API token found!")
    exit(1)

# Test with a sample image URL (apple image)
image_url = "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400"

print(f"\n📡 Downloading test image...")
response = requests.get(image_url)
img = Image.open(BytesIO(response.content))
print(f"✅ Image loaded: {img.size}")

print(f"\n🤖 Testing Hugging Face Object Detection...")
try:
    client = InferenceClient(token=api_token)
    detections = client.object_detection(img)
    
    print(f"\n✅ SUCCESS! Detected {len(detections)} objects:")
    for d in detections[:5]:  # Show first 5
        print(f"   - {d['label']}: {d['score']*100:.1f}% confidence")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
