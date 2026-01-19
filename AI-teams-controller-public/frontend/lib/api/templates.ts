/**
 * Template API Client
 *
 * Fetches templates from backend API.
 */

import { getAuthHeaders } from '../auth-utils';
import { tryRefreshTokens } from '../auth';

// Types matching backend schemas
export interface TemplateRole {
  id: string;
  name: string;
  description: string;
  optional: boolean;
}

export interface TeamTemplate {
  name: string;
  display_name: string;
  description: string;
  version: string;
  roles: TemplateRole[];
}

export interface TemplatesResponse {
  templates: TeamTemplate[];
}

export interface CreateTeamRequest {
  template_name: string;
  project_name: string;
  prd: string;
}

export interface CreateTeamResponse {
  success: boolean;
  team_id: string;
  message: string;
  output_dir: string;
}

/**
 * Fetch all available templates from backend
 */
export async function fetchTemplates(): Promise<TeamTemplate[]> {
  let response = await fetch('/api/templates', {
    headers: getAuthHeaders(),
  });

  // Handle 401: try refresh tokens and retry once
  if (response.status === 401) {
    const refreshed = await tryRefreshTokens();
    if (refreshed) {
      response = await fetch('/api/templates', {
        headers: getAuthHeaders(),
      });
    } else {
      throw new Error('Authentication required');
    }
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch templates: ${response.statusText}`);
  }

  const data: TemplatesResponse = await response.json();
  return data.templates;
}

/**
 * Create a new team from template
 */
export async function createTeam(request: CreateTeamRequest): Promise<CreateTeamResponse> {
  let response = await fetch('/api/templates/create', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  // Handle 401: try refresh tokens and retry once
  if (response.status === 401) {
    const refreshed = await tryRefreshTokens();
    if (refreshed) {
      response = await fetch('/api/templates/create', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(request),
      });
    } else {
      throw new Error('Authentication required');
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Failed to create team: ${response.statusText}`);
  }

  return response.json();
}
