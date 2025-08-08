from django.apps import AppConfig
from . rag_chatbot import get_embedding_model, get_faiss_index
from .utils import delete_uploaded_images
from .ocr_llm import get_ocr_model
import threading, time


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        threading.Thread(target=self.initialize_models, daemon=True).start() #damon=True: django 종료될 때 백그라운드 쓰레드도 종료

        threading.Thread(target=self.start_image_cleanup_scheduler, daemon=True).start()

    def initialize_models(self):

        ocr = get_ocr_model()
        embedding = get_embedding_model()
        faiss = get_faiss_index()

        print('모든 모델 초기화 완료')

    def start_image_cleanup_scheduler(self):
        while True:
            delete_uploaded_images()
            print('🧹 이미지 정리 완료')
            time.sleep(24 * 60 * 60)  # 하루마다 실행

        
