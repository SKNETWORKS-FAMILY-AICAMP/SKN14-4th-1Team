from django.db import models
from django.utils import timezone

# Create your models here.
class ChatMessage(models.Model):
    """대화 메시지를 저장하는 모델"""
    session_id = models.CharField(max_length=255, db_index=True)  # 세션 ID
    message_type = models.CharField(max_length=10, choices=[
        ('human', 'Human'),
        ('ai', 'AI')
    ])  # 메시지 타입 (사용자 또는 AI)
    content = models.TextField()  # 메시지 내용
    created_at = models.DateTimeField(default=timezone.now)  # 생성 시간
    
    class Meta:
        ordering = ['created_at']  # 시간순으로 정렬
        
    def __str__(self):
        return f"{self.session_id} - {self.message_type}: {self.content[:50]}..."