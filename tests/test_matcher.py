from backend import matcher


def test_skill_boundaries_avoid_Java_inside_JavaScript():
    assert matcher.extract_skills('JavaScript React') == ['JavaScript', 'React']


def test_matching_returns_sorted_results(monkeypatch):
    monkeypatch.setattr(matcher, 'get_resume_text', lambda: '')
    jobs = [
        {'title': 'Intern A', 'description': 'Kubernetes and PostgreSQL'},
        {'title': 'Intern B', 'description': 'Python and Docker'},
    ]
    result = matcher.rank_jobs(jobs)
    assert result[0]['title'] == 'Intern B'
    assert result[0]['match_score'] is not None
    assert result[0]['match_score'] >= (result[1]['match_score'] or 0)


def test_empty_job_list():
    assert matcher.rank_jobs([]) == []
