import json
import sys

from scientific_review.pipelines.baseline import BaselinePipeline


def main():
    path = sys.argv[1]
    paper_id = sys.argv[2] if len(sys.argv) > 2 else "test_1"

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    pipeline = BaselinePipeline()
    result = pipeline.run(text, paper_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    pipeline.close()


if __name__ == "__main__":
    main()
