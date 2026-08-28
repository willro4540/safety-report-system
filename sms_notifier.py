import os
from dotenv import load_dotenv

load_dotenv()

# 개발 중 무료 크레딧을 아끼기 위한 기본값: 실제 발송 대신 콘솔에 로그만 남긴다.
# 실제 데모/시연 때만 .env에서 SMS_ENABLED=true로 켠다.
SMS_ENABLED       = os.getenv("SMS_ENABLED", "false").lower() == "true"
SOLAPI_API_KEY    = os.getenv("SOLAPI_API_KEY")
SOLAPI_API_SECRET = os.getenv("SOLAPI_API_SECRET")
SMS_FROM_NUMBER   = os.getenv("SMS_FROM_NUMBER")


def send_sms_notification(to_number: str, text: str) -> bool:
    """민원 처리 결과(완료/기각) 알림 문자를 보낸다.

    이메일은 접수 완료 시점에 이미 발송되므로(ui/report.py), 이 함수는
    답변/처리 이후 단계에서만 호출한다.
    """
    if not to_number:
        print("[SMS 건너뜀] 수신자 전화번호가 없습니다.")
        return False

    if not SMS_ENABLED:
        print(f"[MOCK SMS] to={to_number} text={text}")
        return True

    from solapi import SolapiMessageService
    from solapi.model import RequestMessage

    message_service = SolapiMessageService(
        api_key=SOLAPI_API_KEY, api_secret=SOLAPI_API_SECRET
    )
    message = RequestMessage(from_=SMS_FROM_NUMBER, to=to_number, text=text)

    try:
        response = message_service.send(message)
        return response.group_info.count.registered_success > 0
    except Exception as e:
        print(f"[SMS 발송 실패] {e}")
        return False
