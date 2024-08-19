from fastapi import APIRouter

router = APIRouter()


@router.get("/speech/application")
def start_speech_application_by_abstract():
    print("start speech_application_by_abstract")
