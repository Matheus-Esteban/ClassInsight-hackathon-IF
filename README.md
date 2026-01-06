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
* **Tokenização e Rate Limiting**: O texto é segmentado para respeitar os limites de **12.000 TPM** (Tokens por Minuto) da API Groq, utilizando algoritmos de truncagem para evitar o estouro de *payload*.
* **Análise Multidirecional**: Através de engenharia de prompt, a IA (Llama 3.3) gera simultaneamente o **Relatório Pedagógico** para o Professor e o **Guia de Estudos** para o Aluno.
* **Resiliência de Cota**: Implementa pausas de segurança (*sleep*) entre requisições para operar dentro do limite gratuito de **100.000 TPD** (Tokens por Dia).

### D. Módulo de Distribuição e Persistência Volátil
* **Renderização de Documentos**: Utiliza a biblioteca `FPDF` para conversão de texto estruturado para PDF, aplicando sanitização de caracteres para garantir a integridade do documento final.
* **Segurança na Transmissão**: A distribuição utiliza o protocolo **SMTP sobre TLS/SSL** (Porta 465), garantindo a integridade e confidencialidade dos arquivos durante o tráfego na rede.
* **Idempotência e Cleanup**: Através de blocos estruturais `finally`, o sistema executa a limpeza automática de arquivos temporários (`.wav`, `.md`, `.pdf`), garantindo que o dispositivo retorne ao estado original de armazenamento após cada ciclo (idempotência).
