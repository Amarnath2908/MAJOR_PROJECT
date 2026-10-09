import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export function MainLayout() {
  const location = useLocation();

  // Pages that benefit from the workspace sidebar
  const sidebarRoutes = ['/dashboard', '/history', '/profile'];
  const showSidebar = sidebarRoutes.includes(location.pathname);

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f19] text-slate-100">
      <Navbar />

      <div className="flex-1 flex w-full">
        {showSidebar && <Sidebar />}

        <main className="flex-1 w-full flex flex-col overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;
