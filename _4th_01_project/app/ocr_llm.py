from PIL import Image
import numpy as np
from openai import OpenAI
import os
from paddleocr import PaddleOCR
from .config import load_config

class OCR_LLM():

    def __init__(self, cfg):
        super().__init__()

        self.cfg = load_config()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model_name = self.cfg['OPENAI_MODEL_NAME']

    
    def image_ocr(self, img_file):

        image = Image.open(img_file).convert("RGB")
        image = np.array(image)
        ocr = get_ocr_model()
        result_list = ocr.predict(image)
        
        text = result_list[0]['rec_texts']
        poly = result_list[0]['rec_polys']
        res = self.group_text_by_y(text, poly)

        return list(res)
    
    def group_text_by_y(self, rec_texts, rec_polys, y_threshold=15):

        lines = []

        for text, poly in zip(rec_texts, rec_polys):
            # 중심 좌표 계산
            poly = np.array(poly) 
            x_center = poly[:, 0].mean()
            y_center = poly[:, 1].mean()

            matched = False
            for group in lines:
                if abs(group['y'] - y_center) < y_threshold:
                    group['items'].append((x_center, text))
                    matched = True
                    break

            if not matched:
                lines.append({'y': y_center, 'items': [(x_center, text)]})

        # 정렬
        sorted_lines = []
        for group in sorted(lines, key=lambda g: g['y']):
            sorted_texts = sorted(group['items'], key=lambda x: x[0])  # x축 정렬
            line_text = ' '.join([t[1] for t in sorted_texts])
            sorted_lines.append(line_text)

        return sorted_lines
    
    def keyword_llm(self, word_list):
        client = OpenAI()
        text = ', '.join(word_list)

        prompt = f"""
        다음은 건강기능식품 관련 제품 정보에서 추출한 비정형 텍스트 리스트입니다:

        {text}

        이 정보를 기반으로 제품을 대표할 수 있는 의미 있는 키워드 5개를 뽑아주세요.
        가능하면 아래 기준을 고려하세요:
        - 들어온 순서는 중요성과는 무관합니다.
        - 제품명으로 생각되는 키워드 위주로 뽑아주세요.
        - 한국어로만 된 단어만 뽑아주세요
        - 영어로 된 단어는 제외해주세요.
        - 유아, 어린이, 임산부, 남성, 여성 등 특정 대상 나이 표현 단어 뽑아주세요.

        - '' 안에 있는 것은 하나의 단어로 취급하므로 절대 쪼개지 마세요.


        결과는 리스트 형태로 출력해주세요 (예: ['키워드1', '키워드2', ...]).
        제품명으로 생각되는 키워드를 앞쪽에 배치해주세요
        """

        response = client.chat.completions.create(model=self.openai_model_name, messages=[{"role": "user", "content": prompt}], temperature=0.3)

        return response.choices[0].message.content

    def ocr_to_llm(self, img_file):

        word_list = self.image_ocr(img_file)
        return self.keyword_llm(word_list)


# 전역변수 선언 -> 초기화  

ocr_model = None
def get_ocr_model():
    global ocr_model
    if ocr_model is None:
        ocr_model = PaddleOCR(
            lang='korean',
            use_doc_orientation_classify=False,
            use_doc_unwarping=True,
            use_textline_orientation=False
        )
    return ocr_model
