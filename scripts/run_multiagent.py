from scientific_review.pipelines.multiagent import MultiAgentPipeline

if __name__ == "__main__":
    text = open("example_paper.txt").read()

    pipeline = MultiAgentPipeline()
    result = pipeline.run(text)

    print(result)