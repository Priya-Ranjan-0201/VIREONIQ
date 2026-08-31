import api from '../lib/axios';

export interface CodeExecutionRequest {
  source_code: string;
  language_id: number;
  stdin?: string;
}

export interface CodeExecutionResponse {
  stdout: string | null;
  stderr: string | null;
  compile_output: string | null;
  time: string | null;
  memory: number | null;
  status: {
    id: number;
    description: string;
  };
}

export const codeApi = {
  executeCode: async (data: CodeExecutionRequest): Promise<CodeExecutionResponse> => {
    const response = await api.post('/code/execute', data);
    return response.data;
  },

  getLanguages: async () => {
    const response = await api.get('/code/languages');
    return response.data;
  }
};
