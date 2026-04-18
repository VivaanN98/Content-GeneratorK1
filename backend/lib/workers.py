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
            "Return ONLY valid JSON matching the WORKER 1 schema exactly."
        ),
    ),
    WorkerDefinition(
        id=2,
        name="memory",
        display_name="Memory",
        prompt=(
            "[WORKER_TASK = MEMORY]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON matching the WORKER 2 schema exactly."
        ),
    ),
    WorkerDefinition(
        id=3,
        name="mcqs",
        display_name="MCQs",
        prompt=(
            "[WORKER_TASK = GENERATE_MCQS_25]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'mcqs' — an array of exactly 25 MCQ objects."
        ),
    ),
    WorkerDefinition(
        id=4,
        name="very_short",
        display_name="Very Short Questions",
        prompt=(
            "[WORKER_TASK = GENERATE_VERY_SHORT_25]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'very_short' — an array of exactly 25 very short Q&A objects."
        ),
    ),
    WorkerDefinition(
        id=5,
        name="short_answer",
        display_name="Short Answer Questions",
        prompt=(
            "[WORKER_TASK = GENERATE_SHORT_25]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'short_answer' — an array of exactly 25 short answer Q&A objects."
        ),
    ),
    WorkerDefinition(
        id=6,
        name="medium_answer",
        display_name="Medium Answer Questions",
        prompt=(
            "[WORKER_TASK = GENERATE_MEDIUM_25]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'medium_answer' — an array of exactly 25 medium answer Q&A objects."
        ),
    ),
    WorkerDefinition(
        id=7,
        name="long_answer",
        display_name="Long Answer Questions",
        prompt=(
            "[WORKER_TASK = GENERATE_LONG_20]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'long_answer' — an array of exactly 20 long answer Q&A objects."
        ),
    ),
    WorkerDefinition(
        id=8,
        name="assertion_reason",
        display_name="Assertion-Reason",
        prompt=(
            "[WORKER_TASK = GENERATE_ASSERTION_15]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'assertion_reason' — an array of exactly 15 assertion-reason objects."
        ),
    ),
    WorkerDefinition(
        id=9,
        name="case_studies",
        display_name="Case Studies",
        prompt=(
            "[WORKER_TASK = GENERATE_CASE_10]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'case_studies' — an array of exactly 10 case study objects, each with exactly 4 sub-questions (sub_id: a, b, c, d)."
        ),
    ),
    WorkerDefinition(
        id=10,
        name="tests",
        display_name="Test Generation",
        prompt=(
            "[WORKER_TASK = GENERATE_TESTS]\n"
            "Class {class_num} {subject}, Chapter: {chapter}.\n"
            "Return ONLY valid JSON with key 'tests' — an array of exactly 2 test objects per the WORKER 5 schema."
        ),
    ),
]
