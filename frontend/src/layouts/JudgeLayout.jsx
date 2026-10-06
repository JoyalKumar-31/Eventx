import React from "react";
import { LayoutDashboard, Calendar, ClipboardCheck, Trophy } from "lucide-react";
import { DashboardLayout } from "./DashboardLayout";

export const JudgeLayout = () => {
  const navItems = [
    { name: "Dashboard", path: "/judge/dashboard", icon: LayoutDashboard },
    { name: "My Assigned Events", path: "/judge/events", icon: Calendar },
    { name: "Scoring Matrix", path: "/judge/scoring", icon: ClipboardCheck },
    { name: "Live Rankings", path: "/judge/rankings", icon: Trophy },
  ];

  return <DashboardLayout title="Judge Portal" navItems={navItems} roleColor="amber" />;
};
