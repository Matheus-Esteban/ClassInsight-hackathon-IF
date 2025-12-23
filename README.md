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
### Como Executar:

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

## 2. Fluxo de Operação

O sistema opera através de uma pipeline sequencial desenhada para maximizar a eficiência em hardware com recursos limitados (2GB RAM).

### A. Módulo de Gravação  
* **Captura**: O sistema acessa o hardware de áudio via `sounddevice` com taxa de amostragem de 44.1kHz.
* **Bufferização**: Os dados brutos são armazenados em uma `queue.Queue` (fila) em tempo real, técnica que evita a perda de pacotes de áudio enquanto o processador gerencia outras tarefas.
* **Interrupção**: O encerramento ocorre via **CTRL + C** (sinal SIGINT), disparando o fechamento do fluxo de entrada e a persistência do arquivo `audio_projeto.wav` no disco de forma segura.



###  B. Módulo de Transcrição  
* **Gestão de RAM**: O arquivo de áudio é fatiado em blocos (*chunks*) de 10 minutos para permitir o processamento em hardware.
* **Inferência**: Utiliza o modelo **OpenAI Whisper** local para realizar a conversão de fala em texto de forma precisa.
* **Otimização**: O sistema invoca explicitamente o `gc.collect()` (Garbage Collector) após o processamento de cada bloco para liberar memória RAM e consolidar o texto final em `resultado.md`.

### C. Módulo de Inteligência  
* **Arquitetura Map-Reduce**: O texto transcrito é segmentado para respeitar rigorosamente o limite de **12.000 tokens por minuto (TPM)** da API do Groq.
* **Processamento Llama 3.3**: A inteligência artificial gera, em uma única execução lógica, uma análise pedagógica para o **Professor** e um guia de estudos estruturado para o **Aluno**.
* **Controle de Cota**: Implementa pausas de segurança (*sleep*) entre requisições para operar dentro da folga de **100.000 tokens diários (TPD)** do plano gratuito.


###  D. Módulo de Envio e Limpeza 
* **Geração de PDF**: Os relatórios são renderizados utilizando a biblioteca `FPDF`, aplicando sanitização de caracteres para garantir a integridade do documento final.
* **Protocolo SMTP**: A distribuição dos documentos é realizada via e-mail utilizando o protocolo SMTP com criptografia SSL (porta 465) para garantir a segurança da transmissão.
* **Cleanup Final**: O uso do bloco estrutural `finally` garante que todos os arquivos temporários (`.wav`, `.md`, `.pdf`) sejam apagados automaticamente, assegurando a **idempotência do sistema** e a privacidade total dos dados acadêmicos.

