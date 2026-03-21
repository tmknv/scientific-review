from scientific_review.pipelines.baseline import BaselinePipeline

if __name__ == "__main__":
    text = open("example_paper.txt").read()

    pipeline = BaselinePipeline()
    result = pipeline.run(text, paper_id="test_1")

    print(result)