"""
Test script for opponent API endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_gpu_status():
    """Test GPU status endpoint."""
    print("\n=== Testing GPU Status ===")
    response = requests.get(f"{BASE_URL}/opponent/gpu-status")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"GPU Available: {data['gpu_available']}")
    print(f"GPU Enabled: {data['gpu_enabled']}")
    print(f"Backend Info: {data['backend_info']}")
    return data

def test_gpu_toggle():
    """Test GPU toggle endpoint."""
    print("\n=== Testing GPU Toggle ===")
    
    # Disable GPU
    response = requests.post(f"{BASE_URL}/opponent/gpu-toggle?enable=false")
    print(f"Disable GPU - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Enable GPU
    response = requests.post(f"{BASE_URL}/opponent/gpu-toggle?enable=true")
    print(f"Enable GPU - Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_opponent_move(profile="random"):
    """Test opponent move generation."""
    print(f"\n=== Testing Opponent Move ({profile}) ===")
    
    # Starting position
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    payload = {
        "fen": fen,
        "profile": profile
    }
    
    response = requests.post(
        f"{BASE_URL}/opponent/move",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Move UCI: {data['move_uci']}")
        print(f"Move SAN: {data['move_san']}")
        if data.get('evaluation'):
            print(f"Evaluation: {data['evaluation']}")
    else:
        print(f"Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def test_all_profiles():
    """Test all opponent profiles."""
    profiles = ["random", "aggressive", "defensive", "moderate", "defensive_passive"]
    
    for profile in profiles:
        test_opponent_move(profile)

if __name__ == "__main__":
    print("=" * 60)
    print("BishopForge Opponent API Test Suite")
    print("=" * 60)
    
    try:
        # Test GPU status
        gpu_status = test_gpu_status()
        
        # Test GPU toggle
        test_gpu_toggle()
        
        # Test all opponent profiles
        test_all_profiles()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server")
        print("Make sure the backend is running: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")

