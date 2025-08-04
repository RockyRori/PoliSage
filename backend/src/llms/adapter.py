from backend.src.llms.llm_tongyiqianwen import qwen_plus_query


def generate_answer(question, reference, model="default", language="Chinese") -> str:
    prompt = generate_prompt(language, question, reference)
    if model:
        return qwen_plus_query(prompt)
    # return "question_text :" + question_text + "\n" + "reference :" + "\n".join(reference)


def generate_prompt(language: str, question_text: str, reference_text: str) -> str:
    if language == "Chinese":
        result = f"""
规则:
你是一个乐于助人的助手。
根据提供的参考资料回答以下问题。如果你认为这个问题与参考文献无关，请回答“材料中的知识无法解答这个问题”。
在你的回答中，请在方括号中加上与参考文献相对应的标注编号。

回答示例: 
孙膑 『1』 是中国战国时期齐国军事家 『2』 ，代表作为孙子兵法 『3』。
问题:
{question_text}

参考资料:
{reference_text}
"""
    else:
        result = f"""
Rules:
You are a helpful assistant.
Answer the following question based on the provided references. If you think the question is not related to the references, please answer "Answer cannot be found in documents.".
In your answer, please include citation numbers in square brackets corresponding to the references.

Example Answer Format: 
Students are responsible for notifying 『1』 the University of any changes to their personal details after registration. For changes like name, HKID Card 『2』 or Passport information, legal documentary evidence is required 『3』.

Questions:
{question_text}

References:
{reference_text}
"""
    return result


if __name__ == "__main__":
    # 示例输入：组装后的完整用户问题
    question = ("Based on your previous inquiries: What are the famous potato chip brands?; "
                "I want you to recommend some delicious snack. And your current question: "
                "Which brand is tasty?")

    # 示例参考文献列表
    references = []
    references.append({
        'content': "Coco is the best chips with a crunchy texture and rich flavor.",
        'source': "doc1.txt",
        'similarity': "89%"
    })
    references.append({
        'content': "Violet offers chips that are also popular and known for their quality.",
        'source': "doc2.txt",
        'similarity': "76%"
    })

    answer = generate_answer(question, references)

    print("LLM Answer with citations:")
    print(answer)
