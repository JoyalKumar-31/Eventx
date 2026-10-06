import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { RoleRoute } from "./auth/RoleRoute";

// Layouts
import { PublicLayout } from "./layouts/PublicLayout";
import { StudentLayout } from "./layouts/StudentLayout";
import { CoordinatorLayout } from "./layouts/CoordinatorLayout";
import { JudgeLayout } from "./layouts/JudgeLayout";
import { AdminLayout } from "./layouts/AdminLayout";
import { SponsorLayout } from "./layouts/SponsorLayout";

// Auth & Error Pages
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import ForbiddenPage from "./pages/auth/ForbiddenPage";
import NotFoundPage from "./pages/auth/NotFoundPage";

// Public Pages
import HomePage from "./pages/public/HomePage";
import EventsPage from "./pages/public/EventsPage";
import EventDetailPage from "./pages/public/EventDetailPage";
import SchedulePage from "./pages/public/SchedulePage";
import VenuesPage from "./pages/public/VenuesPage";
import AnnouncementsPage from "./pages/public/AnnouncementsPage";
import PublicResultsPage from "./pages/public/PublicResultsPage";
import CertificateVerifyPage from "./pages/public/CertificateVerifyPage";

// Student Portal Pages
import StudentDashboard from "./pages/student/StudentDashboard";
import StudentRegistrationsPage from "./pages/student/StudentRegistrationsPage";
import StudentTeamsPage from "./pages/student/StudentTeamsPage";
import StudentPaymentsPage from "./pages/student/StudentPaymentsPage";
import StudentPassPage from "./pages/student/StudentPassPage";
import StudentCertificatesPage from "./pages/student/StudentCertificatesPage";
import StudentProfilePage from "./pages/student/StudentProfilePage";

// Coordinator Portal Pages
import CoordinatorDashboard from "./pages/coordinator/CoordinatorDashboard";
import CoordinatorEventsPage from "./pages/coordinator/CoordinatorEventsPage";
import CoordinatorParticipantsPage from "./pages/coordinator/CoordinatorParticipantsPage";
import CoordinatorJudgesPage from "./pages/coordinator/CoordinatorJudgesPage";
import CoordinatorAttendancePage from "./pages/coordinator/CoordinatorAttendancePage";
import CoordinatorResultsPage from "./pages/coordinator/CoordinatorResultsPage";
import CoordinatorAnalyticsPage from "./pages/coordinator/CoordinatorAnalyticsPage";

// Judge Portal Pages
import JudgeDashboard from "./pages/judge/JudgeDashboard";
import JudgeEventsPage from "./pages/judge/JudgeEventsPage";
import JudgeScoringPage from "./pages/judge/JudgeScoringPage";
import JudgeRankingsPage from "./pages/judge/JudgeRankingsPage";

// Admin Portal Pages
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsersPage from "./pages/admin/AdminUsersPage";
import AdminEventsPage from "./pages/admin/AdminEventsPage";
import AdminSponsorsPage from "./pages/admin/AdminSponsorsPage";
import AdminRevenuePage from "./pages/admin/AdminRevenuePage";
import AdminAuditLogsPage from "./pages/admin/AdminAuditLogsPage";

// Sponsor Portal Pages
import SponsorDashboard from "./pages/sponsor/SponsorDashboard";
import SponsorPlansPage from "./pages/sponsor/SponsorPlansPage";
import SponsorPromotionsPage from "./pages/sponsor/SponsorPromotionsPage";
import SponsorAnalyticsPage from "./pages/sponsor/SponsorAnalyticsPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Pages */}
          <Route element={<PublicLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/:id" element={<EventDetailPage />} />
            <Route path="/schedule" element={<SchedulePage />} />
            <Route path="/venues" element={<VenuesPage />} />
            <Route path="/announcements" element={<AnnouncementsPage />} />
            <Route path="/results" element={<PublicResultsPage />} />
            <Route path="/verify-certificate" element={<CertificateVerifyPage />} />
            <Route path="/verify/:hash" element={<CertificateVerifyPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/403" element={<ForbiddenPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>

          {/* Student Portal */}
          <Route
            path="/student"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={["STUDENT", "ADMIN"]}>
                  <StudentLayout />
                </RoleRoute>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/student/dashboard" replace />} />
            <Route path="dashboard" element={<StudentDashboard />} />
            <Route path="registrations" element={<StudentRegistrationsPage />} />
            <Route path="teams" element={<StudentTeamsPage />} />
            <Route path="payments" element={<StudentPaymentsPage />} />
            <Route path="passes" element={<StudentPassPage />} />
            <Route path="certificates" element={<StudentCertificatesPage />} />
            <Route path="profile" element={<StudentProfilePage />} />
          </Route>

          {/* Coordinator Portal */}
          <Route
            path="/coordinator"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={["EVENT_COORDINATOR", "ADMIN"]}>
                  <CoordinatorLayout />
                </RoleRoute>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/coordinator/dashboard" replace />} />
            <Route path="dashboard" element={<CoordinatorDashboard />} />
            <Route path="events" element={<CoordinatorEventsPage />} />
            <Route path="participants" element={<CoordinatorParticipantsPage />} />
            <Route path="judges" element={<CoordinatorJudgesPage />} />
            <Route path="attendance" element={<CoordinatorAttendancePage />} />
            <Route path="results" element={<CoordinatorResultsPage />} />
            <Route path="analytics" element={<CoordinatorAnalyticsPage />} />
          </Route>

          {/* Judge Portal */}
          <Route
            path="/judge"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={["JUDGE", "ADMIN"]}>
                  <JudgeLayout />
                </RoleRoute>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/judge/dashboard" replace />} />
            <Route path="dashboard" element={<JudgeDashboard />} />
            <Route path="events" element={<JudgeEventsPage />} />
            <Route path="scoring" element={<JudgeScoringPage />} />
            <Route path="rankings" element={<JudgeRankingsPage />} />
          </Route>

          {/* Admin Portal */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={["ADMIN"]}>
                  <AdminLayout />
                </RoleRoute>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsersPage />} />
            <Route path="events" element={<AdminEventsPage />} />
            <Route path="sponsors" element={<AdminSponsorsPage />} />
            <Route path="revenue" element={<AdminRevenuePage />} />
            <Route path="audit-logs" element={<AdminAuditLogsPage />} />
          </Route>

          {/* Sponsor Portal */}
          <Route
            path="/sponsor"
            element={
              <ProtectedRoute>
                <RoleRoute allowedRoles={["SPONSOR", "ADMIN"]}>
                  <SponsorLayout />
                </RoleRoute>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/sponsor/dashboard" replace />} />
            <Route path="dashboard" element={<SponsorDashboard />} />
            <Route path="plans" element={<SponsorPlansPage />} />
            <Route path="my-sponsorships" element={<SponsorPlansPage />} />
            <Route path="promotions" element={<SponsorPromotionsPage />} />
            <Route path="analytics" element={<SponsorAnalyticsPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
