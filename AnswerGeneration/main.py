import numpy as np
import spacy

nlp = spacy.load('en_core_web_md')


def generate_answer(question):
    question_vector = text_to_vector(question)
    similar_index = find_similar_index(question_vector, text_question_vectors)
    return text_answers[int(similar_index)]


def text_to_vector(text):
    return nlp(' '.join([
        token.lemma_.lower() if not token.ent_type_ else token.ent_type_
        for token in nlp(text)
        if not token.text.isspace()
    ])), nlp(' '.join([
        token.lemma_.lower() if not token.ent_type_ else token.ent_type_
        for token in nlp(text)
        if not token.text.isspace() and not token.is_stop and len(token.text) > 1
    ]))


def find_similar_index(test_vector, vectors):
    similarities_overall = [test_vector[0].similarity(vector[0]) for vector in vectors]

    if test_vector[1].vector_norm:
        similarities_meaning = [test_vector[1].similarity(vector[1]) if vector[1].vector_norm else 0 for vector in vectors]
    else:
        similarities_meaning = 0

    similarities = similarities_overall + np.array(similarities_meaning) * 0.5
    return np.argmax(similarities)


with open('../data/QA.txt', 'r') as f:
    text_raw = f.read()

text_raw_lines = text_raw.splitlines()

text_question_vectors = [text_to_vector(text) for text in text_raw_lines[0::3]]
text_answers = text_raw_lines[1::3]

if __name__ == '__main__':
    while 1:
        question = input("Q: ")
        answer = generate_answer(question)
        print("A:", answer)
