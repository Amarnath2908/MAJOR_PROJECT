import React from 'react';
import { Box, Sparkles, Image as ImageIcon, Calendar, Trash2, ArrowUpRight } from 'lucide-react';
import Badge from '../common/Badge';
import { resolveAssetUrl } from '../../services/api';
import { formatDate } from '../../utils/formatDate';

export function ProjectCard({ project, onOpen, onDelete }) {
  const displayImage =
    resolveAssetUrl(project.edited_image) ||
    resolveAssetUrl(project.original_image) ||
    resolveAssetUrl(project.thumbnail);

  return (
    <div
      onClick={() => onOpen && onOpen(project)}
      className="group glass-panel glass-panel-hover rounded-2xl overflow-hidden cursor-pointer flex flex-col border border-slate-800 hover:border-brand-500/40 transition-all duration-200"
    >
      {/* Thumbnail Area */}
      <div className="relative aspect-video w-full bg-slate-900 overflow-hidden">
        {displayImage ? (
          <img
            src={displayImage}
            alt={project.title || 'Project preview'}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-700 bg-slate-900">
            <ImageIcon className="w-8 h-8" />
          </div>
        )}

        {/* Status Pill */}
        <div className="absolute top-2.5 right-2.5">
          <Badge status={project.status} />
        </div>

        {/* 3D Indicator */}
        {project.model_3d && (
          <div className="absolute bottom-2.5 left-2.5 px-2 py-1 rounded-lg bg-dark-900/80 backdrop-blur-md text-[10px] font-bold text-cyan-400 border border-cyan-500/40 flex items-center gap-1 shadow-md">
            <Box className="w-3 h-3" />
            <span>3D Ready</span>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-sm font-semibold text-white group-hover:text-brand-300 transition-colors truncate">
              {project.title || 'Untitled Project'}
            </h4>
            <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-brand-400 transition-colors flex-shrink-0" />
          </div>

          {project.prompt && (
            <p className="text-xs text-slate-400 italic line-clamp-1 mt-1">
              "{project.prompt}"
            </p>
          )}

          {project.target_object && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-bold text-slate-500">Target:</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-500/15 border border-brand-500/30 text-brand-300 font-medium">
                {project.target_object}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between pt-3 mt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-500" />
            {formatDate(project.created_at)}
          </span>

          {onDelete && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(project.project_id);
              }}
              className="text-slate-500 hover:text-red-400 p-1 rounded-md hover:bg-slate-800 transition-colors"
              title="Delete Project"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProjectCard;
