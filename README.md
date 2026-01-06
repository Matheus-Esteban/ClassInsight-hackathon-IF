# Transcrição e Análise de Aulas - Hackathon IF

Este projeto automatiza o fluxo de captura de áudio, transcrição e geração de inteligência pedagógica. Ele foi desenvolvido com foco em **Eficiência de Processos Acadêmicos**, permitindo que uma aula gravada seja convertida em relatórios técnicos para professores e guias de estudo para alunos.

## 1. Configuração do Ambiente (venv)

O projeto utiliza um Ambiente Virtual (venv) para isolar as dependências e garantir a portabilidade do software.

### Passos para instalação no Linux (Debion):

1. **Dependências do Sistema Operacional:**
   Abra o terminal e instale o FFmpeg (para processar áudio) e o PortAudio:
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg libportaudio2 portaudio19-dev python3-pyaudio python3-venv -y
   
   ```
2. **Criação do Ambiente Virtual:** Na pasta raiz do projeto, execute:
  ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Instalação das Bibliotecas Python:** Com o  ```.venv ``` ativo, instale os pacotes necessários:
  ```bash
   pip install --upgrade pip
   pip install pyaudio speechrecognition sounddevice numpy scipy whisper-openai pydub groq fpdf2 python-dotenvv 
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

O sistema foi arquitetado sob uma **pipeline sequencial e determinística**, otimizada para ambientes com restrições severas de hardware (dispositivos com 2GB de RAM).

### A. Módulo de Captura e Interrupção Multimodal
* **Acesso ao Hardware**: o sistema cria um fluxo de áudio por meio da interface `sounddevice`, funcionando com uma taxa de amostragem que varia de 16 kHz a 44,1 kHz.
* **Concorrência por Multithreading**: Para reduzir o *overhead* do processador, a captura emprega uma **Thread exclusiva** e uma estrutura de dados `queue.Queue`. Isso assegura que a gravação não apresente *jitter* (atraso) durante o monitoramento de comandos de voz pelo sistema.
* **Interrupção Híbrida**:
   * **Comando de Voz**: uma thread secundária usa a biblioteca `SpeechRecognition` para acompanhar a palavra-chave **"PARAR"** em tempo real. Quando o comando é identificado, o sistema indica o término da gravação por meio de um *flag* de sincronização.
   * **Sinal de Hardware**: Como uma medida de redundância, o sistema permite o encerramento por meio do **SIGINT (CTRL+C)**, assegurando que o buffer seja esvaziado (*flushed*) e que o descritor de arquivo `.wav` seja fechado de forma adequada.

### B. Módulo de Transcrição (Processamento de Sinais)
* **Segmentação Dinâmica**: Para funcionar dentro do limite de 2GB de RAM, o sistema utiliza o fatiamento de áudio (*audio chunking*). Isso evita que ocorram erros de *Out of Memory* (OOM) em arquivos extensos.
* **Inferência Local**: Emprega o motor **OpenAI Whisper**, executando a decodificação fonética de forma local para assegurar a privacidade dos dados acadêmicos e diminuir a latência da rede.
* **Gerenciamento de Memória**: Após a transcrição de cada segmento, o sistema chama o `gc.collect()` (Garbage Collector) para obrigar a coleta de lixo e liberar ponteiros de memória.

### C. Módulo de Inteligência (Orquestração de Modelos de Linguagem)

Este módulo atua como o motor analítico do sistema, transformando dados brutos em conhecimento estruturado por meio de uma arquitetura de microsserviços em nuvem.

* **Otimização de Contexto e Payload**: o texto transcrito passa por um processo de filtragem e truncagem inteligente (com limite de 15.000 caracteres), assegurando que esteja em conformidade com a janela de contexto do modelo e prevenindo erros de *413 Payload Too Large*.
* **Gestão de Recursos Críticos (RAM)**: Antes de começar a orquestração da IA, o sistema realiza a liberação explícita do modelo Whisper da memória principal e chama o *Garbage Collector* (`gc.collect()`). Essa técnica é essencial para garantir a estabilidade do sistema em hardware com apenas 2GB de RAM, evitando problemas causados por *Memory Leak*.
* **Engenharia de Prompt Multidirecional**: Emprega o modelo de última geração **Llama 3.3 (70B)** para conduzir uma análise em dois âmbitos pedagógicos diferentes:
   * **Visão do Docente**: Concentrada na análise técnica, pedagógica e nas métricas de engajamento.
   * **Visão do Discente**: Concentrada na síntese de conteúdo e recursos para fixação (aprendizagem ativa).
* **Resiliência e Rate Limiting**: Adota um controle rigoroso de taxa para atender aos limites da API Groq (**12.000 TPM** / **100.000 TPD**). O sistema administra as cotas de requisição por meio de pausas estratégicas, assegurando a continuidade do serviço sem interrupções causadas por bloqueios de segurança do provedor.

### D. Módulo de Distribuição e Persistência Volátil
* **Renderização de Documentos**: Utiliza a biblioteca `FPDF` para conversão de texto estruturado para PDF, aplicando sanitização de caracteres para garantir a integridade do documento final.
* **Segurança na Transmissão**: A distribuição utiliza o protocolo **SMTP sobre TLS/SSL** (Porta 465), garantindo a integridade e confidencialidade dos arquivos durante o tráfego na rede.
* **Idempotência e Cleanup**: Através de blocos estruturais `finally`, o sistema executa a limpeza automática de arquivos temporários (`.wav`, `.md`, `.pdf`), garantindo que o dispositivo retorne ao estado original de armazenamento após cada ciclo (idempotência).
