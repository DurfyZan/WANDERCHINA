import { useState, useEffect, useCallback } from 'react'
import type { CommunityTopicPayload, InteractionNode, AgentPersona } from '@/types'

const mockAgents: Record<string, AgentPersona> = {
  tourist: {
    agent_id: 'agent-tourist-001',
    role_type: 'Tourist',
    nationality: '美国',
    language_style: 'Casual',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=TouristJohn',
  },
  local: {
    agent_id: 'agent-local-001',
    role_type: 'Local',
    nationality: '中国',
    language_style: '网络用语',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=LocalZhang',
  },
  expat: {
    agent_id: 'agent-expat-001',
    role_type: 'Expat',
    nationality: '英国',
    language_style: 'Academic',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=ExpatDavid',
  },
}

const mockMainPost: InteractionNode = {
  node_id: 'node-001',
  parent_id: null,
  agent: mockAgents.tourist,
  content: 'Hey everyone! I just arrived in Beijing and tried to buy some souvenirs at the Palace Museum. The vendor only accepts WeChat Pay, but I don\'t have a Chinese bank account. 😟 Any suggestions?',
  timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
}

const mockComments: InteractionNode[] = [
  {
    node_id: 'node-002',
    parent_id: 'node-001',
    agent: mockAgents.local,
    content: '老哥别慌！这个很简单，你可以去便利店买点东西用现金，然后让店员帮你充到微信里。或者直接下载一个WeChat，绑定境外银行卡就能用了！现在老外都能用境外信用卡绑WeChat Pay了，超方便的！✨',
    timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
  },
  {
    node_id: 'node-003',
    parent_id: 'node-002',
    agent: mockAgents.tourist,
    content: 'Thank you so much! I\'ll try that right away. By the way, do I need to learn Chinese characters to use the app?',
    timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
  },
  {
    node_id: 'node-004',
    parent_id: 'node-002',
    agent: mockAgents.expat,
    content: 'I\'ve been living here for 2 years. Pro tip: Download the English version of WeChat and enable translation features. Most young vendors can communicate in basic English. The key is to have Alipay or WeChat Pay - cash is becoming increasingly rare in big cities.',
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
  },
  {
    node_id: 'node-005',
    parent_id: 'node-004',
    agent: mockAgents.local,
    content: '说得对！现在北京上海都普及移动支付了，连煎饼摊都能扫码。外国人来了建议先弄个支付宝国际版，绑定境外卡就能用，跟用信用卡一样方便。再不行就去找银行问问，有些银行有专门的境外游客支付服务～',
    timestamp: new Date(Date.now() - 1000 * 60 * 1).toISOString(),
  },
]

const mockEvaluation = {
  sentiment: 'positive' as const,
  intent: 'seeking-help',
  tags: ['payment', 'wechat', 'beijing', 'tourist'],
  scores: {
    human_likeness: 4.5,
    coherence: 4.8,
    cultural_fit: 4.7,
  },
  is_passed: true,
}

interface StreamingState {
  isLoading: boolean
  content: string
  thinkingProcess: string
  status: 'idle' | 'loading' | 'completed'
}

