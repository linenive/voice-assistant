import RPi.GPIO as GPIO
from config import BUTTON_PIN

def setup():
    """GPIO 초기화"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_pressed():
    """버튼이 눌렸는지 확인"""
    return GPIO.input(BUTTON_PIN) == GPIO.LOW

def cleanup():
    """GPIO 정리"""
    GPIO.cleanup()
