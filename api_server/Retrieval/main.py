from Retrieval.retrieval_module import search_in_chromadb

if __name__ == "__main__":
    # 검색 쿼리 입력
    query = input("검색어를 입력하세요: ")
    collection_name = "pdf_text_collection"  # 저장된 컬렉션 이름
    top_k = 3  # 검색할 최대 결과 개수

    # 검색 수행
    print("\n🔍 검색을 시작합니다...")
    results = search_in_chromadb(query, collection_name, top_k)

    # 결과 출력
    print(f"\n🔎 검색 결과 (Top {top_k}):")
    for i, result in enumerate(results):
        print(f"\n결과 {i + 1}:")
        print(result)

#실행 코드 python -m Retrieval.main