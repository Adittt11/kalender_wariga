import { Navigate, useLocation } from "react-router-dom";
import { isAdminLoggedIn } from "../services/adminAuthApi";

export default function RequireAdmin({ children }) {
  const location = useLocation();

  if (!isAdminLoggedIn()) {
    return <Navigate replace to="/admin-login" state={{ from: location }} />;
  }

  return children;
}
