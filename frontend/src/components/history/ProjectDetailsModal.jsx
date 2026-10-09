import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Sparkles, Trash2, Calendar, ZoomIn, ArrowRight } from 'lucide-react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import Badge from '../common/Badge';
import { resolveAssetUrl } from '../../services/api';
import { formatDate } from '../../utils/formatDate';
import useStudioStore from '../../store/studioStore';

export function ProjectDetailsModal({
  project,
  isOpen,
  onClose,
  onDelete,
}) {
  const navigate = useNavigate();
  const { setUploadedImage, setEditResult, set3DResult } = useStudioStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!project) return null;

  const originalUrl = resolveAssetUrl(project.original_image);
  const editedUrl = resolveAssetUrl(project.edited_image);
  const modelUrl = resolveAssetUrl(project.model_3d);

  const handleContinueEditing = () => {
    // Load project into studio store
    setUploadedImage({
      imageId: project.image_id || null,
      imageUrl: project.original_image,
      fileName: project.title,
    });

    if (editedUrl) {
      setEditResult({
        projectId: project.project_id,
        editedImage: project.edited_image,
        prompt: project.prompt || '',
        targetObject: project.target_object || null,
      });
    }

    if (modelUrl) {
      set3DResult({ modelUrl: project.model_3d });
    }

    onClose();
    navigate('/studio');
  };

  const handleView3D = () => {
    if (project.model_3d) {
      set3DResult({ modelUrl: project.model_3d });
      onClose();
      navigate('/viewer');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={project.title || 'Project Details'} maxWidth="max-w-2xl">
      <div className="flex flex-col gap-5">
        {/* Images comparison or previews */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {originalUrl && (
            <div className="flex flex-col gap-1.5">
              <span className="text-xs font-semibold text-slate-400">Original Space</span>
              <div className="relative aspect-video rounded-xl overflow-hidden border border-slate-800 bg-slate-900">
                <img src={originalUrl} alt="Original space" className="w-full h-full object-cover" />
              </div>
            </div>
          )}

          {editedUrl && (
            <div className="flex flex-col gap-1.5">
              <span className="text-xs font-semibold text-brand-300">AI Customized Space</span>
              <div className="relative aspect-video rounded-xl overflow-hidden border border-brand-500/30 bg-slate-900">
                <img src={editedUrl} alt="AI edited space" className="w-full h-full object-cover" />
              </div>
            </div>
          )}
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs">
          <div>
            <span className="text-slate-500 block">Status</span>
            <div className="mt-1">
              <Badge status={project.status} />
            </div>
          </div>

          <div>
            <span className="text-slate-500 block">Created</span>
            <span className="text-slate-200 mt-1 block font-medium">
              {formatDate(project.created_at)}
            </span>
          </div>

          <div>
            <span className="text-slate-500 block">3D Model</span>
            <span className="text-slate-200 mt-1 block font-medium">
              {project.model_3d ? 'Available (.GLB)' : 'Not generated'}
            </span>
          </div>

          {project.target_object && (
            <div>
              <span className="text-slate-500 block">Target Object</span>
              <span className="text-brand-300 mt-1 block font-semibold">
                {project.target_object}
              </span>
            </div>
          )}
        </div>

        {/* Prompt note */}
        {project.prompt && (
          <div className="p-3 bg-dark-900 rounded-xl border border-slate-800 text-xs text-slate-300">
            <span className="text-slate-500 block text-[11px] uppercase tracking-wider mb-1">
              Natural Language Prompt
            </span>
            <p className="italic font-medium text-white">"{project.prompt}"</p>
          </div>
        )}

        {/* Actions bar */}
        <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
          {showDeleteConfirm ? (
            <div className="flex items-center gap-2 bg-red-950/40 p-2 rounded-xl border border-red-800/60">
              <span className="text-xs text-red-300">Delete this design?</span>
              <button
                type="button"
                onClick={() => {
                  onDelete(project.project_id);
                  onClose();
                }}
                className="px-2.5 py-1 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-semibold cursor-pointer"
              >
                Confirm
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(false)}
                className="px-2 py-1 text-slate-400 hover:text-white text-xs cursor-pointer"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-red-400 py-2 px-3 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete Design</span>
            </button>
          )}

          <div className="flex items-center gap-2">
            {project.model_3d && (
              <Button
                variant="cyan"
                size="sm"
                onClick={handleView3D}
                leftIcon={<Box className="w-4 h-4" />}
              >
                View 3D Model
              </Button>
            )}

            <Button
              size="sm"
              onClick={handleContinueEditing}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Open in Studio
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}

export default ProjectDetailsModal;
