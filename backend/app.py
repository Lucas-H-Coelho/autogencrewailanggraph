from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import random # For more dynamic simulations

# Adicionar o diretório pai ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.autogen_engine import autogen_module
    from backend.crewai_engine import crewai_module
    # langgraph_module não é diretamente chamado aqui, mas poderia ser usado pelos engines
    ENGINES_AVAILABLE = True
except ImportError as e:
    print(f"AVISO: Não foi possível importar um ou mais módulos de IA: {e}")
    ENGINES_AVAILABLE = False

    class DummyModule:
        def run_autogen_dialogue(self, task_description):
            return f"Simulação AutoGen: Iniciando diálogo sobre '{task_description}'. Agente A diz olá. Agente B responde. Discussão concluída."

        def run_crewai_task(self, task_description):
            # Simular uma resposta mais estruturada
            return {
                "title": f"Relatório Simulado para: {task_description[:30]}...",
                "summary": f"Este é um sumário gerado pela simulação do CrewAI para a tarefa '{task_description}'. O processo envolveu análise, processamento e geração de resultados.",
                "steps": [
                    f"Passo 1: Análise inicial da tarefa '{task_description[:20]}...'",
                    "Passo 2: Coleta de dados simulada.",
                    "Passo 3: Processamento e deliberação entre agentes simulados.",
                    "Passo 4: Geração do relatório final."
                ],
                "raw": f"Dados brutos simulados: {random.randint(1000, 9999)}"
            }
    autogen_module = DummyModule()
    crewai_module = DummyModule()

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "engines_available": ENGINES_AVAILABLE}), 200

def generate_flow_update(task_description, agent_used, result):
    """Gera uma atualização de fluxo mais dinâmica para LangGraph."""
    node_count = random.randint(2, 5)
    nodes = [
        {"id": "start", "type": "input", "data": {"label": f"Tarefa: {task_description[:20]}..."}, "position": {"x": 50, "y": 50}},
    ]
    edges = []

    last_node_id = "start"
    for i in range(1, node_count + 1):
        current_node_id = f"node-{i}"
        node_label = f"Agente {agent_used} - Passo {i}" if agent_used else f"Processo {i}"
        if i == 1 and agent_used:
             node_label = f"Agente Principal: {agent_used}"

        nodes.append({
            "id": current_node_id,
            "data": {"label": node_label},
            "position": {"x": 50 + i * 150, "y": 50 + random.randint(-20, 20)}
        })
        edges.append({
            "id": f"e-{last_node_id}-{current_node_id}",
            "source": last_node_id,
            "target": current_node_id,
            "animated": True if i < node_count else False
        })
        last_node_id = current_node_id
    
    result_label = "Resultado"
    if isinstance(result, dict) and result.get("title"):
        result_label = result.get("title")[:30] + "..."
    elif isinstance(result, str):
        result_label = result[:30] + "..."

    nodes.append({
        "id": "end", "type": "output", "data": {"label": f"Final: {result_label}"}, 
        "position": {"x": 50 + (node_count + 1) * 150, "y": 50}
    })
    edges.append({
        "id": f"e-{last_node_id}-end", "source": last_node_id, "target": "end"
    })
    
    return {"nodes": nodes, "edges": edges}

@app.route('/api/run-dialogue-agent', methods=['POST'])
def handle_run_dialogue_agent():
    data = request.json
    task_description = data.get('task')
    if not task_description:
        return jsonify({"error": "Nenhuma tarefa fornecida"}), 400

    agent_to_use = "AutoGen" # Simples para este endpoint
    
    # Simulação de escolha de motor (poderia ser mais complexa)
    if ENGINES_AVAILABLE:
        # result = some_intelligent_controller_for_dialogue(task_description)
        result = autogen_module.run_autogen_dialogue(task_description)
    else:
        result = autogen_module.run_autogen_dialogue(task_description) # Usa o dummy

    flow_update = generate_flow_update(task_description, agent_to_use, result)
    
    return jsonify({
        "result": result, 
        "agent_used": agent_to_use,
        "flow_update": flow_update
    })

@app.route('/api/run-task-agent', methods=['POST'])
def handle_run_task_agent():
    data = request.json
    task_description = data.get('task')
    if not task_description:
        return jsonify({"error": "Nenhuma tarefa fornecida"}), 400

    agent_to_use = "CrewAI" # Simples para este endpoint

    if ENGINES_AVAILABLE:
        # result = some_intelligent_controller_for_task(task_description)
        result = crewai_module.run_crewai_task(task_description)
    else:
        result = crewai_module.run_crewai_task(task_description) # Usa o dummy

    flow_update = generate_flow_update(task_description, agent_to_use, result)

    return jsonify({
        "result": result, 
        "agent_used": agent_to_use,
        "flow_update": flow_update
    })

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    if not ENGINES_AVAILABLE:
        print("####################################################################")
        print("# AVISO: Motores de IA não importados. Backend em modo SIMULAÇÃO.  #")
        print("# Esperado no WebContainer. Para funcionalidade completa, use      #")
        print("# um ambiente Python dedicado com dependências instaladas.         #")
        print("####################################################################")
    app.run(debug=True, host='0.0.0.0', port=5000)
