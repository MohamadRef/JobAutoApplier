import { useEffect, useState } from "react";
import {
  BriefcaseBusiness,
  Search,
  MapPin,
  ExternalLink,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [jobs, setJobs] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [location, setLocation] = useState("Canada");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiErrors, setApiErrors] = useState([]);

  async function fetchJobs(search = keyword, place = location) {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams({
        keyword: search,
        location: place,
      });

      const response = await fetch(
        `${API_URL}/jobs/matched?${params}`
      );

      if (!response.ok) {
        throw new Error("Unable to fetch internships");
      }

      const data = await response.json();

      setJobs(data.jobs || []);
      setApiErrors(data.errors || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchJobs("", "Canada");
  }, []);

  const scoredJobs = jobs.filter(
    (job) => job.match_score !== null
  );

  const averageMatch = scoredJobs.length
    ? Math.round(
        scoredJobs.reduce(
          (sum, job) => sum + job.match_score,
          0
        ) / scoredJobs.length
      )
    : 0;

  function handleSearch(event) {
    event.preventDefault();
    fetchJobs();
  }

  function formatLocation(value) {
    return Array.isArray(value)
      ? value.join(", ")
      : value || "Not specified";
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <BriefcaseBusiness size={22} />
          </div>
          <span>JobAutoApplier</span>
        </div>

        <div className="navigation">
          <div className="nav-item active">
            <BriefcaseBusiness size={18} />
            Discover Jobs
          </div>
        </div>

        <div className="sidebar-footer">
          <span className="status-dot" />
          Backend connection required
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <p className="eyebrow">YOUR INTERNSHIP SEARCH</p>
            <h1>Discover Opportunities</h1>
            <p className="subtitle">
              Find software engineering internships matched
              to your skills.
            </p>
          </div>

          <button
            className="refresh-btn"
            onClick={() => fetchJobs()}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </header>

        <section className="stats">
          <div className="stat-card">
            <p>Internships Found</p>
            <h2>{jobs.length}</h2>
            <span>Matching your search</span>
          </div>

          <div className="stat-card">
            <p>Average Skill Match</p>
            <h2>
              {scoredJobs.length ? `${averageMatch}%` : "N/A"}
            </h2>
            <span>Based on detected skills</span>
          </div>

          <div className="stat-card">
            <p>High Matches</p>
            <h2>
              {jobs.filter(
                (job) => job.match_score >= 80
              ).length}
            </h2>
            <span>80% skill overlap or higher</span>
          </div>
        </section>

        <section className="search-section">
          <form onSubmit={handleSearch} className="search-bar">
            <div className="input-group">
              <Search size={18} />

              <input
                placeholder="Search internships..."
                value={keyword}
                onChange={(event) =>
                  setKeyword(event.target.value)
                }
              />
            </div>

            <div className="input-group location-input">
              <MapPin size={18} />

              <input
                placeholder="Location"
                value={location}
                onChange={(event) =>
                  setLocation(event.target.value)
                }
              />
            </div>

            <button type="submit" disabled={loading}>
              Search Jobs
            </button>
          </form>
        </section>

        <div className="section-heading">
          <div>
            <h2>Available Internships</h2>
            <p>Sorted by skill compatibility</p>
          </div>
          <span className="result-count">
            {jobs.length} results
          </span>
        </div>

        {loading && (
          <div className="message">
            Searching for internships...
          </div>
        )}

        {error && (
          <div className="message error">
            <AlertCircle size={18} />
            {error}. Make sure your Python backend is running.
          </div>
        )}

        {apiErrors.length > 0 && (
          <div className="message error">
            Some job sources failed: {apiErrors.join("; ")}
          </div>
        )}

        {!loading && !error && jobs.length === 0 && (
          <div className="message">
            No internships found. Try another keyword.
          </div>
        )}

        {!loading && !error && (
          <div className="job-list">
            {jobs.map((job) => (
              <article
                className="job-card"
                key={`${job.source}-${job.id}`}
              >
                <div className="job-top">
                  <div>
                    <span className="company">
                      {job.company}
                    </span>

                    <h3>{job.title}</h3>

                    <div className="job-meta">
                      <span>
                        <MapPin size={14} />
                        {formatLocation(job.location)}
                      </span>

                      <span>{job.source}</span>
                    </div>
                  </div>

                  <div className="match-score">
                    <strong>
                      {job.match_score === null
                        ? "N/A"
                        : `${job.match_score}%`}
                    </strong>
                    <span>Skill Match</span>
                  </div>
                </div>

                <div className="skills">
                  {job.matched_skills?.map((skill) => (
                    <span className="skill matched" key={skill}>
                      <CheckCircle2 size={13} />
                      {skill}
                    </span>
                  ))}

                  {job.missing_skills?.map((skill) => (
                    <span className="skill missing" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>

                <div className="job-bottom">
                  <span>
                    {job.detected_job_skills?.length || 0}
                    {" "}technologies detected
                  </span>

                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="apply-btn"
                  >
                    View Job
                    <ExternalLink size={15} />
                  </a>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;