from chromaDB import process_all_pdfs_in_directory

if __name__ == "__main__":
    directory_path = "/data/ephemeral/랩큐" # 저장할 PDF폴더 경로로
    collection_name = "pdf_text_collection" # 컬렉션 이름름

    process_all_pdfs_in_directory(directory_path, collection_name)
