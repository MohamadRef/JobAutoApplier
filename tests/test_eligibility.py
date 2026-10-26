from backend.eligibility import review_eligibility


def test_ontario_restriction_is_flagged():
    result = review_eligibility({
        'title': 'Software Developer Co-op',
        'description': 'We only consider students in a university co-op program in Ontario.'
    })
    assert result['eligibility_review_needed']
    assert any('Ontario' in warning for warning in result['eligibility_warnings'])


def test_early_start_is_flagged():
    result = review_eligibility({
        'title': 'Software Engineer Intern May 2026',
        'description': 'Remote role'
    })
    assert any('schedule conflict' in warning.lower() for warning in result['eligibility_warnings'])


def test_no_claim_of_automatic_eligibility():
    result = review_eligibility({'title': 'Software Intern', 'description': 'Python and REST APIs'})
    assert result['eligibility_warnings'] == []
    assert result['eligibility_review_needed'] is False
