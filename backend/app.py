from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Adicionar o diretório pai ao sys.path para permitir importações relativas
# Isso é útil se você estiver executando o app.py diretamente de dentro da pasta backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tentar importar os módulos. Se falhar, imprimir um aviso.
# No WebContainer, esses imports provavelmente falharão devido às restrições.
try:
    from backend.autogen_engine import autogen_module
    from backend.crewai_engine import crewai_module
    from backend.langgraph_engine import langgraph_module
    ENGINES_AVAILABLE = True
except ImportError as e:
    print(f"AVISO: Não foi possível importar um ou mais módulos de IA: {e}")
    print("As funcionalidades do backend relacionadas a esses módulos estarão desabilitadas.")
    print("Isso é esperado no ambiente WebContainer devido à restrição à biblioteca padrão do Python.")
    ENGINES_AVAILABLE = False

    # Criar módulos dummy se a importação falhar
    class DummyModule:
        def run_autogen_dialogue(self, task_description):
            return "Funcionalidade AutoGen não disponível no ambiente atual."

        def run_crewai_task(self, task_description):
            return "Funcionalidade CrewAI não disponível no ambiente atual."

        def get_langgraph_visualization(self, task_id):
            return {"nodes": [{"id": "error", "data": {"label": "LangGraph não disponível"}}], "edges": []}

    autogen_module = DummyModule()
    crewai_module = DummyModule()
    langgraph_module = DummyModule()


app = Flask(__name__)
CORS(app) # Habilitar CORS para todas as rotas

# Endpoint para verificar a saúde da API
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "engines_available": ENGINES_AVAILABLE}), 200

@app.route('/api/run-dialogue-agent', methods=['POST'])
def run_dialogue_agent():
    data = request.json
    task_description = data.get('task')

    if not task_description:
        return jsonify({"error": "Nenhuma tarefa fornecida"}), 400

    # Lógica do controlador inteligente (simplificada)
    if "discutir" in task_description.lower() or "ideia" in task_description.lower() or "conversa" in task_description.lower():
        # Usar AutoGen
        if ENGINES_AVAILABLE:
            result = autogen_module.run_autogen_dialogue(task_description)
        else:
            result = "Motor AutoGen não disponível. Simulação: AutoGen processaria: " + task_description
        agent_used = "AutoGen"
    else:
        # Por padrão, ou se não for claramente diálogo, tentar CrewAI (ou simular)
        if ENGINES_AVAILABLE:
            result = crewai_module.run_crewai_task(task_description)
        else:
            result = "Motor CrewAI não disponível. Simulação: CrewAI executaria: " + task_description
        agent_used = "CrewAI (Fallback)"


    # Simulação de atualização do LangGraph
    # Em um cenário real, isso seria mais complexo e baseado no resultado da tarefa
    flow_update = {
        "nodes": [
            {"id": "1", "type": "input", "data": {"label": "Início: " + task_description[:20] + "..."}, "position": {"x": 50, "y": 5}},
            {"id": "2", "data": {"label": f"Agente: {agent_used}"}, "position": {"x": 50, "y": 100}},
            {"id": "3", "type": "output", "data": {"label": "Resultado: " + result[:20] + "..."}, "position": {"x": 50, "y": 200}}
        ],
        "edges": [
            {"id": "e1-2", "source": "1", "target": "2", "animated": True},
            {"id": "e2-3", "source": "2", "target": "3"}
        ]
    }
    
    return jsonify({
        "result": result, 
        "agent_used": agent_used,
        "flow_update": flow_update # Dados para LangGraph
    })

@app.route('/api/run-task-agent', methods=['POST'])
def run_task_agent():
    data = request.json
    task_description = data.get('task')

    if not task_description:
        return jsonify({"error": "Nenhuma tarefa fornecida"}), 400

    # Lógica do controlador inteligente (simplificada)
    if "discutir" in task_description.lower() or "ideia" in task_description.lower() or "conversa" in task_description.lower():
        # Usar AutoGen
        if ENGINES_AVAILABLE:
            result = autogen_module.run_autogen_dialogue(task_description)
        else:
            result = "Motor AutoGen não disponível. Simulação: AutoGen processaria: " + task_description
        agent_used = "AutoGen (Fallback)"
    else:
        # Usar CrewAI
        if ENGINES_AVAILABLE:
            result = crewai_module.run_crewai_task(task_description)
        else:
            result = "Motor CrewAI não disponível. Simulação: CrewAI executaria: " + task_description
        agent_used = "CrewAI"

    # Simulação de atualização do LangGraph
    flow_update = {
        "nodes": [
            {"id": "task1", "type": "input", "data": {"label": "Tarefa: " + task_description[:20] + "..."}, "position": {"x": 50, "y": 5}},
            {"id": "task2", "data": {"label": f"Agente: {agent_used}"}, "position": {"x": 50, "y": 100}},
            {"id": "task3", "type": "output", "data": {"label": "Resultado: " + result[:20] + "..."}, "position": {"x": 50, "y": 200}}
        ],
        "edges": [
            {"id": "etask1-2", "source": "task1", "target": "task2", "animated": True},
            {"id": "etask2-3", "source": "task2", "target": "task3"}
        ]
    }

    return jsonify({
        "result": result, 
        "agent_used": agent_used,
        "flow_update": flow_update
    })

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    if not ENGINES_AVAILABLE:
        print("####################################################################")
        print("# AVISO IMPORTANTE:                                                #")
        print("# Os motores de IA (AutoGen, CrewAI, LangGraph) não puderam ser    #")
        print("# importados. O backend funcionará em modo de simulação.           #")
        print("# Isso é esperado no WebContainer devido às suas limitações.       #")
        print("# Para funcionalidade completa, execute em um ambiente Python      #")
        print("# com as dependências instaladas.                                  #")
        print("####################################################################")
    app.run(debug=True, host='0.0.0.0', port=5000)
