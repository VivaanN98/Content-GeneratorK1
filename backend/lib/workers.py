from dataclasses import dataclass


@dataclass
class WorkerDefinition:
    id: int
    name: str
    display_name: str
    prompt: str


WORKERS = [
    WorkerDefinition(
        id=1,
        name="core_learning",
        display_name="Core Learning",
        prompt=(
            "[WORKER_TASK = CORE_LEARNING]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Follow the WORKER 1 template."
        ),
    ),
    WorkerDefinition(
        id=2,
        name="memory",
        display_name="Memory",
        prompt=(
            "[WORKER_TASK = MEMORY]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Follow the WORKER 2 template. "
            "Include exactly 6 flashcards and exactly 6 key terms."
        ),
    ),
    WorkerDefinition(
        id=3,
        name="mcqs",
        display_name="MCQs",
        prompt=(
            "[WORKER_TASK = MCQ]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 4 MCQs per the WORKER 3 template."
        ),
    ),
    WorkerDefinition(
        id=4,
        name="very_short",
        display_name="Very Short Questions",
        prompt=(
            "[WORKER_TASK = VERY_SHORT]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 2 very short Q&A pairs per the WORKER 3 template."
        ),
    ),
    WorkerDefinition(
        id=5,
        name="short_answer",
        display_name="Short Answer Questions",
        prompt=(
            "[WORKER_TASK = SHORT]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 2 short answer Q&A pairs per the WORKER 3 template."
        ),
    ),
    WorkerDefinition(
        id=6,
        name="medium_answer",
        display_name="Medium Answer Questions",
        prompt=(
            "[WORKER_TASK = MEDIUM]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 3 medium answer Q&A pairs per the WORKER 4 template."
        ),
    ),
    WorkerDefinition(
        id=7,
        name="long_answer",
        display_name="Long Answer Questions",
        prompt=(
            "[WORKER_TASK = LONG]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 1 long answer Q&A per the WORKER 4 template."
        ),
    ),
    WorkerDefinition(
        id=8,
        name="assertion_reason",
        display_name="Assertion-Reason",
        prompt=(
            "[WORKER_TASK = ASSERTION]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 3 assertion-reason items per the WORKER 4 template."
        ),
    ),
    WorkerDefinition(
        id=9,
        name="case_studies",
        display_name="Case Studies",
        prompt=(
            "[WORKER_TASK = CASE_STUDY]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 1 case study with exactly 4 sub-questions per the WORKER 4 template."
        ),
    ),
    WorkerDefinition(
        id=10,
        name="tests",
        display_name="Test Generation",
        prompt=(
            "[WORKER_TASK = GENERATE_TESTS]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate exactly 1 complete test per the WORKER 5 template."
        ),
    ),
]
