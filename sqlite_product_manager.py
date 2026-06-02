import sqlite3
from typing import List, Tuple, Optional

class ProductManager:
    """SQLite를 사용하여 제품 데이터를 관리하는 클래스"""
    
    def __init__(self, db_name: str = "products.db"):
        """
        데이터베이스 연결 초기화
        
        Args:
            db_name: 데이터베이스 파일 이름 (기본값: products.db)
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """데이터베이스에 연결"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"✓ 데이터베이스 '{self.db_name}'에 연결되었습니다.")
        except sqlite3.Error as e:
            print(f"✗ 데이터베이스 연결 오류: {e}")
    
    def create_table(self):
        """Products 테이블 생성"""
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY AUTOINCREMENT,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
            """
            self.cursor.execute(sql)
            self.conn.commit()
            print("✓ Products 테이블이 준비되었습니다.")
        except sqlite3.Error as e:
            print(f"✗ 테이블 생성 오류: {e}")
    
    def insert_product(self, product_name: str, product_price: int) -> bool:
        """
        제품 데이터 삽입
        
        Args:
            product_name: 제품 이름
            product_price: 제품 가격
            
        Returns:
            성공 여부
        """
        try:
            sql = """
            INSERT INTO Products (productName, productPrice)
            VALUES (?, ?)
            """
            self.cursor.execute(sql, (product_name, product_price))
            self.conn.commit()
            print(f"✓ 제품 '{product_name}' (가격: {product_price})이 추가되었습니다.")
            return True
        except sqlite3.Error as e:
            print(f"✗ 제품 삽입 오류: {e}")
            return False
    
    def select_all_products(self) -> List[Tuple]:
        """
        모든 제품 조회
        
        Returns:
            제품 정보 리스트 [(productID, productName, productPrice), ...]
        """
        try:
            sql = "SELECT * FROM Products"
            self.cursor.execute(sql)
            products = self.cursor.fetchall()
            return products
        except sqlite3.Error as e:
            print(f"✗ 조회 오류: {e}")
            return []
    
    def select_product_by_id(self, product_id: int) -> Optional[Tuple]:
        """
        특정 제품 조회 (ID로 검색)
        
        Args:
            product_id: 제품 ID
            
        Returns:
            제품 정보 (productID, productName, productPrice) 또는 None
        """
        try:
            sql = "SELECT * FROM Products WHERE productID = ?"
            self.cursor.execute(sql, (product_id,))
            product = self.cursor.fetchone()
            return product
        except sqlite3.Error as e:
            print(f"✗ 조회 오류: {e}")
            return None
    
    def select_products_by_name(self, product_name: str) -> List[Tuple]:
        """
        제품 이름으로 검색
        
        Args:
            product_name: 제품 이름 (부분 검색 가능)
            
        Returns:
            검색된 제품 정보 리스트
        """
        try:
            sql = "SELECT * FROM Products WHERE productName LIKE ?"
            self.cursor.execute(sql, (f"%{product_name}%",))
            products = self.cursor.fetchall()
            return products
        except sqlite3.Error as e:
            print(f"✗ 조회 오류: {e}")
            return []
    
    def update_product(self, product_id: int, product_name: str = None, 
                      product_price: int = None) -> bool:
        """
        제품 정보 수정
        
        Args:
            product_id: 수정할 제품 ID
            product_name: 새로운 제품 이름 (None이면 수정 안함)
            product_price: 새로운 제품 가격 (None이면 수정 안함)
            
        Returns:
            성공 여부
        """
        try:
            if product_name is not None and product_price is not None:
                sql = "UPDATE Products SET productName = ?, productPrice = ? WHERE productID = ?"
                self.cursor.execute(sql, (product_name, product_price, product_id))
            elif product_name is not None:
                sql = "UPDATE Products SET productName = ? WHERE productID = ?"
                self.cursor.execute(sql, (product_name, product_id))
            elif product_price is not None:
                sql = "UPDATE Products SET productPrice = ? WHERE productID = ?"
                self.cursor.execute(sql, (product_price, product_id))
            else:
                print("✗ 수정할 정보가 없습니다.")
                return False
            
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"✓ 제품 ID {product_id}이 수정되었습니다.")
                return True
            else:
                print(f"✗ 제품 ID {product_id}을 찾을 수 없습니다.")
                return False
                
        except sqlite3.Error as e:
            print(f"✗ 수정 오류: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """
        제품 삭제
        
        Args:
            product_id: 삭제할 제품 ID
            
        Returns:
            성공 여부
        """
        try:
            sql = "DELETE FROM Products WHERE productID = ?"
            self.cursor.execute(sql, (product_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"✓ 제품 ID {product_id}이 삭제되었습니다.")
                return True
            else:
                print(f"✗ 제품 ID {product_id}을 찾을 수 없습니다.")
                return False
                
        except sqlite3.Error as e:
            print(f"✗ 삭제 오류: {e}")
            return False
    
    def display_all_products(self):
        """모든 제품 정보를 보기 좋게 출력"""
        products = self.select_all_products()
        if not products:
            print("등록된 제품이 없습니다.")
            return
        
        print("\n" + "="*60)
        print(f"{'ID':<5} {'제품명':<25} {'가격':<15}")
        print("="*60)
        for product_id, product_name, product_price in products:
            print(f"{product_id:<5} {product_name:<25} {product_price:>10}원")
        print("="*60 + "\n")
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            print("✓ 데이터베이스 연결을 종료했습니다.")


# ============================================================================
# 사용 예제
# ============================================================================

if __name__ == "__main__":
    # ProductManager 인스턴스 생성
    manager = ProductManager()
    
    print("\n" + "="*60)
    print("【 제품 관리 시스템 】")
    print("="*60)
    
    # 1. 제품 추가 (INSERT)
    print("\n[1] 제품 추가")
    manager.insert_product("노트북", 1500000)
    manager.insert_product("마우스", 50000)
    manager.insert_product("키보드", 150000)
    manager.insert_product("모니터", 350000)
    
    # 2. 모든 제품 조회 (SELECT ALL)
    print("\n[2] 모든 제품 조회")
    manager.display_all_products()
    
    # 3. ID로 특정 제품 조회 (SELECT BY ID)
    print("[3] ID로 특정 제품 조회")
    product = manager.select_product_by_id(2)
    if product:
        product_id, product_name, product_price = product
        print(f"ID: {product_id}, 제품명: {product_name}, 가격: {product_price}원")
    
    # 4. 제품 이름으로 검색 (SELECT BY NAME)
    print("\n[4] 제품 이름으로 검색")
    search_results = manager.select_products_by_name("노")
    for product_id, product_name, product_price in search_results:
        print(f"ID: {product_id}, 제품명: {product_name}, 가격: {product_price}원")
    
    # 5. 제품 정보 수정 (UPDATE)
    print("\n[5] 제품 정보 수정")
    manager.update_product(2, product_name="무선 마우스", product_price=75000)
    manager.display_all_products()
    
    # 6. 제품 삭제 (DELETE)
    print("[6] 제품 삭제")
    manager.delete_product(4)
    manager.display_all_products()
    
    # 7. 최종 조회
    print("[7] 최종 조회")
    all_products = manager.select_all_products()
    print(f"등록된 제품 수: {len(all_products)}개\n")
    
    # 연결 종료
    manager.close()
