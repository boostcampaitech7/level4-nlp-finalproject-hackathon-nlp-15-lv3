import argparse

import requests


def main(args: argparse.Namespace) -> None:
    print("### Indexing Test ###")
    data = {
        "id": "test",
        "name": "test",
        "group_id": "test",
        "documents": [
            {
                "id": "test",
                "text": "test",
                "metadata": {},
                "score": 0.0
            }
        ],
        "max_chunk_size": 1024,
        "num_chunk_overlap": 256
    }
    with requests.post(f"{args.api_address}/indexing", json=data) as req:
        print(req.json())

    print("### Retrieval Test ###")
    data = {
        "id": "test",
        "name": "test",
        "group_id": "test",
        "query": "test",
        "max_query_size": 1024,
        "top_k": 3
    }

    with requests.post(f"{args.api_address}/retrieve", json=data) as req:
        print(req.json())

    print("### Chat Test ###")
    data = {
        "id": "test",
        "name": "test",
        "group_id": "test",
        "messages": [
            {
                "role": "user",
                "content": "test"
            }
        ],
        "max_query_size": 1024,
        "top_k": 3
    }

    with requests.post(f"{args.api_address}/chat", json=data) as req:
        print(req.json())

    print("### Chat Stream Test ###")
    data["stream"] = True
    with requests.post(f"{args.api_address}/chat", json=data, stream=True) as req:
        for line in req:
            print(line.decode("utf-8"), end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_address", type=str, default="http://0.0.0.0:8000")
    args = parser.parse_args()
    main(args)
