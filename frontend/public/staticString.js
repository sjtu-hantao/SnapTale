window.user_id = "";
window.device_id = "";
window.ip_and_port = window.location.host;
window.backend_url = window.location.hostname === "localhost"
  ? "http://localhost:8000"
  : `${window.location.protocol}//${window.location.hostname}:8000`;
// For the static params in this file, please remember to declaring them in src/global.d.ts.