export function useCommunityData() {
  const [mainPost, setMainPost] = useState<InteractionNode | null>(null)
  const [comments, setComments] = useState<InteractionNode[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isLoading: false,
    content: '',
    thinkingProcess: '',
    status: 'idle',
  })
  const [topicPayload, setTopicPayload] = useState<CommunityTopicPayload | null>(null)

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const simulateSSEStream = useCallback(async (
    text: string,
    onChunk: (chunk: string) => void
  ) => {
    const words = text.split(' ')
    for (let i = 0; i < words.length; i++) {
      await delay(50 + Math.random() * 100)
      onChunk(words[i] + (i < words.length - 1 ? ' ' : ''))
    }
  }, [])

  const startGeneration = useCallback(async () => {
    setIsStreaming(true)
    setMainPost(null)
    setComments([])
    setTopicPayload(null)

    setStreamingState({
      isLoading: true,
      content: '',
      thinkingProcess: '',
      status: 'loading',
    })

    const thinkingContent = `
<think>
The tourist is asking about payment difficulties in Beijing. They're unfamiliar with Chinese mobile payment systems. As a helpful local, I should:

1. Understand their problem - they can't use WeChat Pay without a Chinese bank account
2. Provide practical solutions that are commonly used by foreigners
3. Keep the response natural and in line with how Chinese people actually communicate online
4. Use popular Chinese internet slang and expressions to make it more authentic

Key solutions to suggest:
- Use Alipay's international version (支持绑定境外信用卡)
- Find convenience stores that can help reload WeChat
- Use cash and exchange at the airport/bank
- Some vendors accept foreign cards now

Let me craft a response that sounds natural and helpful.
</think>
    `

    await delay(500)

    const thinkingLines = thinkingContent.trim().split('\n')
    let thinkingResult = ''
    for (const line of thinkingLines) {
      await delay(30 + Math.random() * 50)
      thinkingResult += line + '\n'
      setStreamingState(prev => ({
        ...prev,
        thinkingProcess: thinkingResult,
      }))
    }

    await delay(300)

    const fullContent = mockMainPost.content
    let streamedContent = ''
    const words = fullContent.split(' ')
    for (let i = 0; i < words.length; i++) {
      await delay(40 + Math.random() * 80)
      streamedContent += words[i] + (i < words.length - 1 ? ' ' : '')
      setStreamingState(prev => ({
        ...prev,
        content: streamedContent,
      }))
    }

    await delay(500)

    // 保存最终的主贴内容
    const finalMainPost: InteractionNode = {
      ...mockMainPost,
      content: streamedContent,
      thinking_process: thinkingResult,
    }
    setMainPost(finalMainPost)

    await delay(1000)

    // 逐个生成评论
    for (let commentIndex = 0; commentIndex < mockComments.length; commentIndex++) {
      const comment = mockComments[commentIndex]
      
      await delay(800)

      // 流式生成评论内容
      let commentContent = ''
      const commentChars = comment.content.split('')
      for (let charIndex = 0; charIndex < commentChars.length; charIndex++) {
        await delay(20 + Math.random() * 40)
        commentContent += commentChars[charIndex]
        
        setComments(prev => {
          // 查找是否已有这条评论
          const existingIndex = prev.findIndex(c => c.node_id === comment.node_id)
          
          if (existingIndex >= 0) {
            // 更新已存在的评论
            const newComments = [...prev]
            newComments[existingIndex] = {
              ...newComments[existingIndex],
              content: commentContent
            }
            return newComments
          } else {
            // 添加新评论
            return [...prev, {
              ...comment,
              content: commentContent
            }]
          }
        })
      }

      await delay(500)

      // 第一个评论添加思考过程
      if (commentIndex === 0) {
        const commentThinking = `
<think>
The tourist needs help with payment. Let me provide practical advice using common Chinese expressions and slang.
</think>
        `
        let cThinking = ''
        const commentThinkingLines = commentThinking.trim().split('\n')
        
        for (let lineIndex = 0; lineIndex < commentThinkingLines.length; lineIndex++) {
          await delay(30 + Math.random() * 50)
          cThinking += commentThinkingLines[lineIndex] + '\n'
          
          setComments(prev => {
            return prev.map(c => {
              if (c.node_id === comment.node_id) {
                return {
                  ...c,
                  thinking_process: cThinking
                }
              }
              return c
            })
          })
        }
      }
    }

    // 设置最终的topicPayload
    setTopicPayload({
      topic_id: 'topic-' + Date.now(),
      scenario: '景区支付困难',
      location: '北京故宫',
      nodes: [finalMainPost, ...mockComments],
      status: 'annotated',
      evaluation: mockEvaluation,
    })

    setStreamingState({
      isLoading: false,
      content: '',
      thinkingProcess: '',
      status: 'completed',
    })

    setIsStreaming(false)
  }, [])

  useEffect(() => {
    if (isStreaming && streamingState.status === 'loading') {
      setTopicPayload({
        topic_id: 'topic-generating-' + Date.now(),
        scenario: '景区支付困难',
        location: '北京故宫',
        nodes: [],
        status: 'generating',
        evaluation: {
          sentiment: 'neutral',
          intent: 'seeking-help',
          tags: [],
          scores: {
            human_likeness: 0,
            coherence: 0,
            cultural_fit: 0,
          },
          is_passed: false,
        },
      })
    }
  }, [isStreaming, streamingState.status])

  return {
    mainPost,
    comments,
    isStreaming,
    streamingState,
    topicPayload,
    startGeneration,
  }
}
