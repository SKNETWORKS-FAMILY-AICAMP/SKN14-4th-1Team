import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from .ocr_llm import OCR_LLM
from .config import load_config
from .utils import get_user_profile_summary

load_dotenv()
CFG = load_config()

class RAG_Chatbot():

    def __init__(self):

        super().__init__()

        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')

        self.cfg = CFG
        self.ocr = OCR_LLM(self.cfg)

        self.openai_embedding_model = self.cfg["OPENAI_EMBEDDING_MODEL"]
        self.openai_model_name = self.cfg['OPENAI_MODEL_NAME']
        self.faiss_dir = self.cfg['FAISS_FILE_PATH']

        self.embeddings = get_embedding_model()
        self.vector_store = get_faiss_index()
        self.retriever = self.vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 3})

        self.llm = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=0.3, model_name=self.openai_model_name, max_tokens=1024)


    def run(self, question="", use_ocr=False, search_mode=False, img_file=None, user=None, chat_history=None):
        
        if user != None:

            user_detail = get_user_profile_summary(user)

        if chat_history is not None and len(chat_history) > 0:
            history_text = ""
            for item in chat_history:
                prefix = "사용자" if item["role"] == "human" else "ai"
                history_text += f"{prefix}: {item['content']}\n"
        else:
            history_text = ""

        if use_ocr:

            if img_file is None:
                raise ValueError("OCR 모드가 활성화되어 있으나 이미지 파일이 제공되지 않았습니다. 이미지를 업로드한 후 다시 시도해 주세요.")
        
            try:
                question = str(self.ocr.image_ocr(img_file))
            except Exception as e:
                raise RuntimeError(f"OCR 처리 중 예상치 못한 오류가 발생했습니다: {e}")

            retrieved_docs = self.retriever.get_relevant_documents(question)
            context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
            prompt_template = self.prompt_ocr(question=question, context=context)
        
        else:
            try:
                if not question.strip():
                    raise ValueError("질문이 비어 있습니다. 텍스트를 입력해 주세요.")
                
                retrieved_docs = self.retriever.get_relevant_documents(question)
                context = "\n---\n".join([doc.page_content for doc in retrieved_docs])

                if search_mode==True:
                    prompt_template = self.prompt_ocr(question=question, context=context)
                else:
                    print(f'{history_text=}')
                    prompt_template = self.prompt(question=question, context=context, user_summary=user_detail, history=history_text)

            except Exception as e:
                raise RuntimeError(f"텍스트 처리 중 오류가 발생했습니다: {e}")

            
        response = self.llm.invoke(prompt_template.format(question=question, context=context))
    
        return response.content
    
    def prompt(self, question, context, user_summary="", history=""):
        
        system_prompt = PromptTemplate.from_template("""
        
         [System Instruction]
            - 당신은 건강기능식품과 영양제 추천에 전문적인 경험이 있는 상담 전문가입니다.
            - 답변은 반드시 아래 규칙을 모두 지켜주세요.

            - 답변은 상담사가 직접 대화하듯, 친근하고 자연스러운 말투로 작성하세요.
            - 첫 답변만 입력된 사용자의 이름, 건강 정보, 관심사 등은 한 문장 또는 두 문장 이내로 자연스럽게 녹여서 안내합니다.
                입력되지 않는 부분은 굳이 언급할 필요 없습니다.
                - 예시: 반가워요! 임신 중이시고 소화/장 건강과 스트레스 관리에 관심이 많으시군요."
            - user_summary에 없는 내용이 채팅 내용에 들어있다면, 채팅 내용을 우선으로 합니다.
                예를 들어 user_summary에는 임신했다고 되어있지만, 현재 임신하지 않는 상태라하고 언급되면 임신하지 않는 상태 인지한 후 답변을 이어나가세요.
            - 필요 이상으로 반복되는 정보, 딱딱한 나열, 사무적인 표현은 사용하지 마세요.
            - 안내가 필요한 경우도 실제 상담사가 설명하듯 간결하고 배려 있게 안내합니다.
            - 제품 추천 시에도 "이런 제품이 도움이 될 수 있어요~" 등 자연스럽게 연결합니다.
            - 문서에 정보가 없으면, "해당 정보는 문서에 없어요"라고만 간결히 안내하고, 너무 길게 설명하지 않습니다.
            - **영양제 추천(=복수의 제품 제안)은 아래의 경우에만 하세요:**
            - 사용자의 질문에 "추천", "추천해줘", "영양제 추천", "뭐가 좋아요?", "추천 부탁" 등  
                **명확하게 추천 의도가 있을 때만**
            - 예시:  
                - "피로에 좋은 영양제 추천해줘"  
                - "여성 건강에 맞는 영양제 뭐가 좋아?"  
            - 단순 효능/부작용/상담 질문에는 제품 추천 없이 안내만 해주세요.
            - **추천 의도가 없는 말에는 제품을 절대 제품 추천 하지 마세요.**

            - 제품 추천시에는, 제품명·제조사·효능·주의사항 등 **문서에 있는 정보만** 구체적으로 안내합니다.
            - 문서에 없는 항목은 "문서에 정보 없음"이라고 적으세요.

            - 영양제 추천 답변 마지막에만 꼭 붙이세요:  
            "건강기능식품은 의약품이 아니므로, 섭취 전 반드시 전문가와 상담하시길 권장드립니다."
                                                     

            [Example - Output Indicator]
            예시:

            안녕하세요! {user_summary}
            요즘 건강이나 생활에 여러 고민이 있으셨던 것 같아요. 궁금하신 내용을 바탕으로 아래와 같이 안내드릴게요.

            1. 제품명은 **000**입니다.  
            제조사는 **000**입니다.  
            이 제품은 **000**에 도움을 줄 수 있다고 문서에 나와 있습니다.  
            복용 시 주의사항: **000**  
            보관 방법: **000**  
            유통기한: **000**

            2. 제품명은 ...
            ---
            ※ 문서에 정보가 없는 항목은 반드시 "문서에 정보 없음"이라고 작성합니다.
            ※ 추측, 생성, 일반적 상식, 또는 문서/히스토리에 없는 정보는 절대 포함하지 않습니다.
            ※ 모든 답변은 완결된 존댓말, 친절하고 공감 있는 문장으로 마무리합니다.

            [Chat History]
            {history}

            [User Information]
            {user_summary}

            [Context]
            {context}

            [Input Data]
            {question}
            """)

        return system_prompt.format(context=context, question=question, user_summary=user_summary, history=history)
  
    
    def prompt_ocr(self, question, context):

        prompt = PromptTemplate.from_template(f"""
            [System Instruction]
            당신은 여러 문서를 분석하여 사용자의 질문에 친절히 답변하는 건강기능식품 전문가입니다.

            입력된 키워드가 문서에서 일부라도 포함된 유사한 건강기능식품 3종을 찾습니다.
            키즈, 유아는 같은 의미입니다.

            응답 시 유의사항:
            - 반드시 주어진 문서 내 정보만을 기반으로 답변하세요.
            - 정보를 찾을 수 없는 경우, "해당 문서에서 찾을 수 없습니다."라고 답변하세요.
            - 정보를 찾은 경우 아래 항목을 포함하여 문장을 평서형으로 작성하세요:
            
            1. 제품명 및 브랜드
            2. 기대 효과 및 기능성
            3. 섭취 방법                                   
            4. 주요 성분 및 함량
            5. 섭취 시 주의사항
            - 절대 말을 지어내거나 문서를 벗어난 내용을 포함하지 마세요.
            - 문장이 여러개시 한 줄에 한문장만 입력되도록 하세요.

            # OCR 키워드 입력
            {question}

            # 문서 내용
            {context}

            # 답변:
            <<제품명>>
                - 브랜드:
                - 기대효과 및 기능성:
                - 섭취 방법:
                - 주요 성분 및 함량:
                - 섭취 시 주의사항:
              ,

            <<제품명2>>
                - 브랜드:
                - 기대효과 및 기능성:
                - 섭취 방법:
                - 주요 성분 및 함량:
                - 섭취 시 주의사항:
              ,

            <<제품명>>
                - 브랜드:
                - 기대효과 및 기능성:
                - 섭취 방법:
                - 주요 성분 및 함량:
                - 섭취 시 주의사항:
            """)
        
        return prompt

# 전역변수 선언 -> 초기화
embedding_model = None
faiss_index = None

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        embedding_model = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model=CFG['OPENAI_EMBEDDING_MODEL']
        )
    return embedding_model

def get_faiss_index():
    global faiss_index
    if faiss_index is None:
        embeddings = get_embedding_model()
        faiss_index = FAISS.load_local(CFG['FAISS_FILE_PATH'], index_name='index', embeddings=embeddings, allow_dangerous_deserialization=True)
    return faiss_index