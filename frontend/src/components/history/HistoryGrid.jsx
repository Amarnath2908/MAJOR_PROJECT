import React, { useState, useMemo } from 'react';
import ProjectCard from '../dashboard/ProjectCard';
import ProjectDetailsModal from './ProjectDetailsModal';
import HistoryFilters from './HistoryFilters';
import { Skeleton } from '../common/Loader';
import EmptyState from '../common/EmptyState';
import { History, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function HistoryGrid({
  projects = [],
  isLoading,
  onDeleteProject,
}) {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedProject, setSelectedProject] = useState(null);

  // Filter projects by search query and status
  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      const matchesSearch =
        !searchTerm ||
        (project.title && project.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (project.prompt && project.prompt.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesStatus =
        statusFilter === 'all' || project.status?.toLowerCase() === statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [projects, searchTerm, statusFilter]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-10 w-full max-w-sm bg-slate-800/80 rounded-xl animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="glass-panel rounded-2xl p-3 space-y-3">
              <Skeleton className="w-full aspect-video rounded-xl" />
              <Skeleton className="w-3/4 h-4 rounded-lg" />
              <Skeleton className="w-1/2 h-3 rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Search & Filter Toolbar */}
      <HistoryFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
      />

      {/* Grid or Empty */}
      {filteredProjects.length === 0 ? (
        <EmptyState
          icon={<History className="w-8 h-8 text-brand-400" />}
          title={searchTerm || statusFilter !== 'all' ? 'No matching designs found' : 'No design projects yet'}
          description={
            searchTerm || statusFilter !== 'all'
              ? 'Try adjusting your search terms or filter criteria.'
              : 'Start your creative journey by uploading a room image in Design Studio.'
          }
          actionLabel={searchTerm || statusFilter !== 'all' ? 'Clear Filters' : '+ Create New Design'}
          onAction={() => {
            if (searchTerm || statusFilter !== 'all') {
              setSearchTerm('');
              setStatusFilter('all');
            } else {
              navigate('/studio');
            }
          }}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.project_id}
              project={project}
              onOpen={(p) => setSelectedProject(p)}
              onDelete={onDeleteProject}
            />
          ))}
        </div>
      )}

      {/* Detail Modal */}
      <ProjectDetailsModal
        project={selectedProject}
        isOpen={!!selectedProject}
        onClose={() => setSelectedProject(null)}
        onDelete={(id) => {
          if (onDeleteProject) onDeleteProject(id);
          setSelectedProject(null);
        }}
      />
    </div>
  );
}

export default HistoryGrid;
