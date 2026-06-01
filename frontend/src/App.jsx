import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  CheckCircle2,
  CircleAlert,
  ClipboardList,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Trash2,
  Users
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

const emptyPlayerForm = {
  name: "",
  age: 25,
  sport: "",
  position: "",
  team: ""
};

const emptyPerformanceForm = {
  player_id: "",
  matches_played: 0,
  minutes_played: 0,
  goals: 0,
  assists: 0,
  accuracy: 0,
  efficiency: 0,
  win_contribution: 0
};

const sports = [
  "Football/Soccer",
  "Basketball",
  "Cricket",
  "Tennis",
  "Rugby"
];

const avatarColors = [
  "#2563eb",
  "#059669",
  "#dc2626",
  "#d97706",
  "#7c3aed",
  "#0891b2",
  "#be123c",
  "#4d7c0f"
];

function App() {
  const [activeTab, setActiveTab] = useState("players");
  const [players, setPlayers] = useState([]);
  const [performances, setPerformances] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [playerForm, setPlayerForm] = useState(emptyPlayerForm);
  const [performanceForm, setPerformanceForm] = useState(emptyPerformanceForm);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [playersResponse, performancesResponse] = await Promise.all([
        fetch(`${API_BASE}/players/`),
        fetch(`${API_BASE}/performances/`)
      ]);

      if (!playersResponse.ok || !performancesResponse.ok) {
        throw new Error("API returned an error");
      }

      setPlayers(await playersResponse.json());
      setPerformances(await performancesResponse.json());
      setApiOnline(true);
    } catch (error) {
      setApiOnline(false);
      showToast("Cannot reach the FastAPI backend on port 8000.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredPlayers = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();
    if (!query) return players;

    return players.filter((player) =>
      [player.name, player.sport, player.position, player.team]
        .join(" ")
        .toLowerCase()
        .includes(query)
    );
  }, [players, searchTerm]);

  const stats = useMemo(() => {
    return [
      {
        label: "Total Players",
        value: players.length,
        helper: "Registered athletes",
        icon: Users,
        tone: "blue"
      },
      {
        label: "Sports",
        value: new Set(players.map((player) => player.sport)).size,
        helper: "Active disciplines",
        icon: Activity,
        tone: "green"
      },
      {
        label: "Teams",
        value: new Set(players.map((player) => player.team)).size,
        helper: "Unique teams",
        icon: ShieldCheck,
        tone: "amber"
      },
      {
        label: "Records",
        value: performances.length,
        helper: "Performance entries",
        icon: BarChart3,
        tone: "rose"
      }
    ];
  }, [players, performances]);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => setToast(null), 4200);
  };

  const submitPlayer = async (event) => {
    event.preventDefault();
    setSaving(true);

    const payload = {
      ...playerForm,
      age: Number(playerForm.age)
    };

    try {
      const response = await fetch(`${API_BASE}/players/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(await response.text());

      setPlayerForm(emptyPlayerForm);
      setActiveTab("players");
      showToast(`${payload.name} was added to the roster.`, "success");
      await loadData();
    } catch (error) {
      showToast("Player could not be saved. Check the required fields.", "error");
    } finally {
      setSaving(false);
    }
  };

  const submitPerformance = async (event) => {
    event.preventDefault();
    setSaving(true);

    const payload = Object.fromEntries(
      Object.entries(performanceForm).map(([key, value]) => [key, Number(value)])
    );

    try {
      const response = await fetch(`${API_BASE}/performances/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(await response.text());

      setPerformanceForm(emptyPerformanceForm);
      showToast("Performance record saved.", "success");
      await loadData();
    } catch (error) {
      showToast("Performance record could not be saved.", "error");
    } finally {
      setSaving(false);
    }
  };

  const deletePlayer = async () => {
    if (!deleteTarget) return;
    setSaving(true);

    try {
      const response = await fetch(`${API_BASE}/players/${deleteTarget.id}`, {
        method: "DELETE"
      });

      if (!response.ok) throw new Error("Delete failed");

      setDeleteTarget(null);
      showToast("Player removed from the roster.", "success");
      await loadData();
    } catch (error) {
      showToast("Player could not be deleted.", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <ClipboardList size={26} />
          </div>
          <div>
            <h1>Sports Analytics</h1>
            <p>Team selection and performance dashboard</p>
          </div>
        </div>

        <div className={`status-pill ${apiOnline ? "online" : "offline"}`}>
          {apiOnline ? <CheckCircle2 size={16} /> : <CircleAlert size={16} />}
          {apiOnline ? "API connected" : "API offline"}
        </div>
      </header>

      <section className="stats-grid" aria-label="Roster summary">
        {stats.map((item) => (
          <StatCard key={item.label} item={item} />
        ))}
      </section>

      <section className="workspace">
        <nav className="tabs" aria-label="Dashboard sections">
          <TabButton
            active={activeTab === "players"}
            icon={Users}
            label="Roster"
            onClick={() => setActiveTab("players")}
          />
          <TabButton
            active={activeTab === "add-player"}
            icon={Plus}
            label="Add Player"
            onClick={() => setActiveTab("add-player")}
          />
          <TabButton
            active={activeTab === "performance"}
            icon={BarChart3}
            label="Log Performance"
            onClick={() => setActiveTab("performance")}
          />
        </nav>

        {activeTab === "players" && (
          <RosterView
            loading={loading}
            players={filteredPlayers}
            searchTerm={searchTerm}
            onRefresh={loadData}
            onSearch={setSearchTerm}
            onDelete={setDeleteTarget}
          />
        )}

        {activeTab === "add-player" && (
          <PlayerForm
            form={playerForm}
            saving={saving}
            onChange={setPlayerForm}
            onReset={() => setPlayerForm(emptyPlayerForm)}
            onSubmit={submitPlayer}
          />
        )}

        {activeTab === "performance" && (
          <PerformanceForm
            form={performanceForm}
            players={players}
            saving={saving}
            onChange={setPerformanceForm}
            onReset={() => setPerformanceForm(emptyPerformanceForm)}
            onSubmit={submitPerformance}
          />
        )}
      </section>

      {deleteTarget && (
        <ConfirmDialog
          player={deleteTarget}
          saving={saving}
          onCancel={() => setDeleteTarget(null)}
          onConfirm={deletePlayer}
        />
      )}

      {toast && <Toast toast={toast} onClose={() => setToast(null)} />}
    </main>
  );
}

function StatCard({ item }) {
  const Icon = item.icon;
  return (
    <article className={`stat-card ${item.tone}`}>
      <div className="stat-card-header">
        <span className="stat-icon">
          <Icon size={20} />
        </span>
        <span className="stat-label">{item.label}</span>
      </div>
      <strong>{item.value}</strong>
      <p>{item.helper}</p>
    </article>
  );
}

function TabButton({ active, icon: Icon, label, onClick }) {
  return (
    <button className={active ? "tab active" : "tab"} type="button" onClick={onClick}>
      <Icon size={16} />
      {label}
    </button>
  );
}

function RosterView({ loading, players, searchTerm, onRefresh, onSearch, onDelete }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Player Roster</h2>
          <p>Search, review, and maintain the active athlete list.</p>
        </div>
        <div className="toolbar">
          <label className="search-input">
            <Search size={16} />
            <input
              value={searchTerm}
              onChange={(event) => onSearch(event.target.value)}
              placeholder="Search players"
              type="search"
            />
          </label>
          <button className="icon-button" type="button" onClick={onRefresh} title="Refresh">
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="empty-state">
          <Loader2 className="spin" size={28} />
          <p>Loading roster...</p>
        </div>
      ) : players.length === 0 ? (
        <div className="empty-state">
          <Users size={34} />
          <h3>No players found</h3>
          <p>Add a player or clear the current search.</p>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Player</th>
                <th>Age</th>
                <th>Sport</th>
                <th>Position</th>
                <th>Team</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {players.map((player, index) => (
                <tr key={player.id}>
                  <td>
                    <div className="player-cell">
                      <span
                        className="avatar"
                        style={{ backgroundColor: avatarColors[index % avatarColors.length] }}
                      >
                        {initials(player.name)}
                      </span>
                      <strong>{player.name}</strong>
                    </div>
                  </td>
                  <td>{player.age}</td>
                  <td>
                    <span className={`sport-badge ${sportClass(player.sport)}`}>
                      {player.sport}
                    </span>
                  </td>
                  <td>{player.position}</td>
                  <td>{player.team}</td>
                  <td>
                    <button
                      className="icon-button danger"
                      type="button"
                      onClick={() => onDelete(player)}
                      title={`Delete ${player.name}`}
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function PlayerForm({ form, saving, onChange, onReset, onSubmit }) {
  const update = (field) => (event) => {
    onChange({ ...form, [field]: event.target.value });
  };

  return (
    <form className="panel form-panel" onSubmit={onSubmit}>
      <div className="panel-header">
        <div>
          <h2>Register New Player</h2>
          <p>Add an athlete with their sport, position, and team.</p>
        </div>
      </div>

      <div className="form-grid">
        <Field label="Full Name" required>
          <input value={form.name} onChange={update("name")} placeholder="Lionel Messi" required />
        </Field>
        <Field label="Age" required>
          <input
            min="15"
            max="50"
            type="number"
            value={form.age}
            onChange={update("age")}
            required
          />
        </Field>
        <Field label="Sport" required>
          <select value={form.sport} onChange={update("sport")} required>
            <option value="">Select sport</option>
            {sports.map((sport) => (
              <option key={sport} value={sport}>
                {sport}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Position" required>
          <input
            value={form.position}
            onChange={update("position")}
            placeholder="Forward"
            required
          />
        </Field>
        <Field label="Current Team" className="wide" required>
          <input value={form.team} onChange={update("team")} placeholder="FC Barcelona" required />
        </Field>
      </div>

      <div className="form-actions">
        <button className="button secondary" type="button" onClick={onReset}>
          Clear
        </button>
        <button className="button primary" type="submit" disabled={saving}>
          {saving ? <Loader2 className="spin" size={16} /> : <Plus size={16} />}
          Register Player
        </button>
      </div>
    </form>
  );
}

function PerformanceForm({ form, players, saving, onChange, onReset, onSubmit }) {
  const update = (field) => (event) => {
    onChange({ ...form, [field]: event.target.value });
  };

  return (
    <form className="panel form-panel" onSubmit={onSubmit}>
      <div className="panel-header">
        <div>
          <h2>Log Performance Record</h2>
          <p>Capture match-level metrics for a rostered athlete.</p>
        </div>
      </div>

      <div className="form-grid compact">
        <Field label="Player" className="wide" required>
          <select value={form.player_id} onChange={update("player_id")} required>
            <option value="">Choose a player</option>
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name} - {player.team} ({player.sport})
              </option>
            ))}
          </select>
        </Field>

        {[
          ["matches_played", "Matches Played"],
          ["minutes_played", "Minutes Played"],
          ["goals", "Goals"],
          ["assists", "Assists"],
          ["accuracy", "Accuracy (%)"],
          ["efficiency", "Efficiency (%)"],
          ["win_contribution", "Win Contribution (%)"]
        ].map(([field, label]) => (
          <Field key={field} label={label}>
            <input
              min="0"
              max={field.includes("accuracy") || field.includes("efficiency") || field.includes("win") ? "100" : undefined}
              step={field.includes("accuracy") || field.includes("efficiency") || field.includes("win") ? "0.1" : "1"}
              type="number"
              value={form[field]}
              onChange={update(field)}
            />
          </Field>
        ))}
      </div>

      <div className="form-actions">
        <button className="button secondary" type="button" onClick={onReset}>
          Clear
        </button>
        <button className="button primary" type="submit" disabled={saving || players.length === 0}>
          {saving ? <Loader2 className="spin" size={16} /> : <BarChart3 size={16} />}
          Save Record
        </button>
      </div>
    </form>
  );
}

function Field({ label, children, required = false, className = "" }) {
  return (
    <label className={`field ${className}`}>
      <span>
        {label} {required && <em>*</em>}
      </span>
      {children}
    </label>
  );
}

function ConfirmDialog({ player, saving, onCancel, onConfirm }) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onCancel}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-player-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal-icon danger">
          <Trash2 size={24} />
        </div>
        <h2 id="delete-player-title">Delete Player</h2>
        <p>
          Remove <strong>{player.name}</strong> from the roster? This cannot be undone.
        </p>
        <div className="modal-actions">
          <button className="button secondary" type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="button danger" type="button" onClick={onConfirm} disabled={saving}>
            {saving ? <Loader2 className="spin" size={16} /> : <Trash2 size={16} />}
            Delete
          </button>
        </div>
      </section>
    </div>
  );
}

function Toast({ toast, onClose }) {
  const Icon = toast.type === "success" ? CheckCircle2 : CircleAlert;
  return (
    <aside className={`toast ${toast.type}`} role="status">
      <Icon size={18} />
      <span>{toast.message}</span>
      <button type="button" onClick={onClose} aria-label="Close notification">
        x
      </button>
    </aside>
  );
}

function initials(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

function sportClass(sport) {
  const normalized = sport.toLowerCase();
  if (normalized.includes("basketball")) return "basketball";
  if (normalized.includes("cricket")) return "cricket";
  if (normalized.includes("tennis")) return "tennis";
  if (normalized.includes("rugby")) return "rugby";
  return "football";
}

export default App;
