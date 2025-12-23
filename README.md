# Sistema de Transcrição e Análise de Aulas - Hackathon IF

Este projeto automatiza o fluxo de captura de áudio, transcrição e geração de inteligência pedagógica. Ele foi desenvolvido com foco em **Eficiência de Processos Acadêmicos**, permitindo que uma aula gravada seja convertida em relatórios técnicos para professores e guias de estudo para alunos.

## 🛠️ 1. Configuração do Ambiente (venv)

O projeto utiliza um Ambiente Virtual (venv) para isolar as dependências e garantir a portabilidade do software.

### Passos para instalação no Linux Mint:

1. **Dependências do Sistema Operacional:**
   Abra o terminal e instale o FFmpeg (para processar áudio) e o PortAudio:
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg libportaudio2 python3-venv
