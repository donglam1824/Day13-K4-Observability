"""
Streamlit Dashboard cho Day 13 AI Observability
Nguồn dữ liệu: data/logs.jsonl
Tuân thủ hợp đồng: config/dashboard.yaml (6 Panel chuẩn)
"""

import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Day 13 AI Observability Dashboard",
    page_icon="📊",
    layout="wide",
)

LOG_PATH = Path("data/logs.jsonl")

st.title("📊 Day 13 AI Observability Dashboard")
st.markdown("**Nguồn dữ liệu:** `data/logs.jsonl` | **Contract:** `config/dashboard.yaml` (6 Panel chuẩn)")

# Sidebar Controls
st.sidebar.header("⚙️ Cấu hình Dashboard")
auto_refresh = st.sidebar.checkbox("Tự động làm mới (Auto Refresh)", value=False)
time_window_mins = st.sidebar.slider("Khung thời gian xem (phút)", min_value=10, max_value=180, value=60, step=10)

if auto_refresh:
    st.sidebar.caption("Đang làm mới dữ liệu...")
    import time
    time.sleep(15)
    st.rerun()

# Đọc file data/logs.jsonl
@st.cache_data(ttl=3)
def load_data(log_file: Path) -> pd.DataFrame:
    if not log_file.exists():
        return pd.DataFrame()
    
    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    
    if not records:
        return pd.DataFrame()
    
    df = pd.DataFrame(records)
    if "ts" in df.columns:
        df["datetime"] = pd.to_datetime(df["ts"])
    return df

df_raw = load_data(LOG_PATH)

if df_raw.empty or "datetime" not in df_raw.columns:
    st.warning("⚠️ Chưa có dữ liệu trong `data/logs.jsonl`. Vui lòng khởi động ứng dụng và chạy load test để tạo log.")
    st.stop()

# Lọc theo khung thời gian (Default 60 phút)
max_time = df_raw["datetime"].max()
cutoff_time = max_time - pd.Timedelta(minutes=time_window_mins)
df = df_raw[df_raw["datetime"] >= cutoff_time].copy()

st.caption(f"⏱️ **Time Range:** Từ {cutoff_time.strftime('%H:%M:%S')} đến {max_time.strftime('%H:%M:%S')} | **Tổng số records:** {len(df)}")

# Chia làm 2 hàng x 3 cột cho 6 Panel
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

# -------------------------------------------------------------
# PANEL 1: Latency percentiles (P50, P95, P99)
# -------------------------------------------------------------
with col1:
    st.subheader("1. Latency percentiles")
    df_sent = df[df["event"] == "response_sent"].copy()
    
    if not df_sent.empty and "latency_ms" in df_sent.columns:
        p50 = df_sent["latency_ms"].quantile(0.50)
        p95 = df_sent["latency_ms"].quantile(0.95)
        p99 = df_sent["latency_ms"].quantile(0.99)
        
        status = "✅ PASSED" if p95 <= 3000 else "❌ BREACHED"
        st.metric("P95 Latency (ms)", f"{p95:.1f} ms", delta=f"{status} (SLO <= 3000ms)")
        st.caption(f"P50: {p50:.1f}ms | P99: {p99:.1f}ms")
        
        df_sent["minute"] = df_sent["datetime"].dt.floor("min")
        latency_time = df_sent.groupby("minute")["latency_ms"].quantile(0.95).reset_index()
        
        fig1 = px.line(latency_time, x="minute", y="latency_ms", title="P95 Latency over time (ms)")
        fig1.add_hline(y=3000, line_dash="dash", line_color="red", annotation_text="SLO (3000ms)")
        fig1.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu `response_sent`")

# -------------------------------------------------------------
# PANEL 2: Request traffic
# -------------------------------------------------------------
with col2:
    st.subheader("2. Request traffic")
    df_req = df[df["event"] == "request_received"].copy()
    
    if not df_req.empty:
        df_req["minute"] = df_req["datetime"].dt.floor("min")
        traffic_min = df_req.groupby("minute").size().reset_index(name="requests_per_minute")
        avg_rpm = traffic_min["requests_per_minute"].mean() if not traffic_min.empty else 0
        
        status = "✅ PASSED" if avg_rpm >= 1 else "⚠️ LOW TRAFFIC"
        st.metric("Avg Traffic (req/min)", f"{avg_rpm:.1f} req/min", delta=f"{status} (Threshold >= 1)")
        
        fig2 = px.bar(traffic_min, x="minute", y="requests_per_minute", title="Traffic (requests/minute)")
        fig2.add_hline(y=1, line_dash="dash", line_color="green", annotation_text="Threshold (1 req/min)")
        fig2.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu `request_received`")

