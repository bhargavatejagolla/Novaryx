import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './components/ThemeProvider'
import { AuthProvider } from './hooks/useAuth'
import ProtectedRoute from './components/ProtectedRoute'
import DashboardLayout from './layouts/DashboardLayout'

import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import UserManagement from './pages/UserManagement'
import Settings from './pages/Settings'
import Profile from './pages/Profile'
import StatsCards from './pages/StatsCards'
import Notifications from './pages/Notifications'
import Help from './pages/Help'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        {/* Public routes */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />

                        {/* Protected routes inside layout */}
                        <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/dashboard/analytics" element={<Analytics />} />
                            <Route path="/dashboard/stats" element={<StatsCards />} />
                            <Route path="/settings/users" element={<UserManagement />} />
                            <Route path="/settings" element={<Settings />} />
                            <Route path="/settings/profile" element={<Profile />} />
                            <Route path="/settings/notifications" element={<Notifications />} />
                            <Route path="/help" element={<Help />} />
                        </Route>

                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </ThemeProvider>
    )
}
