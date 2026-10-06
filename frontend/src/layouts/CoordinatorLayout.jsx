import React from "react";
import { LayoutDashboard, Calendar, Users, Award, Scan, Trophy, BarChart3 } from "lucide-react";
import { DashboardLayout } from "./DashboardLayout";

export const CoordinatorLayout = () => {
  const navItems = [
    { name: "Dashboard", path: "/coordinator/dashboard", icon: LayoutDashboard },
    { name: "Manage Events", path: "/coordinator/events", icon: Calendar },
    { name: "Participants", path: "/coordinator/participants", icon: Users },
    { name: "Assign Judges", path: "/coordinator/judges", icon: Award },
    { name: "QR Scanner & Entry", path: "/coordinator/attendance", icon: Scan },
    { name: "Results & Rankings", path: "/coordinator/results", icon: Trophy },
    { name: "Analytics", path: "/coordinator/analytics", icon: BarChart3 },
  ];

  return <DashboardLayout title="Coordinator Portal" navItems={navItems} roleColor="emerald" />;
};
