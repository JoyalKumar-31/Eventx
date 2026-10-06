import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export const RoleRoute = ({ allowedRoles = [], children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-400 text-sm">Verifying access credentials...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Admin has global access or user role must match allowedRoles
  if (user.role === "ADMIN" || allowedRoles.includes(user.role)) {
    return children;
  }

  return <Navigate to="/403" replace />;
};
