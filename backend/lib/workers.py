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
            "Output Markdown only. Follow the WORKER 2 template exactly."
        ),
    ),
    WorkerDefinition(
        id=3,
        name="mcqs",
        display_name="MCQs",
        prompt=(
            "[WORKER_TASK = MCQ]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Follow the WORKER 3 template exactly."
        ),
    ),
    WorkerDefinition(
        id=4,
        name="very_short",
        display_name="Very Short Questions",
        prompt=(
            "[WORKER_TASK = VERY_SHORT]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 4 Batch 1 exactly as specified: Very Short Answer."
        ),
    ),
    WorkerDefinition(
        id=5,
        name="short_answer",
        display_name="Short Answer Questions",
        prompt=(
            "[WORKER_TASK = SHORT]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 4 Batch 2 exactly as specified: Short Answer."
        ),
    ),
    WorkerDefinition(
        id=6,
        name="medium_answer",
        display_name="Medium Answer Questions",
        prompt=(
            "[WORKER_TASK = MEDIUM]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 5 Batch 1 exactly as specified: Medium Answer."
        ),
    ),
    WorkerDefinition(
        id=7,
        name="long_answer",
        display_name="Long Answer Questions",
        prompt=(
            "[WORKER_TASK = LONG]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 5 Batch 2 exactly as specified: Long Answer."
        ),
    ),
    WorkerDefinition(
        id=8,
        name="assertion_reason",
        display_name="Assertion-Reason",
        prompt=(
            "[WORKER_TASK = ASSERTION]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 5 Batch 3 exactly as specified: Assertion-Reason."
        ),
    ),
    WorkerDefinition(
        id=9,
        name="case_studies",
        display_name="Case Studies",
        prompt=(
            "[WORKER_TASK = CASE_STUDY]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 6 Batch 1 and Batch 2 exactly as specified: Case Studies 1-10."
        ),
    ),
    WorkerDefinition(
        id=10,
        name="tests",
        display_name="Test Generation",
        prompt=(
            "[WORKER_TASK = GENERATE_TESTS]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Output Markdown only. Generate Worker 6 Batch 3 exactly as specified: Test 1, Test 2, and Exam Strategy."
        ),
    ),
]
