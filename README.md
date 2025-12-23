# Transcrição e Análise de Aulas - Hackathon IF

Este projeto automatiza o fluxo de captura de áudio, transcrição e geração de inteligência pedagógica. Ele foi desenvolvido com foco em **Eficiência de Processos Acadêmicos**, permitindo que uma aula gravada seja convertida em relatórios técnicos para professores e guias de estudo para alunos.

## 1. Configuração do Ambiente (venv)

O projeto utiliza um Ambiente Virtual (venv) para isolar as dependências e garantir a portabilidade do software.

### Passos para instalação no Linux Mint:

1. **Dependências do Sistema Operacional:**
   Abra o terminal e instale o FFmpeg (para processar áudio) e o PortAudio:
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg libportaudio2 python3-venv
   ```
2. **Criação do Ambiente Virtual:** Na pasta raiz do projeto, execute:
  ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Instalação das Bibliotecas Python:** Com o  ```.venv ``` ativo, instale os pacotes necessários:
  ```bash
   pip install --upgrade pip
   pip install sounddevice numpy scipy whisper-openai pydub groq fpdf2 python-dotenv
   ```
## 2. Como Executar:

**Configuração de Credenciais**

Crie um arquivo ```.env``` na raiz do projeto com o seguinte conteúdo:
 ```bash
   GROQ_API_KEY=sua_chave_aqui
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASS=sua_senha_de_app_gmail
   ```
**Iniciando o Processo**
Execute o script principal:
 ```bash
 python main.py
   ```

