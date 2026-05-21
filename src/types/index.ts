export interface AgentPersona {
  agent_id: string;
  role_type: 'Tourist' | 'Local' | 'Expat';
  nationality: string;
  language_style: string;
  avatar_url: string;
}

export interface InteractionNode {
  node_id: string;
  parent_id: string | null;
  agent: AgentPersona;
  content: string;
  thinking_process?: string;
  timestamp: string;
}

export interface MetadataAndEval {
  sentiment: 'positive' | 'neutral' | 'negative' | 'anxious';
  intent: string;
  tags: string[];
  scores: {
    human_likeness: number;
    coherence: number;
    cultural_fit: number;
  };
  is_passed: boolean;
  feedback?: string;
}

export interface CommunityTopicPayload {
  topic_id: string;
  scenario: string;
  location: string;
  nodes: InteractionNode[];
  status: 'generating' | 'passed' | 'failed' | 'annotated';
  evaluation: MetadataAndEval;
}
