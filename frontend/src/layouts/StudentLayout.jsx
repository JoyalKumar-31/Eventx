import React from "react";
import { LayoutDashboard, Compass, Ticket, Users, CreditCard, QrCode, Award, User } from "lucide-react";
import { DashboardLayout } from "./DashboardLayout";

export const StudentLayout = () => {
  const navItems = [
    { name: "Dashboard", path: "/student/dashboard", icon: LayoutDashboard },
    { name: "Explore Events", path: "/events", icon: Compass },
    { name: "My Registrations", path: "/student/registrations", icon: Ticket },
    { name: "My Teams", path: "/student/teams", icon: Users },
    { name: "Payments & Invoices", path: "/student/payments", icon: CreditCard },
    { name: "Digital Passes", path: "/student/passes", icon: QrCode },
    { name: "Certificates", path: "/student/certificates", icon: Award },
    { name: "My Profile", path: "/student/profile", icon: User },
  ];

  return <DashboardLayout title="Student Portal" navItems={navItems} roleColor="indigo" />;
};
