import { useEffect, useMemo, useRef, useState } from "react";
import {
  BriefcaseBusiness,
  Bookmark,
  BookmarkCheck,
  Search,
  MapPin,
  ExternalLink,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Upload,
  FileText,
  Compass,
  Target,
  TrendingUp,
  Layers,
  ChevronDown,
  X,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

/* ---------- helpers ---------- */

function tierOf(score) {
  if (score == null) return "none";
  if (score >= 80) return "high";
  if (score >= 50) return "mid";
  return "low";
}

function tierLabel(score) {
  const t = tierOf(score);
  return { high: "Strong match", mid: "Decent match", low: "Weak match", none: "Not scored" }[t];
}

// Stable hue per company so each logo tile gets its own colour
function hueFor(text = "") {
  let h = 0;
  for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) % 360;
  return h;
}

function initials(name = "?") {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

function formatLocation(value) {
  return Array.isArray(value) ? value.join(", ") : value || "Location not listed";
}

/* ---------- small components ---------- */

function ScoreRing({ score }) {
  const size = 76;
  const stroke = 7;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = score == null ? 0 : Math.min(score, 100);

  return (
    <div className={`ring ${tierOf(score)}`} aria-label={`${tierLabel(score)}: ${score ?? "no"} percent`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle className="ring-track" cx={size / 2} cy={size / 2} r={r} strokeWidth={stroke} fill="none" />
        <circle
          className="ring-fill"
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={circ - (pct / 100) * circ}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="ring-label">
        <strong>{score == null ? "–" : score}</strong>
        {score != null && <small>%</small>}
      </div>
    </div>
  );
}

function Stat({ icon: Icon, label, value, hint, tone }) {
  return (
    <div className={`stat ${tone || ""}`}>
      <div className="stat-icon">
        <Icon size={19} />
      </div>
      <div>
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
        <p className="stat-hint">{hint}</p>
      </div>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="job-card skeleton" aria-hidden>
      <div className="sk sk-logo" />
      <div className="sk-lines">
        <div className="sk sk-line w30" />
        <div className="sk sk-line w60 tall" />
        <div className="sk sk-line w40" />
        <div className="sk-row">
          <div className="sk sk-chip" />
          <div className="sk sk-chip" />
          <div className="sk sk-chip" />
        </div>
      </div>
      <div className="sk sk-circle" />
    </div>
  );
}

function JobCard({ job, saved, status, onToggleSave, onStatusChange, onPrepare }) {
  const [open, setOpen] = useState(false);
  const matched = job.matched_skills || [];
  const missing = job.missing_skills || [];
  const LIMIT = 6;
  const hasMore = matched.length + missing.length > LIMIT;
  const shownMatched = open ? matched : matched.slice(0, LIMIT);
  const shownMissing = open ? missing : missing.slice(0, Math.max(0, LIMIT - shownMatched.length));
  const hue = hueFor(job.company);

  return (
    <article className={`job-card tier-${tierOf(job.match_score)}`}>
      <div
        className="logo"
        style={{
          background: `hsl(${hue} 70% 94%)`,
          color: `hsl(${hue} 55% 32%)`,
          borderColor: `hsl(${hue} 50% 86%)`,
        }}
      >
        {initials(job.company)}
      </div>

      <div className="job-body">
        <div className="job-head">
          <span className="company">{job.company}</span>
          <span className="source-pill">{job.source}</span>
        </div>

        <h3>{job.title}</h3>

        <div className="job-meta">
          <span>
            <MapPin size={14} />
            {formatLocation(job.location)}
          </span>
          <span>
            <Layers size={14} />
            {job.detected_job_skills?.length || 0} technologies detected
          </span>
        </div>

        {(matched.length > 0 || missing.length > 0) && (
          <div className="skills">
            {shownMatched.map((skill) => (
              <span className="skill matched" key={`m-${skill}`}>
                <CheckCircle2 size={13} />
                {skill}
              </span>
            ))}
            {shownMissing.map((skill) => (
              <span className="skill missing" key={`x-${skill}`} title="Not found on your resume">
                {skill}
              </span>
            ))}
            {hasMore && (
              <button className="skill-toggle" onClick={() => setOpen(!open)}>
                {open ? "Show less" : `+${matched.length + missing.length - LIMIT} more`}
                <ChevronDown size={13} className={open ? "flip" : ""} />
              </button>
            )}
          </div>
        )}

        {job.eligibility_warnings?.length > 0 && (
          <div className="eligibility-warnings">
            <AlertCircle size={16} />
            <div>{job.eligibility_warnings.map((warning, i) => <p key={i}>{warning}</p>)}</div>
          </div>
        )}
        <div className="job-actions">
          <a href={job.url} target="_blank" rel="noopener noreferrer" className="apply-btn">
            View job
            <ExternalLink size={15} />
          </a>
          <button className="save-btn" onClick={onPrepare}>Prepare application</button>
          <select
            className="application-select"
            aria-label={`Application status for ${job.title}`}
            value={status}
            onChange={(e) => onStatusChange(e.target.value)}
          >
            {['Not Applied', 'Applied', 'Interviewing', 'Offer', 'Rejected'].map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
          <button
            className={`save-btn ${saved ? "saved" : ""}`}
            onClick={onToggleSave}
            aria-pressed={saved}
          >
            {saved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
            {saved ? "Saved" : "Save"}
          </button>
        </div>
      </div>

      <aside className="job-score">
        <ScoreRing score={job.match_score} />
        <span className={`tier-label ${tierOf(job.match_score)}`}>{tierLabel(job.match_score)}</span>
        <div className="score-breakdown">
          {job.skill_score != null && (
            <div>
              <span>Skills</span>
              <b>{job.skill_score}%</b>
            </div>
          )}
          {job.similarity_score != null && (
            <div>
              <span>TF-IDF</span>
              <b>{job.similarity_score}%</b>
            </div>
          )}
        </div>
        {job.match_method && <span className="method">{job.match_method}</span>}
      </aside>
    </article>
  );
}

/* ---------- app ---------- */

function App() {
  const [jobs, setJobs] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [location, setLocation] = useState("Canada");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [resumeUploaded, setResumeUploaded] = useState(false);
  const [resumeName, setResumeName] = useState("");
  const [backendOnline, setBackendOnline] = useState(false);
  const [error, setError] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [apiErrors, setApiErrors] = useState([]);

  const [view, setView] = useState("discover");
  const [sort, setSort] = useState("match");
  const [minMatch, setMinMatch] = useState(0);
  const [sourceFilter, setSourceFilter] = useState("all");
  const [tracked, setTracked] = useState({});
  const [applicationPreview, setApplicationPreview] = useState(null);
  const [previewError, setPreviewError] = useState("");
  const [preparing, setPreparing] = useState(false);

  const fileInput = useRef(null);

  async function fetchJobs(search = "", place = "Canada") {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ keyword: search, location: place });
      const response = await fetch(`${API_URL}/jobs/matched?${params}`);
      if (!response.ok) throw new Error("Unable to fetch internships");
      const data = await response.json();
      setJobs(data.jobs || []);
      setApiErrors(data.errors || []);
      setBackendOnline(true);
    } catch (err) {
      setError(err.message);
      setBackendOnline(false);
    } finally {
      setLoading(false);
    }
  }

  async function checkResume() {
    try {
      const response = await fetch(`${API_URL}/resume/status`);
      if (!response.ok) return;
      const data = await response.json();
      setResumeUploaded(data.uploaded);
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  }

  async function fetchTracking() {
    try {
      const response = await fetch(`${API_URL}/tracking`);
      if (!response.ok) throw new Error('Cannot load tracked jobs');
      const data = await response.json();
      const next = {};
      for (const row of data.items || []) {
        next[`${row.source}-${row.job_id}`] = row;
      }
      setTracked(next);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    fetchJobs();
    checkResume();
    fetchTracking();
  }, []);

  async function uploadResume(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadMessage("Please select a PDF resume.");
      return;
    }

    setUploading(true);
    setUploadMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/resume/upload`, { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === "string" ? data.detail : "Resume upload failed");
      }
      setResumeUploaded(true);
      setResumeName(file.name);
      setUploadMessage("Resume uploaded successfully.");
      await fetchJobs(keyword, location);
    } catch (err) {
      setUploadMessage(err.message);
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  function handleSearch(event) {
    event.preventDefault();
    fetchJobs(keyword, location);
  }

  async function prepareJob(job) {
    setPreparing(true);
    setPreviewError("");
    setApplicationPreview(null);
    try {
      const response = await fetch(`${API_URL}/applications/prepare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job }),
      });
      if (!response.ok) throw new Error("Could not prepare application");
      setApplicationPreview(await response.json());
    } catch (err) {
      setPreviewError(err.message);
    } finally {
      setPreparing(false);
    }
  }

  const keyOf = (job) => `${job.source}-${job.id}`;

  async function changeTracking(job, change) {
    const key = keyOf(job);
    const previous = tracked[key];
    const updated = {
      source: job.source,
      job_id: String(job.id),
      saved: previous?.saved ?? false,
      status: previous?.status ?? 'Not Applied',
      job: { ...previous?.job, ...job },
      ...change,
    };

    // Only update UI when the database confirms it was saved.
    try {
      const response = await fetch(`${API_URL}/tracking`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated),
      });
      if (!response.ok) throw new Error('Could not save application state');
      setTracked((current) => ({
        ...current,
        [key]: { ...updated, job_id: updated.job_id },
      }));
    } catch (err) {
      setError(err.message);
    }
  }

  const sources = useMemo(() => [...new Set(jobs.map((j) => j.source).filter(Boolean))], [jobs]);

  const visibleJobs = useMemo(() => {
    const archived = Object.values(tracked)
      .filter((entry) => entry.saved && entry.job)
      .map((entry) => entry.job);
    let list = view === "saved" ? archived : jobs;
    if (minMatch > 0) list = list.filter((j) => (j.match_score ?? -1) >= minMatch);
    if (sourceFilter !== "all") list = list.filter((j) => j.source === sourceFilter);

    const sorted = [...list];
    if (sort === "match") sorted.sort((a, b) => (b.match_score ?? -1) - (a.match_score ?? -1));
    if (sort === "company") sorted.sort((a, b) => (a.company || "").localeCompare(b.company || ""));
    return sorted;
  }, [jobs, view, tracked, minMatch, sourceFilter, sort]);

  const savedCount = Object.values(tracked).filter((row) => row.saved).length;
  const scoredJobs = jobs.filter((j) => j.match_score != null);
  const averageMatch = scoredJobs.length
    ? Math.round(scoredJobs.reduce((s, j) => s + j.match_score, 0) / scoredJobs.length)
    : null;
  const highMatches = jobs.filter((j) => j.match_score >= 80).length;
  const filtersActive = minMatch > 0 || sourceFilter !== "all";

  return (
    <div className="app">
      {/* ---------- sidebar ---------- */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <BriefcaseBusiness size={20} />
          </div>
          <span>JobAutoApplier</span>
        </div>

        <nav className="navigation">
          <button
            className={`nav-item ${view === "discover" ? "active" : ""}`}
            onClick={() => setView("discover")}
          >
            <Compass size={18} />
            Discover jobs
          </button>
          <button
            className={`nav-item ${view === "saved" ? "active" : ""}`}
            onClick={() => setView("saved")}
          >
            <Bookmark size={18} />
            Saved
            {savedCount > 0 && <span className="nav-count">{savedCount}</span>}
          </button>
        </nav>

        <div className="sidebar-resume">
          <div className="sr-head">
            <FileText size={16} />
            <span>Resume</span>
          </div>
          <p>
            {resumeUploaded
              ? resumeName || "Uploaded and ready for matching"
              : "Add a PDF to see match scores"}
          </p>
          <button onClick={() => fileInput.current?.click()} disabled={uploading}>
            <Upload size={14} />
            {uploading ? "Uploading…" : resumeUploaded ? "Replace" : "Upload"}
          </button>
        </div>

        <div className="sidebar-footer">
          <span className={`status-dot ${backendOnline ? "on" : "off"}`} />
          {backendOnline ? "Backend connected" : "Backend disconnected"}
        </div>
      </aside>

      {/* ---------- main ---------- */}
      <main className="main">
        <header className="header">
          <div>
            <h1>{view === "saved" ? "Saved internships" : "Find your next internship"}</h1>
            <p className="subtitle">
              {view === "saved"
                ? "Roles you bookmarked while browsing."
                : "Every posting is scored against your resume, so the best fits rise to the top."}
            </p>
          </div>
          <button className="refresh-btn" onClick={() => fetchJobs(keyword, location)} disabled={loading}>
            <RefreshCw size={16} className={loading ? "spin" : ""} />
            Refresh
          </button>
        </header>

        <input
          type="file"
          accept=".pdf,application/pdf"
          ref={fileInput}
          onChange={uploadResume}
          style={{ display: "none" }}
        />

        {/* resume banner */}
        <section className={`resume-section ${resumeUploaded ? "ready" : ""}`}>
          <div className="resume-icon">
            <FileText size={24} />
          </div>
          <div className="resume-text">
            <h3>{resumeUploaded ? "Resume matching is on" : "Upload your resume to get match scores"}</h3>
            <p>
              {uploadMessage ||
                (resumeUploaded
                  ? "We compare your skills and wording against each posting using TF-IDF similarity."
                  : "PDF only. We pull out your skills and rank every internship against them.")}
            </p>
          </div>
          <button
            className="resume-upload-btn"
            onClick={() => fileInput.current?.click()}
            disabled={uploading}
          >
            <Upload size={16} />
            {uploading ? "Uploading…" : resumeUploaded ? "Replace resume" : "Upload resume"}
          </button>
        </section>

        {/* stats */}
        <section className="stats">
          <Stat icon={Layers} label="Internships found" value={jobs.length} hint="Matching your search" />
          <Stat
            icon={TrendingUp}
            label="Average match"
            value={averageMatch === null ? "N/A" : `${averageMatch}%`}
            hint="Estimated resume fit"
            tone="blue"
          />
          <Stat icon={Target} label="High matches" value={highMatches} hint="80% or higher" tone="green" />
        </section>

        {/* search */}
        <form onSubmit={handleSearch} className="search-bar">
          <div className="input-group">
            <Search size={18} />
            <input
              placeholder="Search by role, company or skill"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
            {keyword && (
              <button type="button" className="clear" onClick={() => setKeyword("")} aria-label="Clear search">
                <X size={15} />
              </button>
            )}
          </div>
          <div className="input-group location-input">
            <MapPin size={18} />
            <input placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
          <button type="submit" className="search-btn" disabled={loading}>
            Search jobs
          </button>
        </form>

        {/* toolbar */}
        <div className="toolbar">
          <div className="filter-group" role="group" aria-label="Minimum match">
            {[
              [0, "All"],
              [50, "50%+"],
              [80, "80%+"],
            ].map(([val, label]) => (
              <button
                key={val}
                className={`seg ${minMatch === val ? "on" : ""}`}
                onClick={() => setMinMatch(val)}
              >
                {label}
              </button>
            ))}
          </div>

          {sources.length > 1 && (
            <select
              className="select"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              aria-label="Filter by source"
            >
              <option value="all">All sources</option>
              {sources.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          )}

          <select className="select" value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort by">
            <option value="match">Best match first</option>
            <option value="company">Company A–Z</option>
          </select>

          <span className="result-count">
            {visibleJobs.length} {visibleJobs.length === 1 ? "result" : "results"}
          </span>
        </div>

        {/* messages */}
        {error && (
          <div className="message error">
            <AlertCircle size={18} />
            <span>{error}. Check that your Python backend is running.</span>
          </div>
        )}
        {apiErrors.length > 0 && (
          <div className="message warn">
            <AlertCircle size={18} />
            <span>Some job sources failed: {apiErrors.join("; ")}</span>
          </div>
        )}

        {/* list */}
        {loading && (
          <div className="job-list">
            {[0, 1, 2].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {!loading && !error && visibleJobs.length === 0 && (
          <div className="empty">
            <div className="empty-icon">{view === "saved" ? <Bookmark size={26} /> : <Search size={26} />}</div>
            <h3>{view === "saved" ? "Nothing saved yet" : "No internships found"}</h3>
            <p>
              {view === "saved"
                ? "Tap Save on any posting and it will show up here."
                : filtersActive
                ? "Your filters are hiding every result. Loosen them to see more."
                : "Try a broader keyword or a different location."}
            </p>
            {filtersActive && (
              <button
                className="empty-btn"
                onClick={() => {
                  setMinMatch(0);
                  setSourceFilter("all");
                }}
              >
                Clear filters
              </button>
            )}
          </div>
        )}

        {!loading && !error && visibleJobs.length > 0 && (
          <div className="job-list">
            {visibleJobs.map((job) => (
              <JobCard
                key={keyOf(job)}
                job={job}
                saved={Boolean(tracked[keyOf(job)]?.saved)}
                status={tracked[keyOf(job)]?.status || 'Not Applied'}
                onToggleSave={() => changeTracking(job, { saved: !tracked[keyOf(job)]?.saved })}
                onStatusChange={(status) => changeTracking(job, { status })}
                onPrepare={() => prepareJob(job)}
              />
            ))}
          </div>
        )}
      </main>
      {(applicationPreview || previewError || preparing) && (
        <div className="preview-backdrop" onClick={() => { setApplicationPreview(null); setPreviewError(""); }}>
          <section className="preview-dialog" role="dialog" aria-modal="true" aria-label="Application preparation" onClick={(e) => e.stopPropagation()}>
            <button className="preview-close" onClick={() => { setApplicationPreview(null); setPreviewError(""); }}>Close</button>
            {preparing && <p>Preparing application...</p>}
            {previewError && <p role="alert">{previewError}</p>}
            {applicationPreview && (
              <>
                <h2>{applicationPreview.title}</h2>
                <p>{applicationPreview.company}</p>
                {!applicationPreview.ready ? (
                  <p>{applicationPreview.message}</p>
                ) : (
                  <>
                    <h3>Resume evidence</h3>
                    <p>{applicationPreview.evidence_summary}</p>
                    <h3>Not verified on resume</h3>
                    <p>{applicationPreview.unverified_skills.join(", ") || "None detected"}</p>
                    <h3>Before applying</h3>
                    <ul>{applicationPreview.checklist.map((item) => <li key={item}>{item}</li>)}</ul>
                    {applicationPreview.application_url && (
                      <a className="apply-btn" href={applicationPreview.application_url} target="_blank" rel="noopener noreferrer">Open application <ExternalLink size={15}/></a>
                    )}
                    <p className="preview-note">{applicationPreview.note}</p>
                  </>
                )}
              </>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

export default App;