from backend import tracking


def test_tracking_persists_status_and_bookmark(tmp_path, monkeypatch):
    monkeypatch.setattr(tracking, 'DB_PATH', tmp_path / 'test_jobs.db')
    tracking.init_tracking()
    job = {'id': '123', 'source': 'TestBoard', 'title': 'Software Intern', 'company': 'Acme'}
    tracking.update_tracking('TestBoard', '123', True, 'Applied', job)
    rows = tracking.list_tracking()
    assert len(rows) == 1
    assert rows[0]['saved'] is True
    assert rows[0]['status'] == 'Applied'
    assert rows[0]['job']['title'] == 'Software Intern'


def test_invalid_status_rejected(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(tracking, 'DB_PATH', tmp_path / 'test_jobs.db')
    tracking.init_tracking()
    with pytest.raises(ValueError):
        tracking.update_tracking('TestBoard', '123', True, 'Made Up', {})
