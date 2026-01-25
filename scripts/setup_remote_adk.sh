#!/bin/bash

# ==============================================================================
# SETUP DO SERVIDOR REMOTO ADK (Agente Rust Expert)
# ==============================================================================

SERVER_DIR="$HOME/adk-remote-server"
VENV_DIR="$SERVER_DIR/venv"
PORT=8000

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}>>> Iniciando configuracao do Servidor ADK Remoto...${NC}"

# 1. Preparar Diretorios
mkdir -p "$SERVER_DIR/agents"
cd "$SERVER_DIR"

# 2. Configurar Python e Venv
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: python3 nao encontrado. Instale: sudo apt install python3 python3-venv${NC}"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}Criando virtualenv...${NC}"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 3. Instalar Dependencias
echo -e "${GREEN}Instalando dependencias (isso pode demorar um pouco)...${NC}"
pip install --upgrade pip
pip install google-adk google-genai fastapi uvicorn python-dotenv

# 4. Criar o Codigo do Agente (Rust Expert)
echo -e "${GREEN}Criando codigo do Agente (agents/rust_expert.py)...${NC}"
cat << 'EOF' > agents/rust_expert.py
import os
from google.adk.agents import Agent
from google.adk.tools import google_search

# Instrucao especializada para o Rust Expert
RUST_EXPERT_INSTRUCTION = """
Você é um Engenheiro de Software Sênior especializado em Rust e na arquitetura do Tauri 2.x.
Sua missão é escrever código Rust idiomático (ferris-approved) e realizar revisões técnicas rigorosas.

DIRETRIZES DE CODIFICAÇÃO:
1.  **Segurança e Performance**: Sempre priorize 'safety' e 'performance'. Evite 'unsafe' a menos que seja estritamente necessário.
2.  **Idiomatismo**: Use padrões como 'Newtype', 'RAII', e 'Traits' de forma eficiente.
3.  **Tauri Integration**: Foque em comandos Tauri seguros, gerenciamento de estado (State) e IPC eficiente.
4.  **Error Handling**: Nunca use 'unwrap()' em código de produção. Sempre use 'Result' e 'Option' com tratamento de erro claro.
5.  **Documentação**: Escreva Doc-comments (///) para funções públicas.

Ao revisar ou escrever, sempre considere o ecossistema atual do projeto (Tauri 2.x, Rust 1.80+).
"""

def create_agent():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("WARN: GOOGLE_API_KEY not set")
    
    return Agent(
        name="rust_expert_agent",
        model="gemini-2.0-flash-exp",
        instruction=RUST_EXPERT_INSTRUCTION,
        tools=[google_search]
    )
EOF

# 5. Criar o Servidor Web (FastAPI)
echo -e "${GREEN}Criando servidor web (server.py)...${NC}"
cat << 'EOF' > server.py
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Importar agentes
from agents.rust_expert import create_agent

load_dotenv()

app = FastAPI(title="ADK Remote Server")

# Inicializar agentes
agents = {
    "rust_expert_agent": create_agent()
}

class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class AgentInfo(BaseModel):
    name: str
    description: str

@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    return [
        AgentInfo(name=name, description=agent.description or "No description")
        for name, agent in agents.items()
    ]

@app.post("/agents/{agent_name}/chat")
async def chat(agent_name: str, req: MessageRequest):
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    
    # Simples wrapper para execucao sincrona do agente (para demo)
    # Em producao, idealmente usar Runner assincrono mantendo estado
    try:
        # Nota: ADK Agent.run() retorna um gerador ou resposta direta dependendo da versao
        # Aqui simplificamos pegando a resposta direta
        response_text = ""
        # ADK 0.1.x padrao:
        # result = agent.run(req.message) 
        # Adaptando para garantir compatibilidade basica:
        from google.genai import types
        content = types.Content(role="user", parts=[types.Part(text=req.message)])
        
        # Hack rapido para usar o agente sem Runner complexo para este teste
        # Idealmente: Implementar SessionService
        response = agent.model_client.models.generate_content(
            model=agent.model,
            contents=[content],
            config=agent.genai_config
        )
        return {"response": response.text}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# 6. Criar Script de Inicializacao
echo -e "${GREEN}Criando script de inicializacao (start.sh)...${NC}"
cat << 'EOF' > start.sh
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f .env ]; then
        source .env
    else
        echo "Erro: GOOGLE_API_KEY nao configurada. Crie um arquivo .env ou exporte a variavel."
        exit 1
    fi
fi

echo "Iniciando servidor ADK na porta 8000..."
nohup python3 server.py > server.log 2>&1 &
echo "Servidor rodando! PID: $!"
echo "Logs em: server.log"
EOF

chmod +x start.sh

# 7. Setup Final (.env)
if [ ! -f .env ]; then
    echo -e "${BLUE}"
    echo "Configuracao quase pronta!"
    echo "Por favor, insira sua GOOGLE_API_KEY para salvar no arquivo .env:"
    read -p "API Key: " USER_KEY
    echo "GOOGLE_API_KEY=$USER_KEY" > .env
    echo -e "${NC}"
fi

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}SETUP CONCLUIDO!${NC}"
echo -e "Para iniciar o servidor, execute:"
echo -e "${BLUE}cd $SERVER_DIR && ./start.sh${NC}"
echo -e "${GREEN}======================================================${NC}"
