import re

class DataPreparation:

    def __init__(self) -> None:
        pass

    def clean_text(self, text) -> str:
        text = text.lower()  # แปลงข้อความเป็นตัวพิมพ์เล็ก
        text = re.sub(r'\[.*?\]', '', text)  # ลบเนื้อหาที่อยู่ในวงเล็บเหลี่ยม
        text = re.sub(r'https?://\S+|www\.\S+', '', text)  # ลบ URLs
        text = re.sub(r'<.*?>+', '', text)  # ลบ HTML tags
        text = re.sub(r'\n', '', text)  # ลบการขึ้นบรรทัดใหม่
        text = re.sub(r'[^a-zA-Z]', ' ', text)  # เก็บเฉพาะตัวอักษร
        text = re.sub(r'\s+', ' ', text).strip()  # ลบช่องว่างที่ไม่จำเป็น
        return text
