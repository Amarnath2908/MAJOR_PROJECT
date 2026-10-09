import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, PlusCircle, Layers, Wand2, Box, History } from 'lucide-react';
import useAuthStore from '../store/authStore';
import useStudioStore from '../store/studioStore';
import { useProjectsQuery, useUserProfileQuery, useDeleteProjectMutation } from '../queries/useQueries';
import StatsCard from '../components/dashboard/StatsCard';
import RecentProjects from '../components/dashboard/RecentProjects';
import ProjectDetailsModal from '../components/history/ProjectDetailsModal';
import Button from '../components/common/Button';

export function Dashboard() {
  const { user } = useAuthStore();
  const { startNewProject } = useStudioStore();
  const navigate = useNavigate();

  const [selectedProject, setSelectedProject] = useState(null);

  // Server state queries
  const { data: profileData } = useUserProfileQuery();
  const { data: historyData, isLoading: isHistoryLoading } = useProjectsQuery(1, 6);
  const deleteMutation = useDeleteProjectMutation();

  const projects = historyData?.projects || [];
  const totalProjects = profileData?.total_projects ?? historyData?.total ?? 0;

  // Calculate stats from actual project list
  const aiEditsCount = projects.filter((p) => p.edited_image || p.status === 'edited' || p.status === 'model_ready').length;
  const models3dCount = projects.filter((p) => p.model_3d || p.status === 'model_ready').length;

  const handleCreateNew = () => {
    startNewProject();
    navigate('/studio');
  };

  const handleDelete = (projectId) => {
    deleteMutation.mutate(projectId);
  };

  return (
    <div className="p-6 sm:p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Welcome & Quick Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Welcome back,{' '}
            <span className="bg-gradient-to-r from-brand-400 to-cyan-400 bg-clip-text text-transparent">
              {profileData?.full_name || user?.username || 'Designer'}
            </span>
            !
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage your room customizations and generate 3D spatial models.
          </p>
        </div>

        <Button
          onClick={handleCreateNew}
          size="lg"
          leftIcon={<PlusCircle className="w-5 h-5" />}
          className="shadow-glow"
        >
          + Create New Design
        </Button>
      </div>

      {/* Stats Metric Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <StatsCard
          title="Total Designs"
          value={totalProjects}
          icon={<Layers className="w-6 h-6" />}
          subtitle="Saved space projects"
        />
        <StatsCard
          title="AI Image Edits"
          value={aiEditsCount}
          icon={<Wand2 className="w-6 h-6 text-brand-400" />}
          subtitle="Prompt-customized scenes"
        />
        <StatsCard
          title="3D Spatial Models"
          value={models3dCount}
          icon={<Box className="w-6 h-6 text-cyan-400" />}
          subtitle="Ready in Interactive Viewer"
        />
      </div>

      {/* Recent Projects Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            Recent Designs
          </h2>

          {projects.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/history')}
              rightIcon={<History className="w-3.5 h-3.5" />}
            >
              View All History
            </Button>
          )}
        </div>

        <RecentProjects
          projects={projects}
          isLoading={isHistoryLoading}
          onOpenProject={(project) => setSelectedProject(project)}
          onDeleteProject={handleDelete}
          onNewProject={handleCreateNew}
        />
      </div>

      {/* Project Details Modal */}
      <ProjectDetailsModal
        project={selectedProject}
        isOpen={!!selectedProject}
        onClose={() => setSelectedProject(null)}
        onDelete={handleDelete}
      />
    </div>
  );
}

export default Dashboard;
