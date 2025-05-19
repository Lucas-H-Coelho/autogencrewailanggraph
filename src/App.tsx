import React, { useState, useCallback, useEffect } from 'axios';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, Bot, Brain, MessageSquare, Play, Send, Share2, Zap } from 'lucide-react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

type Mode = "dialogue" | "execution";

interface Message {
  id: string;
  sender: "user" | "bot" | "agent";
  content: string;
  type: "text" | "error" | "info";
  agentName?: string;
}

const initialNodes: Node[] = [
  { id: '1', type: 'input', data: { label: 'Início do Fluxo' }, position: { x: 250, y: 5 } },
];

const initialEdges: Edge[] = [];

function App() {
  const [mode, setMode] = useState<Mode>("dialogue");
  const [inputValue, setInputValue] = useState("");
  const [history, setHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addMessageToHistory = (sender: Message["sender"], content: string, type: Message["type"] = "text", agentName?: string) => {
    setHistory(prev => [...prev, { id: Date.now().toString(), sender, content, type, agentName }]);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = async () => {
    if (!inputValue.trim()) return;
    const currentInput = inputValue;
    addMessageToHistory("user", currentInput);
    setInputValue("");
    setIsLoading(true);

    try {
      let response;
      if (mode === "dialogue") {
        addMessageToHistory("info", "Enviando para AutoGen (Modo Diálogo)...");
        response = await axios.post('/api/run-dialogue-agent', { task: currentInput });
      } else {
        addMessageToHistory("info", "Enviando para CrewAI (Modo Execução)...");
        response = await axios.post('/api/run-task-agent', { task: currentInput });
      }
      
      // Simulação de resposta do backend
      // No backend real, você processaria a resposta e talvez atualizaria os nós/arestas do LangGraph
      if (response.data && response.data.result) {
        addMessageToHistory("bot", response.data.result, "text", response.data.agent_used);
        if (response.data.flow_update) {
          // Exemplo: { nodes: [...], edges: [...] }
          // setNodes(response.data.flow_update.nodes);
          // setEdges(response.data.flow_update.edges);
          addMessageToHistory("info", "Fluxo LangGraph atualizado (simulado).");
        }
      } else {
        addMessageToHistory("bot", "Resposta vazia do servidor.", "error");
      }

    } catch (error) {
      console.error("Erro ao comunicar com o backend:", error);
      let errorMessage = "Erro ao processar a solicitação.";
      if (axios.isAxiosError(error) && error.response) {
        errorMessage = `Erro do servidor: ${error.response.status} - ${error.response.data.error || error.message}`;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      addMessageToHistory("bot", errorMessage, "error");
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    // Adiciona uma mensagem de aviso sobre as limitações do Python no WebContainer
    addMessageToHistory("info", "Aviso: O backend Python (Flask e bibliotecas de IA) pode não funcionar corretamente no ambiente WebContainer devido a limitações. Para funcionalidade completa, execute o backend em um ambiente Python dedicado.", "info");
  }, []);


  return (
    <div className="flex flex-col h-screen bg-background text-foreground p-4 font-sans">
      <header className="mb-4">
        <h1 className="text-3xl font-bold text-primary flex items-center">
          <Brain className="mr-2 h-8 w-8" /> Plataforma Híbrida de Agentes Autônomos
        </h1>
        <p className="text-muted-foreground">Unificando AutoGen, CrewAI e LangGraph</p>
      </header>

      <ResizablePanelGroup direction="vertical" className="flex-grow rounded-lg border border-border shadow-lg">
        <ResizablePanel defaultSize={70}>
          <ResizablePanelGroup direction="horizontal" className="h-full">
            <ResizablePanel defaultSize={50}>
              <Card className="h-full flex flex-col rounded-r-none border-r-0">
                <CardHeader className="border-b border-border">
                  <CardTitle className="flex items-center text-primary">
                    <Bot className="mr-2" /> Interação com Agentes
                  </CardTitle>
                  <CardDescription>
                    Escolha o modo de interação e envie sua tarefa.
                  </CardDescription>
                  <Tabs value={mode} onValueChange={(value) => setMode(value as Mode)} className="mt-2">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="dialogue" className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" /> Modo Diálogo (AutoGen)
                      </TabsTrigger>
                      <TabsTrigger value="execution" className="flex items-center gap-1">
                        <Zap className="h-4 w-4" /> Modo Execução (CrewAI)
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                </CardHeader>
                <CardContent className="flex-grow flex flex-col p-0">
                  <ScrollArea className="flex-grow p-4 space-y-4">
                    {history.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[70%] p-3 rounded-lg shadow ${
                            msg.sender === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : msg.type === 'error'
                              ? 'bg-destructive text-destructive-foreground'
                              : msg.type === 'info'
                              ? 'bg-accent/50 text-accent-foreground w-full text-sm'
                              : 'bg-secondary text-secondary-foreground'
                          }`}
                        >
                          {msg.agentName && <p className="text-xs font-semibold mb-1 opacity-80">{msg.agentName}</p>}
                          <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                      </div>
                    ))}
                     {isLoading && (
                        <div className="flex justify-start">
                            <div className="max-w-[70%] p-3 rounded-lg shadow bg-muted text-muted-foreground">
                                <p>Processando...</p>
                            </div>
                        </div>
                    )}
                  </ScrollArea>
                  <div className="p-4 border-t border-border">
                    <div className="flex gap-2">
                      <Textarea
                        value={inputValue}
                        onChange={handleInputChange}
                        placeholder={mode === "dialogue" ? "Digite sua mensagem para o diálogo..." : "Descreva a tarefa para execução..."}
                        className="flex-grow resize-none"
                        rows={2}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit();
                          }
                        }}
                        disabled={isLoading}
                      />
                      <Button onClick={handleSubmit} disabled={isLoading || !inputValue.trim()} className="h-auto px-4 py-2 self-end bg-accent hover:bg-accent/80 text-accent-foreground">
                        <Send className="h-5 w-5 mr-2" /> Enviar
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={50}>
              <Card className="h-full flex flex-col rounded-l-none">
                <CardHeader className="border-b border-border">
                  <CardTitle className="flex items-center text-primary">
                    <Play className="mr-2" /> Painel de Execução / Detalhes
                  </CardTitle>
                  <CardDescription>
                    Resultados detalhados e feedback do modo de execução (CrewAI).
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-grow p-4">
                  <ScrollArea className="h-full">
                    <p className="text-muted-foreground">
                      {mode === "execution" 
                        ? "Os resultados detalhados da execução do CrewAI aparecerão aqui."
                        : "Este painel mostrará detalhes adicionais ou saídas de agentes."}
                    </p>
                    {/* Conteúdo do painel de execução virá aqui */}
                  </ScrollArea>
                </CardContent>
              </Card>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={30}>
          <Card className="h-full flex flex-col rounded-t-none border-t-0">
            <CardHeader className="border-b border-border">
              <CardTitle className="flex items-center text-primary">
                <Share2 className="mr-2" /> Visualização de Fluxos (LangGraph)
              </CardTitle>
              <CardDescription>
                Acompanhe o fluxo de decisão e execução dos agentes.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-grow p-0 relative">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
                className="bg-card"
              >
                <Controls />
                <MiniMap nodeStrokeWidth={3} zoomable pannable />
                <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="hsl(var(--border))" />
              </ReactFlow>
               <div className="absolute bottom-2 right-2 bg-background/80 p-2 rounded text-xs text-muted-foreground">
                Visualização do LangGraph (Simulada)
              </div>
            </CardContent>
          </Card>
        </ResizablePanel>
      </ResizablePanelGroup>
      
      <footer className="mt-4 text-center text-sm text-muted-foreground">
        <p>
          <AlertCircle className="inline h-4 w-4 mr-1" />
          Lembre-se das limitações do Python no WebContainer. Para uma experiência completa, execute o backend em um ambiente Python dedicado.
        </p>
      </footer>
    </div>
  );
}

export default App;
