from app.api.dependencies import get_answer_generator

generator = get_answer_generator()

print(type(generator).__name__)