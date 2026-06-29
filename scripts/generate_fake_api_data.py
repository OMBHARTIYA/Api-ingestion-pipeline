from __future__ import annotations

import logging
from datetime import date, timedelta

import numpy as np
from faker import Faker

from pipeline_utils import ALLOWED_STATUSES, RAW_DIR, ensure_directories, load_config, save_json, setup_logging


def build_projects(fake: Faker, rng: np.random.Generator, count: int) -> list[dict]:
    project_types = ["Residential", "Commercial", "Infrastructure", "Industrial", "Mixed Use"]
    statuses = ["Planned", "Active", "On Hold", "Closing", "Completed"]
    projects = []
    for index in range(1, count + 1):
        start_date = fake.date_between(start_date="-18M", end_date="-6M")
        end_date = start_date + timedelta(days=int(rng.integers(240, 540)))
        projects.append(
            {
                "ProjectID": f"PRJ-{index:03d}",
                "ProjectName": f"{fake.color_name()} {project_types[(index - 1) % len(project_types)]} Initiative",
                "ClientName": f"{fake.company()} Group",
                "Country": fake.country(),
                "City": fake.city(),
                "ProjectType": project_types[(index - 1) % len(project_types)],
                "StartDate": start_date.isoformat(),
                "EndDate": end_date.isoformat(),
                "ProjectStatus": statuses[(index - 1) % len(statuses)],
            }
        )
    return projects


def build_contractors(fake: Faker, count: int) -> list[dict]:
    contractor_types = ["General", "Specialist", "Inspection", "Logistics", "Quality"]
    contractors = []
    for index in range(1, count + 1):
        contractors.append(
            {
                "ContractorID": f"CTR-{index:03d}",
                "ContractorName": f"{fake.company()} Services",
                "ContractorType": contractor_types[(index - 1) % len(contractor_types)],
                "Country": fake.country(),
                "City": fake.city(),
                "ActiveFlag": bool(index % 6 != 0),
            }
        )
    return contractors


def build_work_items(
    fake: Faker,
    rng: np.random.Generator,
    projects: list[dict],
    count: int,
) -> list[dict]:
    categories = ["Structure", "Mechanical", "Electrical", "Interior", "Exterior", "Safety"]
    item_types = ["Task", "Inspection", "Milestone", "Package"]
    units = ["m2", "m3", "ea", "lot", "hr"]
    priorities = ["Low", "Medium", "High", "Critical"]
    statuses = [status_id for status_id, _, _ in ALLOWED_STATUSES]
    work_items = []
    for index in range(1, count + 1):
        project = projects[index % len(projects)]
        project_start = date.fromisoformat(project["StartDate"])
        start_date = fake.date_between(start_date=project_start, end_date="-1M")
        finish_date = start_date + timedelta(days=int(rng.integers(5, 120)))
        work_items.append(
            {
                "WorkItemID": f"WIT-{index:06d}",
                "ProjectID": project["ProjectID"],
                "WorkItemCode": f"{project['ProjectID']}-ITEM-{index:06d}",
                "WorkItemName": f"{fake.bs().title()} Package",
                "WorkItemCategory": categories[index % len(categories)],
                "WorkItemType": item_types[index % len(item_types)],
                "PlannedStartDate": start_date.isoformat(),
                "PlannedFinishDate": finish_date.isoformat(),
                "Quantity": round(float(rng.uniform(1, 500)), 2),
                "UnitOfMeasure": units[index % len(units)],
                "Priority": priorities[index % len(priorities)],
                "CurrentStatusID": statuses[index % len(statuses)],
            }
        )
    return work_items


def build_status_events(
    fake: Faker,
    rng: np.random.Generator,
    projects: list[dict],
    work_items: list[dict],
    contractors: list[dict],
    target_count: int,
    source_system_name: str,
) -> list[dict]:
    progress_path = ["STS-001", "STS-002", "STS-003", "STS-004", "STS-005"]
    exception_statuses = ["STS-006", "STS-007"]
    event_count_per_item = rng.integers(3, 10, size=len(work_items))
    scale_factor = max(target_count / int(event_count_per_item.sum()), 1)
    adjusted_counts = np.maximum(3, np.round(event_count_per_item * scale_factor).astype(int))

    events = []
    event_id = 1
    for item, planned_events in zip(work_items, adjusted_counts):
        project = next(project for project in projects if project["ProjectID"] == item["ProjectID"])
        project_start = np.datetime64(project["StartDate"])
        item_start = np.datetime64(item["PlannedStartDate"])
        cursor = max(project_start, item_start)
        previous_status = None

        for sequence in range(planned_events):
            if sequence == 0:
                status_id = "STS-001"
            else:
                status_pool = progress_path + exception_statuses
                status_id = str(rng.choice(status_pool, p=[0.08, 0.10, 0.32, 0.18, 0.10, 0.12, 0.10]))

            if previous_status in {"STS-004", "STS-005"} and rng.random() < 0.85:
                status_id = previous_status

            days_elapsed = int(rng.integers(1, 12))
            cursor = cursor + np.timedelta64(days_elapsed, "D")
            event_date = str(cursor)[:10]
            hour = int(rng.integers(7, 18))
            minute = int(rng.integers(0, 60))
            second = int(rng.integers(0, 60))
            contractor = contractors[(event_id - 1) % len(contractors)]
            events.append(
                {
                    "StatusEventID": f"EVT-{event_id:07d}",
                    "WorkItemID": item["WorkItemID"],
                    "ProjectID": item["ProjectID"],
                    "StatusID": status_id,
                    "EventDate": event_date,
                    "EventDateTime": f"{event_date}T{hour:02d}:{minute:02d}:{second:02d}",
                    "PreviousStatusID": previous_status,
                    "DaysInPreviousStatus": None if previous_status is None else days_elapsed,
                    "UpdatedBy": contractor["ContractorID"],
                    "SourceSystem": source_system_name,
                    "Comment": fake.sentence(nb_words=10),
                    "IsLatestStatus": False,
                }
            )
            previous_status = status_id
            event_id += 1

        events[-1]["IsLatestStatus"] = True
        item["CurrentStatusID"] = events[-1]["StatusID"]

    return events


def main() -> None:
    setup_logging()
    ensure_directories()
    config = load_config()
    fake = Faker()
    Faker.seed(config["random_seed"])
    rng = np.random.default_rng(config["random_seed"])

    logging.info("Generating synthetic API payloads with seed %s", config["random_seed"])
    projects = build_projects(fake, rng, config["project_count"])
    contractors = build_contractors(fake, config["contractor_count"])
    work_items = build_work_items(fake, rng, projects, config["work_item_count"])
    status_events = build_status_events(
        fake,
        rng,
        projects,
        work_items,
        contractors,
        config["status_event_target_count"],
        config["source_system_name"],
    )

    save_json({"projects": projects}, RAW_DIR / "projects_raw.json")
    save_json({"work_items": work_items}, RAW_DIR / "work_items_raw.json")
    save_json({"status_events": status_events}, RAW_DIR / "status_events_raw.json")
    save_json({"contractors": contractors}, RAW_DIR / "contractors_raw.json")

    logging.info("Generated %s projects", len(projects))
    logging.info("Generated %s contractors", len(contractors))
    logging.info("Generated %s work items", len(work_items))
    logging.info("Generated %s status events", len(status_events))


if __name__ == "__main__":
    main()
