from backend import applications


def test_no_resume_requires_upload(monkeypatch):
    monkeypatch.setattr(applications, 'get_resume_text', lambda: '')
    result = applications.prepare_application({'title': 'Developer Intern', 'company': 'Example'})
    assert result['ready'] is False


def test_application_does_not_fabricate_missing_skills(monkeypatch):
    monkeypatch.setattr(applications, 'get_resume_text', lambda: 'Developed Python applications.')
    result = applications.prepare_application({
        'title': 'Backend Intern', 'company': 'Example',
        'description': 'Experience with Python and Kubernetes required.'
    })
    assert result['ready'] is True
    assert 'Python' in result['matched_skills']
    assert 'Kubernetes' in result['unverified_skills']
    assert 'Kubernetes' not in result['evidence_summary']
    assert 'application_url' in result
