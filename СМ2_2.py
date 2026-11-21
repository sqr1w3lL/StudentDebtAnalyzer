from functools import reduce
from collections import defaultdict


PASS_SCORE = 60
MIN_DEBTS = 2


class Student:
    def __init__(self, surname, name, patronymic, group, specialty,
                 subject, teacher, date, score):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.group = group
        self.specialty = specialty
        self.subject = subject
        self.teacher = teacher
        self.date = date
        self.score = int(score)

    @classmethod
    def from_line(cls, line: str) -> "Student":
        return cls(*line.strip().split())

    @property
    def identity_key(self) -> tuple:
        return (self.surname, self.name, self.patronymic, self.group)

    def is_failed(self) -> bool:
        return self.score < PASS_SCORE


class StudentRecord:
    def __init__(self):
        self.debts: int = 0
        self.failed_scores: list[int] = []

    def add_failed(self, score: int) -> None:
        self.debts += 1
        self.failed_scores.append(score)

    @property
    def average_score(self) -> float:
        return (
            round(sum(self.failed_scores) / len(self.failed_scores), 1)
            if self.failed_scores else 0.0
        )

    def has_too_many_debts(self) -> bool:
        return self.debts > MIN_DEBTS


def load_students(filename: str) -> list[Student]:
    with open(filename, encoding="utf-8") as f:
        return list(map(Student.from_line, f))


def _accumulate_debts(acc: defaultdict, student: Student) -> defaultdict:
    if student.is_failed():
        acc[student.identity_key].add_failed(student.score)
    return acc


def build_debt_records(students: list[Student]) -> defaultdict:
    return reduce(
        _accumulate_debts,
        students,
        defaultdict(StudentRecord)
    )


def filter_debtors(records: defaultdict) -> list[dict]:
    return list(
        map(
            lambda item: {
                "student": item[0],
                "group": item[0][3],
                "debts": item[1].debts,
                "avg": item[1].average_score,
            },
            filter(lambda x: x[1].has_too_many_debts(), records.items())
        )
    )


def _merge(left: list, right: list, key) -> list:
    if not left:
        return right
    if not right:
        return left
    if key(left[0]) <= key(right[0]):
        return [left[0]] + _merge(left[1:], right, key)
    return [right[0]] + _merge(left, right[1:], key)


def merge_sort(lst: list, key) -> list:
    if len(lst) <= 1:
        return lst
    mid = len(lst) // 2
    return _merge(
        merge_sort(lst[:mid], key),
        merge_sort(lst[mid:], key),
        key
    )


def sort_debtors(debtors: list[dict]) -> list[dict]:
    return merge_sort(
        debtors,
        key=lambda x: (-x["debts"], x["avg"], x["group"])
    )


def print_results(debtors: list[dict]) -> None:
    list(map(
        lambda r: print(r["student"], r["debts"], r["avg"]),
        debtors
    ))


class StudentDebtAnalyzer:
    def __init__(self, filename: str):
        self.filename = filename
        self._students: list[Student] = []
        self._records: defaultdict = defaultdict(StudentRecord)
        self._debtors: list[dict] = []

    def load(self) -> "StudentDebtAnalyzer":
        self._students = load_students(self.filename)
        return self

    def analyze(self) -> "StudentDebtAnalyzer":
        self._records = build_debt_records(self._students)
        return self

    def filter_and_sort(self) -> "StudentDebtAnalyzer":
        self._debtors = sort_debtors(filter_debtors(self._records))
        return self

    def report(self) -> None:
        print_results(self._debtors)

    def run(self) -> None:
        self.load().analyze().filter_and_sort().report()


if __name__ == "__main__":
    StudentDebtAnalyzer("students.txt").run()
