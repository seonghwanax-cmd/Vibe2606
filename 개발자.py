class Developer:
    def __init__(self, name, language, experience):
        self.name = name
        self.language = language
        self.experience = experience

    def introduce(self):
        print(
            f"안녕하세요. 저는 {self.name}이고 "
            f"{self.language} 개발자입니다. "
            f"경력은 {self.experience}년입니다."
        )

    def coding(self):
        print(f"{self.name}이(가) {self.language}로 코딩 중입니다.")