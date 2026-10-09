import React from 'react';
import { Sparkles, Plus } from 'lucide-react';
import ProjectCard from './ProjectCard';
import { Skeleton } from '../common/Loader';
import EmptyState from '../common/EmptyState';
import Button from '../common/Button';

export function RecentProjects({
  projects = [],
  isLoading,
  onOpenProject,
  onDeleteProject,
  onNewProject,
}) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-panel rounded-2xl p-3 space-y-3">
            <Skeleton className="w-full aspect-video rounded-xl" />
            <Skeleton className="w-3/4 h-4 rounded-lg" />
            <Skeleton className="w-1/2 h-3 rounded-lg" />
          </div>
        ))}
      </div>
    );
  }

  if (!projects || projects.length === 0) {
    return (
      <EmptyState
        icon={<Sparkles className="w-8 h-8 text-brand-400" />}
        title="No designs created yet"
        description="Upload a photo of your living room, office, or exterior space and transform it with natural language AI customization."
        actionLabel="+ Create First Design"
        onAction={onNewProject}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {projects.map((project) => (
        <ProjectCard
          key={project.project_id}
          project={project}
          onOpen={onOpenProject}
          onDelete={onDeleteProject}
        />
      ))}
    </div>
  );
}

export default RecentProjects;
