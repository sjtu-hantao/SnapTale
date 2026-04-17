import React, { useEffect, useState } from "react";
import { Alert, ConfigProvider, Result, Spin } from "antd";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import "./App.css";
import AppShell from "./components/AppShell";
import GrowthPage from "./pages/GrowthPage";
import StudioPage from "./pages/StudioPage";
import { bootstrapUser, getStoredUserId } from "./lib/mvpApi";

interface SessionState {
  userId: string;
  username: string;
}

const App: React.FC = () => {
  const [session, setSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [bootstrapError, setBootstrapError] = useState("");

  useEffect(() => {
    const bootstrap = async () => {
      setLoading(true);
      setBootstrapError("");
      try {
        const existingUserId = getStoredUserId() || window.user_id;
        const response = await bootstrapUser(existingUserId || undefined);
        setSession({
          userId: response.user.user_id,
          username: response.user.username,
        });
      } catch (error) {
        setBootstrapError("Unable to bootstrap the local MVP user. Make sure the backend is running on port 8000.");
      } finally {
        setLoading(false);
      }
    };

    void bootstrap();
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <Spin size="large" />
      </div>
    );
  }

  if (bootstrapError || !session) {
    return (
      <div className="loading-screen">
        <Result
          status="warning"
          title="Backend connection required"
          subTitle="Start the FastAPI server before opening the MVP studio."
          extra={<Alert type="warning" message={bootstrapError || "No local session found."} showIcon />}
        />
      </div>
    );
  }

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#9b6b2f",
          colorInfo: "#9b6b2f",
          borderRadius: 18,
          fontFamily: '"Aptos", "Segoe UI Variable", "Trebuchet MS", sans-serif',
        },
      }}
    >
      <BrowserRouter>
        <AppShell username={session.username}>
          <Routes>
            <Route
              path="/"
              element={<StudioPage userId={session.userId} onActivityChange={() => setRefreshKey((value) => value + 1)} />}
            />
            <Route path="/growth" element={<GrowthPage userId={session.userId} refreshKey={refreshKey} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
