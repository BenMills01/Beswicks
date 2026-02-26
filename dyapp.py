import streamlit as st
import pandas as pd
import os
import glob

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SEASON_FILE = "data/season_overview.xlsx"
MATCH_FOLDER = "data/match_logs/"

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Beswicks Sports — Client Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        background-color: #0a0e17;
        color: #e0e4ec;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #101828;
        border-right: 1px solid #1e2a3a;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #f97316;
    }

    h1, h2, h3 {
        font-family: 'Space Mono', monospace !important;
        color: #ffffff !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #141c2e 0%, #1a2540 100%);
        border: 1px solid #1e2a3a;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetric"] label {
        color: #8896ab !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f97316 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 1.8rem !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #101828;
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8896ab;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f97316 !important;
        color: #0a0e17 !important;
    }

    .stSelectbox label {
        color: #8896ab !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 0.05em;
    }

    hr {
        border-color: #1e2a3a !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .position-badge {
        display: inline-block;
        background: #1e2a3a;
        color: #f97316;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'Space Mono', monospace;
        border: 1px solid #2a3a50;
    }
    .club-badge {
        display: inline-block;
        background: #141c2e;
        color: #e0e4ec;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'DM Sans', sans-serif;
        border: 1px solid #1e2a3a;
    }

    /* Rating colours */
    .rating-excellent { background-color: #166534; color: #ffffff; padding: 4px 10px; border-radius: 8px; font-weight: 700; text-align: center; }
    .rating-good { background-color: #15803d; color: #ffffff; padding: 4px 10px; border-radius: 8px; font-weight: 700; text-align: center; }
    .rating-average { background-color: #a16207; color: #ffffff; padding: 4px 10px; border-radius: 8px; font-weight: 700; text-align: center; }
    .rating-belowavg { background-color: #c2410c; color: #ffffff; padding: 4px 10px; border-radius: 8px; font-weight: 700; text-align: center; }
    .rating-poor { background-color: #991b1b; color: #ffffff; padding: 4px 10px; border-radius: 8px; font-weight: 700; text-align: center; }
    .rating-minimal { background-color: #374151; color: #9ca3af; padding: 4px 10px; border-radius: 8px; font-weight: 700; text-align: center; }

    /* Game log table */
    .game-log-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
    }
    .game-log-table th {
        background-color: #1a2540;
        color: #f97316;
        padding: 10px 12px;
        text-align: left;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #2a3a50;
    }
    .game-log-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #1e2a3a;
        color: #e0e4ec;
    }
    .game-log-table tr:hover {
        background-color: #141c2e;
    }
    .game-log-table .match-col {
        max-width: 280px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .game-log-table .num-col {
        text-align: center;
        min-width: 40px;
    }
    .game-log-table .rating-col {
        text-align: center;
        min-width: 70px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# POSITION-WEIGHTED PERFORMANCE RATING
# ─────────────────────────────────────────────
def get_position_group(position):
    """Map Wyscout positions to a simplified group."""
    if pd.isna(position) or position is None:
        return "outfield"
    pos = str(position).upper()
    if "GK" in pos:
        return "gk"
    elif any(p in pos for p in ["CB", "LCB", "RCB"]):
        return "cb"
    elif any(p in pos for p in ["RB", "LB", "RWB", "LWB", "WB"]):
        return "fb"
    elif any(p in pos for p in ["CF", "ST", "LW", "RW", "RWF", "LWF"]):
        return "forward"
    elif any(p in pos for p in ["MF", "CM", "DM", "AM", "RCMF", "LCMF", "RDMF", "LDMF", "RAMF", "LAMF", "CAM", "CDM"]):
        return "mid"
    else:
        return "outfield"


def safe_pct(numerator, denominator):
    """Safely compute a percentage."""
    try:
        n = float(numerator) if pd.notna(numerator) else 0
        d = float(denominator) if pd.notna(denominator) else 0
        if d == 0:
            return 0
        return (n / d) * 100
    except (ValueError, TypeError):
        return 0


def safe_float(val):
    """Safely convert to float."""
    try:
        if pd.notna(val):
            return float(val)
    except (ValueError, TypeError):
        pass
    return 0.0


def calculate_performance_rating(row, pos_group, minutes):
    """
    Calculate a 1-10 performance rating weighted by position.
    Returns a float score.
    """
    if minutes < 10:
        return None  # Too few minutes to rate

    # Normalise to per-90 basis
    factor = 90.0 / max(minutes, 1)

    # Common stats (per 90)
    goals_p90 = safe_float(row.get("Goals", 0)) * factor
    assists_p90 = safe_float(row.get("Assists", 0)) * factor
    xg_p90 = safe_float(row.get("xG", 0)) * factor
    xa_p90 = safe_float(row.get("xA", 0)) * factor
    shot_assists_p90 = safe_float(row.get("Shot assists", 0)) * factor

    duels = safe_float(row.get("Duels", 0))
    duels_won = safe_float(row.get("Duels_won", 0))
    duel_pct = safe_pct(duels_won, duels) if duels > 0 else 50

    passes = safe_float(row.get("Passes", 0))
    passes_acc = safe_float(row.get("Passes_accurate", 0))
    pass_pct = safe_pct(passes_acc, passes) if passes > 0 else 50

    interceptions_p90 = safe_float(row.get("Interceptions", 0)) * factor
    recoveries_p90 = safe_float(row.get("Recoveries", 0)) * factor
    clearances_p90 = safe_float(row.get("Clearances", 0)) * factor

    aerial = safe_float(row.get("Aerial duels", 0))
    aerial_won = safe_float(row.get("Aerial duels_won", 0))
    aerial_pct = safe_pct(aerial_won, aerial) if aerial > 0 else 50

    dribbles = safe_float(row.get("Dribbles", 0))
    dribbles_succ = safe_float(row.get("Dribbles_successful", 0))
    dribble_pct = safe_pct(dribbles_succ, dribbles) if dribbles > 0 else 50

    crosses = safe_float(row.get("Crosses", 0))
    crosses_acc = safe_float(row.get("Crosses_accurate", 0))
    cross_pct = safe_pct(crosses_acc, crosses) if crosses > 0 else 50

    progressive_runs_p90 = safe_float(row.get("Progressive runs", 0)) * factor
    touches_box_p90 = safe_float(row.get("Touches in penalty area", 0)) * factor

    shots = safe_float(row.get("Shots", 0))
    shots_on_target = safe_float(row.get("Shots_on target", 0))
    shot_accuracy = safe_pct(shots_on_target, shots) if shots > 0 else 50

    losses_p90 = safe_float(row.get("Losses", 0)) * factor
    fouls_p90 = safe_float(row.get("Fouls", 0)) * factor
    yellow = safe_float(row.get("Yellow cards", 0))
    red = safe_float(row.get("Red cards", 0))

    # Action success rate
    total_actions = safe_float(row.get("Total actions", 0))
    total_actions_succ = safe_float(row.get("Total actions_successful", 0))
    action_pct = safe_pct(total_actions_succ, total_actions) if total_actions > 0 else 50

    # GK specific
    saves = safe_float(row.get("Saves", 0))
    shots_against = safe_float(row.get("Shots against", 0))
    save_pct = safe_pct(saves, shots_against) if shots_against > 0 else 70
    conceded = safe_float(row.get("Conceded goals", 0))
    xcg = safe_float(row.get("xCG", 0))
    exits_p90 = safe_float(row.get("Exits", 0)) * factor

    # Defensive duels
    def_duels = safe_float(row.get("Defensive duels", 0))
    def_duels_won = safe_float(row.get("Defensive duels_won", 0))
    def_duel_pct = safe_pct(def_duels_won, def_duels) if def_duels > 0 else 50

    # Discipline penalty
    discipline_penalty = (yellow * 0.5) + (red * 2.0)

    score = 5.0  # Start at average

    if pos_group == "gk":
        # GK: saves, goals prevented, distribution, commanding area
        if shots_against > 0:
            save_score = min((save_pct / 100) * 4, 4)  # up to +4
        else:
            save_score = 2.0  # untested = average
        goals_prevented = xcg - conceded  # positive = good
        prevention_score = min(max(goals_prevented * 1.5, -2), 2)  # -2 to +2
        dist_score = min((pass_pct / 100) * 1.5, 1.5)  # up to +1.5
        command_score = min(exits_p90 * 0.3, 0.5)  # up to +0.5

        score = 4.0 + save_score + prevention_score + dist_score + command_score
        score -= discipline_penalty

    elif pos_group == "cb":
        # CB: duels, aerials, interceptions, clearances, passing, discipline
        duel_score = min((duel_pct / 100) * 2.5, 2.5)
        aerial_score = min((aerial_pct / 100) * 1.5, 1.5)
        def_actions = min((interceptions_p90 + clearances_p90 + recoveries_p90) * 0.2, 1.5)
        pass_score = min((pass_pct / 100) * 1.5, 1.5)
        loss_penalty = min(losses_p90 * 0.15, 1.0)
        goal_bonus = goals_p90 * 3  # rare but valuable
        assist_bonus = assists_p90 * 2

        score = 3.5 + duel_score + aerial_score + def_actions + pass_score - loss_penalty + goal_bonus + assist_bonus
        score -= discipline_penalty

    elif pos_group == "fb":
        # Fullback/Wingback: crosses, progressive runs, duels, tackles, passing
        duel_score = min((duel_pct / 100) * 1.5, 1.5)
        cross_score = min(cross_pct / 100 * 1.0 + crosses * factor * 0.2, 1.5)
        prog_score = min(progressive_runs_p90 * 0.4, 1.5)
        pass_score = min((pass_pct / 100) * 1.5, 1.5)
        def_score = min((interceptions_p90 + recoveries_p90) * 0.2, 1.0)
        loss_penalty = min(losses_p90 * 0.1, 0.8)
        goal_bonus = goals_p90 * 3
        assist_bonus = assists_p90 * 2.5

        score = 3.5 + duel_score + cross_score + prog_score + pass_score + def_score - loss_penalty + goal_bonus + assist_bonus
        score -= discipline_penalty

    elif pos_group == "mid":
        # Midfielder: pass accuracy, key passes, progressive play, duels, goals/assists
        pass_score = min((pass_pct / 100) * 2.0, 2.0)
        creation_score = min((shot_assists_p90 + xa_p90) * 1.5, 2.0)
        duel_score = min((duel_pct / 100) * 1.5, 1.5)
        prog_score = min(progressive_runs_p90 * 0.3, 1.0)
        recovery_score = min(recoveries_p90 * 0.15, 0.8)
        loss_penalty = min(losses_p90 * 0.1, 0.8)
        goal_bonus = goals_p90 * 2.5
        assist_bonus = assists_p90 * 2.5

        score = 3.5 + pass_score + creation_score + duel_score + prog_score + recovery_score - loss_penalty + goal_bonus + assist_bonus
        score -= discipline_penalty

    elif pos_group == "forward":
        # Forward/Winger: goals, xG, shots, dribbles, assists, touches in box
        goal_score = min(goals_p90 * 3.0, 3.0)
        xg_score = min(xg_p90 * 2.0, 2.0)
        shot_score = min(shot_accuracy / 100 * 1.0 + shots * factor * 0.15, 1.5)
        dribble_score = min(dribble_pct / 100 * 0.8 + dribbles_succ * factor * 0.2, 1.0)
        creation_score = min((assists_p90 * 2.5 + xa_p90 * 1.5 + shot_assists_p90 * 0.5), 2.0)
        box_presence = min(touches_box_p90 * 0.2, 0.8)
        loss_penalty = min(losses_p90 * 0.05, 0.5)

        score = 3.0 + goal_score + xg_score + shot_score + dribble_score + creation_score + box_presence - loss_penalty
        score -= discipline_penalty

    else:
        # Generic outfield
        action_score = min((action_pct / 100) * 3, 3)
        duel_score = min((duel_pct / 100) * 2, 2)
        goal_bonus = goals_p90 * 2.5
        assist_bonus = assists_p90 * 2
        score = 3.5 + action_score + duel_score + goal_bonus + assist_bonus
        score -= discipline_penalty

    # Clamp to 1-10
    score = max(1.0, min(10.0, score))

    # Minutes adjustment: if played less than 45 mins, slightly regress towards average
    if minutes < 45:
        weight = minutes / 45.0
        score = score * weight + 5.0 * (1 - weight)

    return round(score, 1)


def rating_to_html(rating):
    """Convert a rating to a coloured HTML badge."""
    if rating is None:
        return '<span class="rating-minimal">—</span>'
    if rating >= 8.0:
        css = "rating-excellent"
    elif rating >= 6.5:
        css = "rating-good"
    elif rating >= 5.0:
        css = "rating-average"
    elif rating >= 3.5:
        css = "rating-belowavg"
    else:
        css = "rating-poor"
    return f'<span class="{css}">{rating}</span>'


def rating_label(rating):
    """Get a text label for a rating."""
    if rating is None:
        return "N/A"
    if rating >= 8.0:
        return "Excellent"
    elif rating >= 6.5:
        return "Good"
    elif rating >= 5.0:
        return "Average"
    elif rating >= 3.5:
        return "Below Avg"
    else:
        return "Poor"


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_season_data():
    df = pd.read_excel(SEASON_FILE)
    return df


@st.cache_data
def load_match_data():
    all_matches = []
    files = glob.glob(os.path.join(MATCH_FOLDER, "*.xlsx"))

    for f in files:
        df_raw = pd.read_excel(f, header=None)
        headers_row = df_raw.iloc[0].tolist()

        fixed_headers = []
        last_named = ""
        for h in headers_row:
            if h is None or pd.isna(h):
                if "/" in last_named:
                    parts = last_named.split("/")
                    base = parts[0].strip()
                    second_part = parts[1].strip()
                    fixed_headers[-1] = base
                    fixed_headers.append(f"{base}_{second_part}")
                else:
                    fixed_headers.append(f"{last_named}_part2")
            else:
                fixed_headers.append(str(h))
                last_named = str(h)

        seen = {}
        unique_headers = []
        for h in fixed_headers:
            if h in seen:
                seen[h] += 1
                unique_headers.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 0
                unique_headers.append(h)

        df = df_raw.iloc[1:].copy()
        df.columns = unique_headers

        basename = os.path.basename(f)
        player_name = basename.replace("Player_stats_", "").replace(".xlsx", "").replace("__", " ").replace("_", " ").strip()
        df.insert(0, "Player", player_name)
        all_matches.append(df)

    if all_matches:
        combined = pd.concat(all_matches, ignore_index=True)
        combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
        for col in combined.columns:
            if col not in ["Player", "Match", "Competition", "Date", "Position"]:
                combined[col] = pd.to_numeric(combined[col], errors="coerce")
        combined = combined.sort_values(["Player", "Date"], ascending=[True, False])
        return combined
    return pd.DataFrame()


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
season_df = load_season_data()
match_df = load_match_data()
players = season_df["Player"].tolist() if not season_df.empty else []

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("# ⚽ BESWICKS")
    st.markdown("### Client Performance")
    st.markdown("---")
    st.markdown(f"**Clients tracked:** {len(players)}")
    if not match_df.empty:
        latest = match_df["Date"].max()
        if pd.notna(latest):
            st.markdown(f"**Last updated:** {latest.strftime('%d %b %Y')}")
    st.markdown("---")
    st.markdown("##### Rating Guide")
    st.markdown("""
    <div style="font-size: 0.8rem; line-height: 2;">
    <span class="rating-excellent">8-10</span> Excellent<br>
    <span class="rating-good">6.5-8</span> Good<br>
    <span class="rating-average">5-6.5</span> Average<br>
    <span class="rating-belowavg">3.5-5</span> Below Avg<br>
    <span class="rating-poor">1-3.5</span> Poor<br>
    <span class="rating-minimal">—</span> &lt;10 mins
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("##### How to update")
    st.markdown("""
    1. Export match data from Wyscout
    2. Drop files into `data/match_logs/`
    3. Refresh this page
    """)

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown("# ⚽ BESWICKS SPORTS")
st.markdown("### Client Performance Dashboard")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 SEASON OVERVIEW", "👤 PLAYER PROFILE"])

# ─────────────────────────────────────────────
# TAB 1: SEASON OVERVIEW
# ─────────────────────────────────────────────
with tab1:
    if season_df.empty:
        st.warning("No season data found. Place your season overview file in data/season_overview.xlsx")
    else:
        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Clients", len(players))
        with col2:
            total_goals = int(season_df["Goals"].sum()) if "Goals" in season_df.columns else 0
            st.metric("Total Goals", total_goals)
        with col3:
            total_assists = int(season_df["Assists"].sum()) if "Assists" in season_df.columns else 0
            st.metric("Total Assists", total_assists)
        with col4:
            total_apps = int(season_df["Matches played"].sum()) if "Matches played" in season_df.columns else 0
            st.metric("Total Appearances", total_apps)
        with col5:
            total_mins = int(season_df["Minutes played"].sum()) if "Minutes played" in season_df.columns else 0
            st.metric("Total Minutes", f"{total_mins:,}")

        st.markdown("---")
        st.markdown("#### All Clients — Season Stats")

        display_cols = ["Player", "Team", "Position", "Age", "Matches played",
                        "Minutes played", "Goals", "Assists", "xG", "xA",
                        "Duels per 90", "Duels won, %"]
        available_cols = [c for c in display_cols if c in season_df.columns]
        overview_df = season_df[available_cols].copy()

        st.dataframe(
            overview_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Player": st.column_config.TextColumn("PLAYER", width="medium"),
                "Team": st.column_config.TextColumn("CLUB", width="medium"),
                "Position": st.column_config.TextColumn("POS", width="small"),
                "Age": st.column_config.NumberColumn("AGE", width="small"),
                "Matches played": st.column_config.NumberColumn("APPS", width="small"),
                "Minutes played": st.column_config.NumberColumn("MINS", width="small", format="%d"),
                "Goals": st.column_config.NumberColumn("G", width="small"),
                "Assists": st.column_config.NumberColumn("A", width="small"),
                "xG": st.column_config.NumberColumn("xG", width="small", format="%.1f"),
                "xA": st.column_config.NumberColumn("xA", width="small", format="%.1f"),
                "Duels per 90": st.column_config.NumberColumn("DUELS/90", width="small", format="%.1f"),
                "Duels won, %": st.column_config.NumberColumn("DUEL%", width="small", format="%.1f"),
            }
        )

# ─────────────────────────────────────────────
# TAB 2: PLAYER PROFILE
# ─────────────────────────────────────────────
with tab2:
    if not players:
        st.warning("No player data loaded.")
    else:
        selected_player = st.selectbox("Select Client", players, key="profile_player")

        # Get season stats
        player_season = season_df[season_df["Player"] == selected_player]
        if not player_season.empty:
            ps = player_season.iloc[0]

            # Header
            st.markdown(f"## {selected_player}")
            pos = ps.get("Position", "N/A")
            team = ps.get("Team", "N/A")
            age = ps.get("Age", "N/A")
            st.markdown(
                f'<span class="club-badge">{team}</span> '
                f'<span class="position-badge">{pos}</span> '
                f'<span class="club-badge">Age: {age}</span>',
                unsafe_allow_html=True
            )
            st.markdown("")

            # Key metrics
            is_gk = "GK" in str(pos)
            if is_gk:
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                with c1:
                    st.metric("Appearances", int(ps.get("Matches played", 0)))
                with c2:
                    st.metric("Minutes", f"{int(ps.get('Minutes played', 0)):,}")
                with c3:
                    st.metric("Clean Sheets", int(ps.get("Clean sheets", 0)))
                with c4:
                    sr = ps.get("Save rate, %", 0)
                    st.metric("Save Rate", f"{sr:.1f}%" if pd.notna(sr) else "N/A")
                with c5:
                    st.metric("Conceded", int(ps.get("Conceded goals", 0)))
                with c6:
                    pg = ps.get("Prevented goals", 0)
                    st.metric("Goals Prevented", f"{pg:.1f}" if pd.notna(pg) else "N/A")
            else:
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                with c1:
                    st.metric("Appearances", int(ps.get("Matches played", 0)))
                with c2:
                    st.metric("Minutes", f"{int(ps.get('Minutes played', 0)):,}")
                with c3:
                    st.metric("Goals", int(ps.get("Goals", 0)))
                with c4:
                    st.metric("Assists", int(ps.get("Assists", 0)))
                with c5:
                    xg = ps.get("xG", 0)
                    st.metric("xG", f"{xg:.2f}" if pd.notna(xg) else "0")
                with c6:
                    xa = ps.get("xA", 0)
                    st.metric("xA", f"{xa:.2f}" if pd.notna(xa) else "0")

        # Game by game log
        st.markdown("---")
        st.markdown("#### Game by Game")

        if match_df.empty:
            st.info("No match-by-match data loaded.")
        else:
            player_matches = match_df[match_df["Player"].str.contains(
                selected_player.split()[-1], case=False, na=False
            )].copy()

            if player_matches.empty:
                st.info(f"No match data found for {selected_player}.")
            else:
                # Calculate ratings
                ratings = []
                for _, row in player_matches.iterrows():
                    mins = safe_float(row.get("Minutes played", 0))
                    pos_group = get_position_group(row.get("Position", ""))
                    rating = calculate_performance_rating(row, pos_group, mins)
                    ratings.append(rating)
                player_matches = player_matches.copy()
                player_matches["Rating"] = ratings

                # Average rating
                valid_ratings = [r for r in ratings if r is not None]
                if valid_ratings:
                    avg_rating = sum(valid_ratings) / len(valid_ratings)
                    st.markdown(
                        f"**Season Average Rating:** {rating_to_html(round(avg_rating, 1))} "
                        f"({rating_label(avg_rating)}) from {len(valid_ratings)} rated appearances",
                        unsafe_allow_html=True
                    )

                # Build HTML table
                is_gk_player = player_matches["Position"].str.contains("GK", na=False).any()

                if is_gk_player:
                    header_cols = ["Date", "Match", "Mins", "Rating", "Conceded", "xCG", "Saves", "Save%", "Passes", "Pass%", "Exits"]
                else:
                    header_cols = ["Date", "Match", "Pos", "Mins", "Rating", "G", "A", "xG", "Shots", "Passes", "Pass%", "Duels", "Duel%", "Int"]

                html = '<table class="game-log-table"><thead><tr>'
                for col in header_cols:
                    html += f'<th>{col}</th>'
                html += '</tr></thead><tbody>'

                for _, row in player_matches.iterrows():
                    mins = safe_float(row.get("Minutes played", 0))
                    rating = row.get("Rating", None)
                    date_str = row["Date"].strftime("%d %b %Y") if pd.notna(row.get("Date")) else ""
                    match_str = str(row.get("Match", ""))[:45]
                    position_str = str(row.get("Position", ""))

                    if is_gk_player:
                        conceded = int(safe_float(row.get("Conceded goals", 0)))
                        xcg = f"{safe_float(row.get('xCG', 0)):.2f}"
                        saves_val = int(safe_float(row.get("Saves", 0)))
                        shots_ag = safe_float(row.get("Shots against", 0))
                        save_rate = f"{safe_pct(saves_val, shots_ag):.0f}%" if shots_ag > 0 else "—"
                        p = int(safe_float(row.get("Passes", 0)))
                        pa = safe_float(row.get("Passes_accurate", 0))
                        pp = f"{safe_pct(pa, p):.0f}%" if p > 0 else "—"
                        exits = int(safe_float(row.get("Exits", 0)))

                        html += '<tr>'
                        html += f'<td>{date_str}</td>'
                        html += f'<td class="match-col">{match_str}</td>'
                        html += f'<td class="num-col">{int(mins)}</td>'
                        html += f'<td class="rating-col">{rating_to_html(rating)}</td>'
                        html += f'<td class="num-col">{conceded}</td>'
                        html += f'<td class="num-col">{xcg}</td>'
                        html += f'<td class="num-col">{saves_val}</td>'
                        html += f'<td class="num-col">{save_rate}</td>'
                        html += f'<td class="num-col">{p}</td>'
                        html += f'<td class="num-col">{pp}</td>'
                        html += f'<td class="num-col">{exits}</td>'
                        html += '</tr>'
                    else:
                        g = int(safe_float(row.get("Goals", 0)))
                        a = int(safe_float(row.get("Assists", 0)))
                        xg = f"{safe_float(row.get('xG', 0)):.2f}"
                        shots = int(safe_float(row.get("Shots", 0)))
                        p = int(safe_float(row.get("Passes", 0)))
                        pa = safe_float(row.get("Passes_accurate", 0))
                        pp = f"{safe_pct(pa, p):.0f}%" if p > 0 else "—"
                        d = int(safe_float(row.get("Duels", 0)))
                        dw = safe_float(row.get("Duels_won", 0))
                        dp = f"{safe_pct(dw, d):.0f}%" if d > 0 else "—"
                        interceptions = int(safe_float(row.get("Interceptions", 0)))

                        html += '<tr>'
                        html += f'<td>{date_str}</td>'
                        html += f'<td class="match-col">{match_str}</td>'
                        html += f'<td>{position_str}</td>'
                        html += f'<td class="num-col">{int(mins)}</td>'
                        html += f'<td class="rating-col">{rating_to_html(rating)}</td>'
                        html += f'<td class="num-col">{g}</td>'
                        html += f'<td class="num-col">{a}</td>'
                        html += f'<td class="num-col">{xg}</td>'
                        html += f'<td class="num-col">{shots}</td>'
                        html += f'<td class="num-col">{p}</td>'
                        html += f'<td class="num-col">{pp}</td>'
                        html += f'<td class="num-col">{d}</td>'
                        html += f'<td class="num-col">{dp}</td>'
                        html += f'<td class="num-col">{interceptions}</td>'
                        html += '</tr>'

                html += '</tbody></table>'
                st.markdown(html, unsafe_allow_html=True)
