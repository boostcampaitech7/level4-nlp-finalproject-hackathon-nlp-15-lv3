from chromaDB import process_all_pdfs_in_directory

if __name__ == "__main__":
    directory_path = "/data/ephemeral/랩큐"
    collection_name = "pdf_text_collection"

    process_all_pdfs_in_directory(directory_path, collection_name)
