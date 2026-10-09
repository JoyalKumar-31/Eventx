import React from "react";
import { LayoutDashboard, Users, Calendar, Briefcase, DollarSign, History, UserCheck } from "lucide-react";
import { DashboardLayout } from "./DashboardLayout";

export const AdminLayout = () => {
  const navItems = [
    { name: "Command Center", path: "/admin/dashboard", icon: LayoutDashboard },
    { name: "Approvals & Invites", path: "/admin/applications", icon: UserCheck },
    { name: "User Directory", path: "/admin/users", icon: Users },
    { name: "Fest Events", path: "/admin/events", icon: Calendar },
    { name: "Financials & Revenue", path: "/admin/revenue", icon: DollarSign },
    { name: "System Audit Logs", path: "/admin/audit-logs", icon: History },
  ];

  return <DashboardLayout title="Admin Command" navItems={navItems} roleColor="purple" />;
};
