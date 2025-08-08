import re, os
from django.conf import settings

def get_user_profile_summary(user):

    from uauth.models import UserDetail

    try:
        detail = UserDetail.objects.get(user=user)
    except UserDetail.DoesNotExist:
        return "사용자 정보가 없습니다."

    birthday = detail.birthday
    gender = detail.gender
    is_pregnant = detail.is_pregnant
    health_concerns = detail.health_concerns

    summary = "[사용자 정보 요약]"
    
    if birthday:
        summary += f"출생연도: {birthday.year}년, "
    
    if gender == 'M':
        summary += "성별: 남성, "
    elif gender == 'F':
        summary += "성별: 여성, "
        if is_pregnant:
            summary += "현재 임신 중, "
    
    if health_concerns:
        summary += f"건강 관심사: {health_concerns}."
    
    return summary.strip()

def parse_product_detail(raw_text):
    result = {}

    # 제품명 추출
    product_match = re.search(r"<<(.+?)>>", raw_text)
    if product_match:
        result["제품명"] = product_match.group(1).strip()

    # 항목 정의
    fields = [
        "브랜드",
        "기대효과 및 기능성",
        "섭취 방법",
        "주요 성분 및 함량",
        "섭취 시 주의사항"
    ]

    for i in range(len(fields)):
        start = fields[i]
        end = fields[i+1] if i + 1 < len(fields) else None

        if end:
            # 수정된 정규식
            pattern = rf"-?\s*{start}:\s*(.*?)(?=-?\s*{end}:|$)"
        else:
            pattern = rf"-?\s*{start}:\s*(.*)"

        match = re.search(pattern, raw_text, re.DOTALL)
        if match:
            value = match.group(1)
            value = re.sub(r'\s+', ' ', value).strip()
            value = re.sub(r'[-ㆍ·．・]*\s*$', '', value)
            result[start] = value

    # 키 변환
    parsed_clean = {
        "name": result.get("제품명", ""),
        "brand": result.get("브랜드", ""),
        "benefits": result.get("기대효과 및 기능성", ""),
        "how_to_take": result.get("섭취 방법", ""),
        "ingredients": result.get("주요 성분 및 함량", ""),
        "cautions": result.get("섭취 시 주의사항", "")
    }

    return parsed_clean


def delete_uploaded_images():
    upload_dir = settings.MEDIA_ROOT
    deleted_count = 0

    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted_count += 1

    print(f"[스케줄러] {deleted_count}개의 이미지가 삭제되었습니다.")