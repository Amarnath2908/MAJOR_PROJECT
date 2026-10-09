import React, { useState } from 'react';
import { History, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useProjectsQuery, useDeleteProjectMutation } from '../queries/useQueries';
import HistoryGrid from '../components/history/HistoryGrid';
import Button from '../components/common/Button';

export function ProjectHistory() {
  const [page, setPage] = useState(1);
  const pageSize = 24;

  const { data: historyData, isLoading } = useProjectsQuery(page, pageSize);
  const deleteMutation = useDeleteProjectMutation();

  const projects = historyData?.projects || [];
  const total = historyData?.total || 0;

  const handleDelete = (projectId) => {
    deleteMutation.mutate(projectId);
  };

  return (
    <div className="p-6 sm:p-8 max-w-7xl mx-auto w-full space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2.5">
            <History className="w-7 h-7 text-brand-400" />
            Project Design History
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Browse, inspect, and reopen your previous interior customizations and 3D scenes.
          </p>
        </div>

        <Link to="/studio">
          <Button size="md" leftIcon={<PlusCircle className="w-4 h-4" />}>
            New Design
          </Button>
        </Link>
      </div>

      {/* Main Grid */}
      <HistoryGrid
        projects={projects}
        isLoading={isLoading}
        onDeleteProject={handleDelete}
      />
    </div>
  );
}

export default ProjectHistory;
