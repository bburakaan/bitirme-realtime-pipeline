import { useEffect, useState } from "react";
import api from "./api";
import SummaryCards from "./components/SummaryCards";
import RecentEventsTable from "./components/RecentEventsTable";
import RecentSessionsTable from "./components/RecentSessionsTable";
import RecentPredictionsTable from "./components/RecentPredictionsTable";
import StatsCharts from "./components/StatsCharts";
import OlistSummaryCards from "./components/OlistSummaryCards";
import RecentOlistOrdersTable from "./components/RecentOlistOrdersTable";
import OlistPaymentsChart from "./components/OlistPaymentsChart";
import IntentModelCards from "./components/IntentModelCards";
import IntentPredictionCard from "./components/IntentPredictionCard";

export default function App() {
  const [summary, setSummary] = useState({
    raw_events_count: 0,
    session_features_count: 0,
    predictions_count: 0,
    profile_distribution: [],
    finalize_reason_distribution: [],
  });
  const [events, setEvents] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [predictions, setPredictions] = useState([]);

  const [olistSummary, setOlistSummary] = useState(null);
  const [olistOrders, setOlistOrders] = useState([]);
  const [olistPayments, setOlistPayments] = useState([]);

  const [intentMetrics, setIntentMetrics] = useState(null);
  const [intentPrediction, setIntentPrediction] = useState(null);

  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      setError("");

      const summaryRes = await api.get("/stats/summary");
      const eventsRes = await api.get("/events/recent?limit=10");
      const sessionsRes = await api.get("/sessions/recent?limit=10");
      const predictionsRes = await api.get("/predictions/recent?limit=10");

      const olistSummaryRes = await api.get("/olist/summary");
      const olistOrdersRes = await api.get("/olist/orders/recent?limit=10");
      const olistPaymentsRes = await api.get("/olist/payments/summary");

      const intentInfoRes = await api.get("/intent/model-info");

      const samplePredictionRes = await api.post("/intent/predict", {
        Administrative: 0,
        Administrative_Duration: 0,
        Informational: 0,
        Informational_Duration: 0,
        ProductRelated: 10,
        ProductRelated_Duration: 627.5,
        BounceRates: 0.02,
        ExitRates: 0.05,
        PageValues: 0,
        SpecialDay: 0,
        Month: "Feb",
        OperatingSystems: 3,
        Browser: 3,
        Region: 1,
        TrafficType: 4,
        VisitorType: "Returning_Visitor",
        Weekend: true,
      });

      setSummary(summaryRes.data || {});
      setEvents(eventsRes.data?.items || []);
      setSessions(sessionsRes.data?.items || []);
      setPredictions(predictionsRes.data?.items || []);

      setOlistSummary(olistSummaryRes.data || {});
      setOlistOrders(olistOrdersRes.data?.items || []);
      setOlistPayments(olistPaymentsRes.data?.items || []);

      setIntentMetrics(intentInfoRes.data?.metrics || {});
      setIntentPrediction(samplePredictionRes.data || {});
    } catch (err) {
      console.error("API error:", err);
      setError("API verisi alınamadı. FastAPI açık mı kontrol et.");
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        maxWidth: "1450px",
        margin: "0 auto",
        padding: "32px 24px",
        color: "#111827",
      }}
    >
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ margin: 0, fontSize: "42px" }}>Realtime E-Commerce Dashboard</h1>
        <p style={{ color: "#6b7280", marginTop: "10px", fontSize: "16px" }}>
          Kafka, PostgreSQL, FastAPI and Machine Learning based monitoring screen
        </p>
      </div>

      {error && (
        <div
          style={{
            background: "#fee2e2",
            color: "#991b1b",
            padding: "14px",
            borderRadius: "12px",
            marginBottom: "20px",
            border: "1px solid #fecaca",
          }}
        >
          {error}
        </div>
      )}

      <SummaryCards summary={summary} />

      <StatsCharts
        profileData={summary?.profile_distribution || []}
        finalizeData={summary?.finalize_reason_distribution || []}
      />

      <RecentEventsTable items={events} />
      <RecentSessionsTable items={sessions} />
      <RecentPredictionsTable items={predictions} />

      <div style={{ marginTop: "40px", marginBottom: "20px" }}>
        <h1 style={{ margin: 0, fontSize: "36px" }}>Olist E-Commerce Data</h1>
        <p style={{ color: "#6b7280", marginTop: "10px", fontSize: "16px" }}>
          Real relational e-commerce dataset integrated into PostgreSQL
        </p>
      </div>

      <OlistSummaryCards summary={olistSummary} />
      <OlistPaymentsChart items={olistPayments} />
      <RecentOlistOrdersTable items={olistOrders} />

      <div style={{ marginTop: "40px", marginBottom: "20px" }}>
        <h1 style={{ margin: 0, fontSize: "36px" }}>Intent Model Analytics</h1>
        <p style={{ color: "#6b7280", marginTop: "10px", fontSize: "16px" }}>
          Online Shoppers Purchasing Intention dataset based model metrics and sample inference
        </p>
      </div>

      <IntentModelCards metrics={intentMetrics} />
      <IntentPredictionCard prediction={intentPrediction} />
    </div>
  );
}