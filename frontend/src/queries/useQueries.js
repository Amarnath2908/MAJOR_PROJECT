import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import projectService from '../services/projectService';
import authService from '../services/authService';
import uploadService from '../services/uploadService';
import aiService from '../services/aiService';

export const QUERY_KEYS = {
  projects: (page, pageSize) => ['projects', page, pageSize],
  project: (id) => ['project', id],
  profile: ['user_profile'],
};

// ── Project Queries ──────────────────────────────────────────────────────────
export function useProjectsQuery(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: QUERY_KEYS.projects(page, pageSize),
    queryFn: () => projectService.getHistory(page, pageSize),
    staleTime: 30000,
  });
}

export function useProjectQuery(projectId) {
  return useQuery({
    queryKey: QUERY_KEYS.project(projectId),
    queryFn: () => projectService.getProject(projectId),
    enabled: !!projectId,
    staleTime: 30000,
  });
}

export function useUserProfileQuery() {
  return useQuery({
    queryKey: QUERY_KEYS.profile,
    queryFn: () => authService.getMe(),
    staleTime: 60000,
  });
}

// ── Mutations ────────────────────────────────────────────────────────────────
export function useDeleteProjectMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectId) => projectService.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.profile });
    },
  });
}

export function useUploadMutation() {
  return useMutation({
    mutationFn: ({ file, onProgress }) => uploadService.uploadImage(file, onProgress),
  });
}

export function useAnalyzeMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ image_id, prompt, signal }) => aiService.analyzeImage({ image_id, prompt }, signal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useGenerateEditMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ image_id, prompt, project_id, target_object, signal }) =>
      aiService.generateEdit({ image_id, prompt, project_id, target_object }, signal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useApproveProjectMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId) => projectService.approveProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useMake3DMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ project_id, image_id, signal }) =>
      aiService.generate3D({ project_id, image_id }, signal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
