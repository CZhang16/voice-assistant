"""
小白语音助手 - 唤醒词测试
"""
import sys
sys.path.insert(0, r'C:\Users\fourStar\clawd\voice-assistant')

import struct
import pvporcupine
import pyaudio
from src.config import Config

def test_wake_word():
    config = Config()
    access_key = config.get("wake_word.access_key")
    sensitivity = config.get("wake_word.sensitivity", 0.5)
    
    print("=== Xiaobai Wake Word Test ===")
    print(f"Access Key: {'Configured' if access_key else 'Missing'}")
    
    try:
        # 使用英文 computer 测试
        print("\nInitializing Porcupine (keyword: computer)...")
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["computer"],
            sensitivities=[sensitivity]
        )
        print(f"[OK] Porcupine initialized")
        print(f"     Sample rate: {porcupine.sample_rate} Hz")
        print(f"     Frame length: {porcupine.frame_length} samples")
        
        # 测试麦克风
        print("\nChecking microphone...")
        pa = pyaudio.PyAudio()
        info = pa.get_default_input_device_info()
        print(f"[OK] Default input: {info['name']}")
        
        # 打开音频流
        print("\nListening (say 'computer' to test, Ctrl+C to stop)...")
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        stream.start_stream()
        
        # 监听
        import time
        detected = False
        
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                print("\n[DETECTED] Wake word detected!")
                detected = True
                break
        
        # 清理
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
        
        print("\n[OK] Test completed")
        
    except KeyboardInterrupt:
        print("\n[STOPPED] User interrupted")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wake_word()
