import csv
import random
from pathlib import Path

SEED = 20261020
STUDENTS = ["Timothy", "Person A", "Person B", "Person C", "Person D", "Person E"]
PAPERS = ["gw_nsbh", "gw_cosmo", "fable_mps", "mars_clouds"]
CONDITIONS = ["human-assisted", "checkpoint"]


def balanced_design(rng):
    while True:
        grid = {}
        for paper in PAPERS:
            assisted = set(rng.sample(STUDENTS, 3))
            for student in STUDENTS:
                grid[student, paper] = CONDITIONS[0] if student in assisted else CONDITIONS[1]
        if all(sum(grid[s, p] == CONDITIONS[0] for p in PAPERS) == 2 for s in STUDENTS):
            return grid


def main():
    rng = random.Random(SEED)
    grid = balanced_design(rng)
    rows = []
    for student in STUDENTS:
        order = rng.sample(PAPERS, len(PAPERS))
        for number, paper in enumerate(order, start=1):
            rows.append([student, number, paper, grid[student, paper], SEED, ""])
    out = Path(__file__).with_name("assignments.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["student", "session_number", "paper_id", "condition", "randomization_seed", "scheduled_date"])
        writer.writerows(rows)


if __name__ == "__main__":
    main()