# -------------------------------------------------------------
# PANEL 3: Error rate and breakdown
# -------------------------------------------------------------
with col3:
    st.subheader("3. Error rate & breakdown")
    total_reqs = len(df[df["event"] == "request_received"])
    failed_reqs = len(df[df["event"] == "request_failed"])
    
    error_rate = (failed_reqs / total_reqs * 100) if total_reqs > 0 else 0.0
    status = "✅ PASSED" if error_rate <= 2.0 else "❌ SLO BREACHED"
    
    st.metric("Error Rate (%)", f"{error_rate:.2f}%", delta=f"{status} (Threshold <= 2%)")
    
    df_err = df[df["event"] == "request_failed"]
    if not df_err.empty and "error_type" in df_err.columns:
        err_counts = df_err["error_type"].value_counts().reset_index()
        err_counts.columns = ["error_type", "count"]
        fig3 = px.pie(err_counts, values="count", names="error_type", title="Error Breakdown")
        fig3.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.success("Không có lỗi (0 Failed Requests)")

# -------------------------------------------------------------
# PANEL 4: Cost over time
# -------------------------------------------------------------
with col4:
    st.subheader("4. Cost over time")
    if not df_sent.empty and "cost_usd" in df_sent.columns:
        total_cost = df_sent["cost_usd"].sum()
        status = "✅ PASSED" if total_cost <= 2.5 else "❌ COST EXCEEDED"
        
        st.metric("Total Cost (USD)", f"${total_cost:.4f}", delta=f"{status} (Threshold <= $2.5)")
        
        df_sent["minute"] = df_sent["datetime"].dt.floor("min")
        cost_time = df_sent.groupby("minute")["cost_usd"].sum().reset_index()
        
        fig4 = px.area(cost_time, x="minute", y="cost_usd", title="Cost per minute ($)")
        fig4.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu `cost_usd`")

# -------------------------------------------------------------
# PANEL 5: Input and output tokens
# -------------------------------------------------------------
with col5:
    st.subheader("5. Input & Output tokens")
    if not df_sent.empty and "tokens_in" in df_sent.columns and "tokens_out" in df_sent.columns:
        total_in = int(df_sent["tokens_in"].sum())
        total_out = int(df_sent["tokens_out"].sum())
        total_tokens = total_in + total_out
        
        status = "✅ PASSED" if total_tokens <= 50000 else "⚠️ HIGH USAGE"
        st.metric("Total Tokens", f"{total_tokens:,}", delta=f"In: {total_in:,} | Out: {total_out:,}")
        
        tokens_summary = pd.DataFrame({
            "Type": ["Input Tokens", "Output Tokens"],
            "Count": [total_in, total_out]
        })
        fig5 = px.bar(tokens_summary, x="Type", y="Count", color="Type", title="Tokens Breakdown")
        fig5.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu tokens")

# -------------------------------------------------------------
# PANEL 6: Quality proxy
# -------------------------------------------------------------
with col6:
    st.subheader("6. Quality proxy")
    if not df_sent.empty and "quality_score" in df_sent.columns:
        avg_quality = df_sent["quality_score"].mean()
        status = "✅ PASSED" if avg_quality >= 0.75 else "❌ QUALITY LOW"
        
        st.metric("Mean Quality Score", f"{avg_quality:.2f}", delta=f"{status} (Threshold >= 0.75)")
        
        df_sent["minute"] = df_sent["datetime"].dt.floor("min")
        quality_time = df_sent.groupby("minute")["quality_score"].mean().reset_index()
        
        fig6 = px.line(quality_time, x="minute", y="quality_score", title="Quality Score over time")
        fig6.add_hline(y=0.75, line_dash="dash", line_color="green", annotation_text="Threshold (0.75)")
        fig6.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu `quality_score`")
