import re
from datetime import date

# Change this date to your earliest available internship start.
AVAILABLE_FROM = date(2027, 4, 25)

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
}


def review_eligibility(job):
    text = (job.get('description') or '').lower()
    title = (job.get('title') or '').lower()
    warnings = []

    if 'university co-op program in ontario' in text or re.search(
        r'only considering applicants.{0,120}co-op program in ontario', text
    ):
        warnings.append('Requires enrollment in an Ontario university co-op program; check eligibility.')

    if 'legally eligible to work' in text or 'legally entitled to work' in text:
        warnings.append('Verify work authorization and any full-time work conditions.')

    if 'unpaid' in text or 'stipend: none' in text or 'performance-based stipend' in text:
        warnings.append('Compensation may be unpaid or conditional; verify before applying.')

    # Parse explicit month + year; do not guess from vague seasons or posting dates.
    combined = title + ' ' + text[:550]
    matches = re.findall(
        r'\b(' + '|'.join(MONTHS) + r')\s+(?:\d{1,2}\s*[-–]\s*)?(20\d{2})\b', combined
    )
    for month, year in matches:
        start = date(int(year), MONTHS[month], 1)
        if start < AVAILABLE_FROM:
            warnings.append(f'Possible schedule conflict: {month.title()} {year} start is before {AVAILABLE_FROM.isoformat()}.')
            break

    if not matches and 'winter 2027' in combined and AVAILABLE_FROM > date(2027, 1, 1):
        warnings.append('Possible schedule conflict: Winter 2027 term is before your availability date.')

    return {'eligibility_warnings': warnings, 'eligibility_review_needed': bool(warnings)}
