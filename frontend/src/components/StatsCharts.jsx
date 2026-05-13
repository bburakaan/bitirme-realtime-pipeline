import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function StatsCharts({ profileData = [], finalizeData = [] }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "24px",
        marginBottom: "24px",
      }}
    >
      <div style={{ background: "#fff", padding: "16px", borderRadius: "12px", border: "1px solid #ddd" }}>
        <h2>Profile Distribution</h2>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={profileData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="profile" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ background: "#fff", padding: "16px", borderRadius: "12px", border: "1px solid #ddd" }}>
        <h2>Finalize Reason Distribution</h2>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={finalizeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="finalize_reason" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}