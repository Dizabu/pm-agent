import pytest

from app.task import Task, TaskStore


def make_store(tmp_path) -> TaskStore:
    return TaskStore(tmp_path / "tasks.json")


def test_list_is_empty_when_file_does_not_exist(tmp_path):
    store = make_store(tmp_path)
    assert store.list_tasks() == []


def test_create_task_assigns_increasing_ids(tmp_path):
    store = make_store(tmp_path)
    first = store.create_task("Write README")
    second = store.create_task("Fix login")
    assert first.id == 1
    assert second.id == 2
    assert first.status == "todo"


def test_tasks_persist_in_the_file(tmp_path):
    store = make_store(tmp_path)
    first = store.create_task("Write README")
    store2 = make_store(tmp_path)
    assert store2.list_tasks() == [first]


def test_update_task_status(tmp_path):
    store = make_store(tmp_path)
    first = store.create_task("Write README")
    updated = store.update_task_status(first.id, "done")
    assert updated.status == "done"
    assert store.list_tasks()[0].status == "done"


def test_update_unknown_task_raises(tmp_path):
    store = make_store(tmp_path)
    with pytest.raises(ValueError):
        store.update_task_status(99, "done")


def test_update_with_invalid_status_raises(tmp_path):
    store = make_store(tmp_path)
    task = store.create_task("Write README")
    with pytest.raises(ValueError):
        store.update_task_status(task.id, "invalid_status")


def test_new_id_does_not_reuse_existing_ids(tmp_path):
    store = make_store(tmp_path)
    store._save([Task(id=1, title="Task 1"), Task(id=3, title="Task 3")])
    new_task = store.create_task("Task 4")
    assert new_task.id == 4
