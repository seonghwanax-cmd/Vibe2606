# 파이썬연습.py

# 숫자와 글자를 담는 상자 만들기
X = 100
Y = 200
strA = "문자열을 저장"

# 지금 만든 정보를 보여주기
print(dir())          # 이 파일에서 사용할 수 있는 이름들을 보여줘요
print(len(strA))      # 글자 상자(strA) 안에 몇 글자가 있는지 알려줘요

# 두 숫자를 곱하는 작은 기계 만들기
def times(a, b):
    return a * b

# 곱셈 기계를 사용해 보기
result = times(3, 4)
print(result)         # 3 곱하기 4는 12예요

# 사람 정보를 담는 상자 설계도 만들기
class Person:
    def __init__(self, id, name):
        self.id = id       # 이 사람의 번호를 저장해요
        self.name = name   # 이 사람의 이름을 저장해요

    def printInfo(self):
        print("ID:", self.id)
        print("Name:", self.name)

# 사람 상자를 하나 만들어 보아요
person1 = Person(1, "홍길동")

# 만든 사람 상자 속 정보를 화면에 보여줘요
person1.printInfo()
