from django.core.management.base import BaseCommand
from app.utils import delete_uploaded_images

class Command(BaseCommand):
    help = "Deletes uploaded images in MEDIA_ROOT"

    def handle(self, *args, **kwargs):
        delete_uploaded_images()
        self.stdout.write(self.style.SUCCESS("✅ 이미지 삭제 완료!"))