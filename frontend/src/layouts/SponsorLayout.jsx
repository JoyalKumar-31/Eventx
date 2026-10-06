import React from "react";
import { LayoutDashboard, Award, Sparkles, Image, BarChart3 } from "lucide-react";
import { DashboardLayout } from "./DashboardLayout";

export const SponsorLayout = () => {
  const navItems = [
    { name: "Dashboard", path: "/sponsor/dashboard", icon: LayoutDashboard },
    { name: "Sponsorship Packages", path: "/sponsor/plans", icon: Award },
    { name: "My Sponsorships", path: "/sponsor/my-sponsorships", icon: Sparkles },
    { name: "Promotion Slots", path: "/sponsor/promotions", icon: Image },
    { name: "Reach & Analytics", path: "/sponsor/analytics", icon: BarChart3 },
  ];

  return <DashboardLayout title="Sponsor Portal" navItems={navItems} roleColor="sky" />;
};
