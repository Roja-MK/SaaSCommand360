from pathlib import Path
import subprocess
import re

from prefect import flow, task, get_run_logger


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

PYTHON_EXE = BASE_DIR / "venv" / "Scripts" / "python.exe"
DBT_EXE = BASE_DIR / "venv" / "Scripts" / "dbt.exe"

BACKUP_SCRIPT = BASE_DIR / "scripts" / "export_backup.py"
SILVER_SCRIPT = BASE_DIR / "pyspark" / "transform_silver.py"
DBT_DIR = BASE_DIR / "dbt_gold"


@task(retries=2, retry_delay_seconds=10)
def run_backup():
    logger = get_run_logger()

    result = subprocess.run(
        [str(PYTHON_EXE), str(BACKUP_SCRIPT)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=True
    )

    logger.info(result.stdout)

    match = re.search(r"BACKUP_PATH=(.+)", result.stdout)

    if not match:
        raise ValueError("Backup path was not returned by export_backup.py")

    backup_path = Path(match.group(1).strip())

    logger.info(f"Backup completed: {backup_path}")

    return str(backup_path)


@task(retries=2, retry_delay_seconds=10)
def transform_silver(backup_path: str):
    logger = get_run_logger()

    result = subprocess.run(
        [str(PYTHON_EXE), str(SILVER_SCRIPT), backup_path],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=True
    )

    logger.info(result.stdout)
    logger.info("Silver transformation completed.")


@task(retries=2, retry_delay_seconds=10)
def run_dbt():
    logger = get_run_logger()

    result = subprocess.run(
        [str(DBT_EXE), "run"],
        cwd=DBT_DIR,
        capture_output=True,
        text=True,
        check=True
    )

    logger.info(result.stdout)
    logger.info("dbt models built successfully.")


@task(retries=2, retry_delay_seconds=10)
def test_dbt():
    logger = get_run_logger()

    result = subprocess.run(
        [str(DBT_EXE), "test"],
        cwd=DBT_DIR,
        capture_output=True,
        text=True,
        check=True
    )

    logger.info(result.stdout)
    logger.info("All dbt data tests passed.")


@flow(name="SaaSCommand360-Pipeline")
def saascommand360_pipeline():

    backup_path = run_backup()

    transform_silver(backup_path)

    run_dbt()

    test_dbt()


if __name__ == "__main__":
    saascommand360_pipeline()